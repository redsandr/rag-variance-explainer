"""
End-to-end RAG pipeline: retrieve relevant MD&A chunks, then generate
a grounded answer via the swappable LLMClient.
"""

import logging
import os
import re
from collections.abc import Callable
from typing import Any

from config import config
from llm import LLMClient
from logging_config import log_timer
from post_process import verify_answer_llm
from prompts import build_rag_system_prompt
from retrieval import _company_period_plan, get_client, get_collection, query_multi
from verifier import (
    aggregate_verdicts,
    fallback_answer,
    get_structured_schema,
    parse_answer,
    validate_answer,
    verify_claims_nli,
)

logger = logging.getLogger(__name__)


MAX_QUESTION_LENGTH = 1024


def sanitize_input(raw: str) -> str:
    """Strip control characters and truncate to safe length."""
    cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', raw)
    return cleaned[:MAX_QUESTION_LENGTH]


def build_context(results: list[dict]) -> str:
    """Format retrieved chunks into a labeled context block for the prompt."""
    if not results:
        return "No relevant filing excerpts were found."

    blocks = []
    for index, r in enumerate(results):
        meta = r["metadata"]
        score = r.get("hybrid_score", r.get("relevance", 0))
        label = (
            f"[Source {index} | {meta['ticker']} {meta['form']} filed {meta['filing_date']}"
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
    nli_client: Any | None = None,
    retrieval_client: Any | None = None,
    on_progress: Callable[[str, str], None] | None = None,
    cross_encoder_enabled: bool | None = None,
) -> dict:
    """End-to-end RAG pipeline: retrieve, generate.

    Pulls relevant MD&A chunks from ChromaDB, builds a grounded prompt,
    calls the LLM (with built-in self-verify rules), and returns the answer.
    Returns structured dict with 'question', 'answer', and 'sources'.

    Args:
        question: User question
        ticker_filter: Optional ticker to filter results
        top_k: Number of chunks to retrieve
        min_relevance: Minimum relevance threshold
        llm: Optional LLMClient instance (for testing)
        nli_client: Optional NLIClient instance (for testing)
        retrieval_client: Optional ChromaDB client (for testing)
        on_progress: Optional callback for progress updates
    """

    if top_k is None:
        top_k = config.retrieval_top_k
    if min_relevance is None:
        min_relevance = config.retrieval_min_relevance

    if on_progress:
        on_progress("retrieval", "Retrieving relevant SEC filing chunks...")

    if retrieval_client is None:
        client = get_client()
        collection = get_collection(client)
    else:
        collection = retrieval_client

    with log_timer(logger, "rag.retrieval"):
        results = query_multi(
            collection,
            question,
            top_k=top_k,
            min_relevance=min_relevance,
            ticker_filter=ticker_filter,
            cross_encoder_enabled=cross_encoder_enabled,
        )

    if os.getenv("RAG_DIAGNOSTICS", "").lower() == "true":
        logger.warning("[RAG-DIAG] retrieved=%d ticker_filter=%s", len(results), ticker_filter)
        for index, result in enumerate(results):
            meta = result.get("metadata", {})
            logger.warning(
                "[RAG-DIAG] source=%d ticker=%s form=%s filed=%s accession=%s chunk=%s "
                "relevance=%s hybrid_score=%s chars=%d",
                index, meta.get("ticker"), meta.get("form"), meta.get("filing_date"),
                meta.get("accession_number"), meta.get("chunk_index"),
                result.get("relevance"), result.get("hybrid_score"), len(result.get("text", "")),
            )

    if not results:
        if on_progress:
            on_progress("done", "No relevant filing excerpts found.")
        return {
            "question": question,
            "answer": "I cannot answer this question based on the available SEC filing excerpts.",
            "sources": [],
            "verification_errors": [],
            "structured": True,
            "claims": [],
            "confidence": 0.0,
            "nli_verdicts": None,
            "nli_summary": None,
        }

    context = build_context(results)
    answer_instruction = (
        "Answer as structured claims; source_chunk_index is the zero-based Source number above:"
        if config.structured_output_enabled
        else "Answer (bullet points, cite each claim, chronological by period):"
    )
    prompt = (
        f"Context from SEC filings:\n{context}\n\n"
        f"=== USER QUESTION ===\n{question}\n=== END ===\n\n"
        f"{answer_instruction}"
    )

    if on_progress:
        on_progress("generate", "Generating answer with LLM (may take several minutes)...")

    if llm is None:
        llm = LLMClient()

    system_prompt = build_rag_system_prompt(structured=config.structured_output_enabled)

    structured_fallback = False
    structured_failure_reason: str | None = None

    nli_verdicts: list[dict] | None = None
    nli_summary: dict | None = None

    if config.structured_output_enabled:
        schema = get_structured_schema()
        response_format = {"type": "json_object", "schema": schema}
        with log_timer(logger, "rag.generate"):
            answer = llm.generate(
                prompt,
                system=system_prompt,
                max_tokens=config.llm_max_tokens,
                temperature=config.llm_temperature,
                response_format=response_format,
            )

        parsed = parse_answer(answer)
        if parsed is not None and parsed.can_answer:
            quote_errors = validate_answer(parsed, results)
            plan = _company_period_plan(question) if ticker_filter is None else None
            if plan and not quote_errors:
                cited_scopes = {
                    (results[claim.source_chunk_index]["metadata"].get("ticker"),
                     results[claim.source_chunk_index]["metadata"].get("report_period_end"))
                    for claim in parsed.claims
                    if 0 <= claim.source_chunk_index < len(results)
                }
                if any(not any(cited_ticker == ticker and (period is None or cited_period == period)
                               for cited_ticker, cited_period in cited_scopes)
                       for ticker, period in plan):
                    quote_errors.append("No source-backed claim for each requested company and period")
            if quote_errors:
                logger.warning("[StructuredOutput] quote validation (%d errors): %s", len(quote_errors), quote_errors)
                failure_answer = (
                    "I cannot verify a sourced finding for each requested company and period."
                    if any("each requested company" in error for error in quote_errors)
                    else "I cannot verify the generated claims against the retrieved SEC filing excerpts, "
                         "so I will not present them as sourced findings."
                )
                return {
                    "question": question,
                    "answer": failure_answer,
                    "sources": results,
                    "verification_errors": quote_errors,
                    "structured": True,
                    "claims": [],
                    "confidence": 0.0,
                    "nli_verdicts": None,
                    "nli_summary": None,
                }

            if config.nli_enabled:
                try:
                    sub_claims = [c.statement for c in parsed.claims]
                    if sub_claims:
                        if nli_client is None:
                            from nli import NLIClient
                            nli_client = NLIClient(
                                model_name=config.nli_model,
                                device=config.nli_device,
                                threshold=config.nli_threshold,
                            )
                        nli_verdicts = [
                            verdict
                            for claim in parsed.claims
                            for verdict in verify_claims_nli(
                                [claim.statement], [results[claim.source_chunk_index]],
                                nli_client, config.nli_threshold,
                            )
                        ]
                        nli_summary = aggregate_verdicts(nli_verdicts)
                        if os.getenv("RAG_DIAGNOSTICS", "").lower() == "true":
                            for index, verdict in enumerate(nli_verdicts):
                                logger.warning(
                                    "[RAG-DIAG] nli_claim=%d verdict=%s confidence=%.4f "
                                    "max_entailment=%.4f supported=%s claim=%r",
                                    index, verdict.get("verdict"), verdict.get("confidence", 0.0),
                                    verdict.get("max_entailment", 0.0), verdict.get("supported"),
                                    verdict.get("claim"),
                                )
                        if nli_summary["overall"] == "fail":
                            logger.warning(
                                "[NLI] %d/%d claims unsupported — answer may contain unsupported facts",
                                nli_summary["unsupported"],
                                nli_summary["total"],
                            )
                except Exception:
                    logger.exception("[NLI] verification skipped")
                    nli_verdicts = None
                    nli_summary = None

            return {
                "question": question,
                "answer": parsed.answer,
                "sources": results,
                "verification_errors": quote_errors,
                "structured": True,
                "claims": [c.model_dump() for c in parsed.claims],
                "confidence": parsed.confidence,
                "nli_verdicts": nli_verdicts,
                "nli_summary": nli_summary,
            }

        fallback_result = fallback_answer(answer, question, results)
        structured_fallback = True
        structured_failure_reason = fallback_result.get("structured_failure_reason", "unknown")
        answer = fallback_result["answer"]

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
        "structured_fallback": structured_fallback,
        "structured_failure_reason": structured_failure_reason,
        "nli_verdicts": nli_verdicts,
        "nli_summary": nli_summary,
    }


