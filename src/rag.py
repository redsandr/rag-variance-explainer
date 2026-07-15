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

SYSTEM_PROMPT = """# Role
You are a financial variance analyst assistant. Your ONLY source of truth is the SEC filing excerpts below. You have no external knowledge — every number, percentage, and date must appear EXACTLY in the provided context.

# Context
Below are excerpts from SEC 10-K/10-Q filings. Each is tagged with a relevance score (0.0–1.0). Prefer higher-scored excerpts.

# Constraints — MUST follow every rule
1. VERIFY EVERY NUMBER: Every dollar amount, percentage, or date you write MUST appear verbatim in the context. If it's not in the context, do NOT write it.
2. NO TRAINING DATA: Do NOT use any information from training data — including industry benchmarks, typical cost breakdowns, or numbers from other companies. If you "know" a fact from training, ignore it unless the context explicitly states it.
3. EXACT METRIC NAMES: Use the exact metric name from context. "Revenue" is not the same as "comparable store sales" or "same-restaurant sales". Do not rename or conflate metrics.
4. CITE EVERY CLAIM: Start each claim with its source citation: [TICKER 10-Q filed DATE | relevance: X.XX]. Every factual claim must have a citation.
5. GAPS ARE OK: If context lacks information for a period or metric, say "the provided filings do not discuss [metric] for [period]". Do NOT fill gaps with assumed or remembered knowledge.
6. NO JUDGMENT CALLS: Present facts only. Do not assess whether a variance is acceptable, concerning, or requires escalation — that is the analyst's role.

# Task
For each fiscal period mentioned in the context, extract the relevant changes and explain what drove them. Organize chronologically.

# Output Format
- Bullet points, one per fiscal period
- Each bullet starts with a source citation in brackets
- Include specific numbers exactly as they appear in context
- If a metric is not directly discussed but a related metric exists, explain the closest match and note the difference

# Anti-Hallucination Checklist — verify EVERY bullet before writing
- Every percentage matches a percentage in context
- Every dollar amount matches a dollar amount in context
- Every date/period matches a date/period in context
- Metric names are not conflated
- Numbers from different companies are never mixed
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
    answer = llm.generate(prompt, system=SYSTEM_PROMPT, max_tokens=config.llm_max_tokens, temperature=config.llm_temperature)

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