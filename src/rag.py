"""
End-to-end RAG pipeline: retrieve relevant MD&A chunks, then generate
a grounded answer via the swappable LLMClient.
"""

import logging
from collections.abc import Callable

from config import config
from llm import LLMClient
from post_process import MetricVerifier, verify_answer
from prompts import SYSTEM_PROMPT_RAG
from retrieval import get_client, get_collection, query_multi

logger = logging.getLogger(__name__)


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
        llm = LLMClient()
    answer = llm.generate(prompt, system=SYSTEM_PROMPT_RAG, max_tokens=config.llm_max_tokens, temperature=config.llm_temperature)
    if on_progress:
        on_progress("done", "Done!")

    issues = verify_answer(answer, results)
    if issues["has_issues"]:
        logger.warning("[NumberVerifier] %d issue(s) detected in answer", len(issues["issues"]))
        warning_text = "\n\n\u26a0\ufe0f **Number Verification Note:** The following numbers in the answer may not match the source documents:"
        for issue in issues["issues"]:
            warning_text += f"\n- '{issue['value']}' — {issue.get('context', '')}"
        answer += warning_text

    verifier = MetricVerifier()
    metric_issues = verifier.verify(answer, results)
    if metric_issues:
        logger.warning("[MetricVerifier] %d metric mismatch(es) detected", len(metric_issues))
        warning_text = "\n\n\u26a0\ufe0f **Metric Verification Note:** The following metric names in the answer may not match the source documents:"
        for mi in metric_issues:
            warning_text += f"\n- '{mi['metric']}' (group: {mi['group']})"
        answer += warning_text

    return {
        "question": question,
        "answer": answer,
        "sources": results,
    }


