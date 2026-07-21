"""
End-to-end RAG pipeline: retrieve relevant MD&A chunks, then generate
a grounded answer via the swappable LLMClient.
"""

import logging
import re
from collections.abc import Callable

from config import config
from llm import LLMClient
from logging_config import log_timer
from post_process import verify_answer_llm
from prompts import SYSTEM_PROMPT_RAG
from retrieval import get_client, get_collection, query_multi

logger = logging.getLogger(__name__)


MAX_QUESTION_LENGTH = 256


def sanitize_input(raw: str) -> str:
    """Strip control characters and truncate to safe length."""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    return cleaned[:MAX_QUESTION_LENGTH]


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
    ticker_filter: str | None = None,
    top_k: int | None = None,
    min_relevance: float | None = None,
    llm: LLMClient | None = None,
    on_progress: Callable[[str, str], None] | None = None,
) -> dict:
    """End-to-end RAG pipeline: retrieve, generate.

    Pulls relevant MD&A chunks from ChromaDB, builds a grounded prompt,
    calls the LLM (with built-in self-verify rules), and returns the answer.
    Returns structured dict with 'question', 'answer', and 'sources'.
    """

    if top_k is None:
        top_k = config.retrieval_top_k
    if min_relevance is None:
        min_relevance = config.retrieval_min_relevance

    if on_progress:
        on_progress("retrieval", "Retrieving relevant SEC filing chunks...")

    client = get_client()
    collection = get_collection(client)

    with log_timer(logger, "rag.retrieval"):
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
        f"=== USER QUESTION ===\n{question}\n=== END ===\n\n"
        f"Answer (bullet points, cite each claim, chronological by period):"
    )

    if on_progress:
        on_progress("generate", "Generating answer with LLM (may take several minutes)...")

    if llm is None:
        llm = LLMClient()
    with log_timer(logger, "rag.generate"):
        answer = llm.generate(prompt, system=SYSTEM_PROMPT_RAG, max_tokens=config.llm_max_tokens, temperature=config.llm_temperature)
    verification_errors = []
    try:
        issues = verify_answer_llm(answer, results, llm)
        if issues.get("has_errors") and issues.get("errors"):
            logger.warning("[LLMVerifier] %d issue(s) detected in answer", len(issues["errors"]))
            verification_errors = issues["errors"]
    except Exception as e:
        logger.warning("LLM verification skipped — %s: %s", type(e).__name__, e)

    if on_progress:
        on_progress("done", "Done!")

    return {
        "question": question,
        "answer": answer,
        "sources": results,
        "verification_errors": verification_errors,
    }


