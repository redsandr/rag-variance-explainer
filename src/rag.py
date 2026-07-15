"""
End-to-end RAG pipeline: retrieve relevant MD&A chunks, then generate
a grounded answer via the swappable LLMClient.
"""

from __future__ import annotations
from collections.abc import Callable
from typing import TYPE_CHECKING

from config import config

if TYPE_CHECKING:
    from llm import LLMClient

SYSTEM_PROMPT = """You are a financial variance analysis assistant. You help \
analysts understand WHY a company's financial metrics changed, using only \
the retrieved filing excerpts provided to you as context.

Rules you must follow:
- Base your answer STRICTLY on the provided context. Do NOT use any outside \
knowledge — including specific dollar amounts, dates, percentages, or details \
that are not present in the context excerpts shown to you. If you know a \
fact from training data, do NOT include it unless the context explicitly \
states it.
- If the context only partially addresses the question, explain what IS \
available and note the gap — do NOT dismiss the entire answer. For example, \
if asked about "revenue variance" but chunks discuss same-restaurant sales, \
extract the revenue-related information and explain the connection.
- Each excerpt is tagged with a relevance score (0.0–1.0). Higher scores \
indicate stronger relevance to the question. Prefer higher-scored \
excerpts for your answer.
- Always cite which filing (ticker, form type, filing date) each piece of \
your answer comes from. Use the exact citation label shown in the context \
block (e.g. [DRI 10-Q filed 2026-03-29 | relevance: 0.87]).
- Pay close attention to metric names. "Revenue" is not the same as \
"comparable store sales" or "same-restaurant sales". Use the exact metric \
name as written in the context. Do not conflate percentage changes from \
different metrics.
- You retrieve and explain. You do NOT make judgment calls about whether a \
variance is acceptable, concerning, or requires escalation — that decision \
belongs to the human analyst. Present the facts and let them decide.

Answer format:
- Use bullet points, organized by fiscal period (chronological order).
- Start each bullet with the source citation in brackets, \
e.g. [DRI 10-Q filed 2026-03-29 | relevance: 0.87].
- Include specific numbers (percentages, dollar amounts) when present in context.
- If the exact metric name is not found but a related metric is discussed, \
explain the closest match and note the difference. \
Only say "the provided filings do not discuss [metric]" if no related \
information exists at all.
"""


def build_context(results: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block for the prompt."""
    if not results:
        return "No relevant filing excerpts were found."

    blocks = []
    for r in results:
        meta = r["metadata"]
        score = r.get("hybrid_score", r.get("relevance", 0))
        label = (
            f"[{meta['ticker']} {meta['form']} filed {meta['filing_date']}"
            f" | relevance: {score:.2f}]"
        )
        blocks.append(f"{label}\n{r['text']}")
    return "\n\n---\n\n".join(blocks)


def answer_question(
    question: str,
    ticker_filter: str = None,
    top_k: int = None,
    min_relevance: float = None,
    llm: LLMClient = None,
    on_progress: Callable | None = None,
) -> dict:
    if top_k is None:
        top_k = config.retrieval_top_k
    if min_relevance is None:
        min_relevance = config.retrieval_min_relevance

    if on_progress:
        on_progress("retrieval", "Retrieving relevant SEC filing chunks...")

    from retrieval import get_client, get_collection, query_multi
    client = get_client()
    collection = get_collection(client)

    results = query_multi(
        collection,
        question,
        top_k=top_k,
        min_relevance=min_relevance,
        ticker_filter=ticker_filter,
    )

    context = build_context(results)
    prompt = (
        f"Context from SEC filings:\n{context}\n\n"
        f"Question: {question}\n\n"
        f"Answer (bullet points, cite each claim, chronological by period):"
    )

    if on_progress:
        on_progress("generate", "Generating answer with LLM (may take several minutes)...")

    if llm is None:
        from llm import LLMClient
        llm = LLMClient()
    answer = llm.generate(prompt, system=SYSTEM_PROMPT, max_tokens=config.llm_max_tokens)

    if on_progress:
        on_progress("done", "Done!")

    return {
        "question": question,
        "answer": answer,
        "sources": results,
    }


if __name__ == "__main__":
    test_questions = [
        ("Why did marketing costs change at Darden?", "DRI"),
        ("Why did Chipotle's labor costs change?", "CMG"),
    ]

    for question, ticker in test_questions:
        print(f"\n{'='*60}")
        print(f"Q: {question}")
        print('='*60)

        result = answer_question(question, ticker_filter=ticker)

        print(f"\nA: {result['answer']}")
        print(f"\n(grounded in {len(result['sources'])} source chunks)")