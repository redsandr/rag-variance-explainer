"""
Pydantic schemas for structured RAG output + validation.
Phase 2: claim decomposition + NLI verification.
"""

import copy
import json
import logging
from collections.abc import Sequence

from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class VerifiedClaim(BaseModel):
    statement: str = Field(description="One atomic claim from the answer")
    source_chunk_index: int = Field(ge=0, description="Index into the retrieved chunks list")
    source_quote: str = Field(description="Verbatim quote from the source chunk supporting this claim")


class StructuredAnswer(BaseModel):
    answer: str = Field(description="Direct answer to the question in 1-3 sentences")
    claims: list[VerifiedClaim] = Field(description="Atomic claims that comprise the answer")
    can_answer: bool = Field(description="True if context contains enough info to answer")
    confidence: float = Field(ge=0.0, le=1.0, description="How fully context supports the answer")


def get_structured_schema() -> dict:
    """Return JSON schema with $ref/$defs resolved inline for llama.cpp compat."""
    schema = StructuredAnswer.model_json_schema()
    return _resolve_refs(schema)


def _resolve_refs(schema: dict, defs: dict | None = None) -> dict:
    """Recursively expand $ref/$defs inline to avoid llama.cpp grammar bug (#21228)."""
    if defs is None:
        defs = schema.get("$defs", schema.get("definitions", {}))
    if isinstance(schema, dict):
        if "$ref" in schema:
            parts = schema["$ref"].strip("#/").split("/")
            resolved = defs
            for p in parts[1:]:
                resolved = resolved.get(p, {})
            merged = {k: v for k, v in schema.items() if k != "$ref"}
            merged.update(copy.deepcopy(resolved))
            return _resolve_refs(merged, defs)
        result = {}
        for k, v in schema.items():
            if k in ("$defs", "definitions"):
                continue
            result[k] = _resolve_refs(v, defs)
        return result
    if isinstance(schema, list):
        return [_resolve_refs(item, defs) for item in schema]
    return schema


STRUCTURED_FORMAT_INSTRUCTION = (
    "You MUST return ONLY valid JSON matching the schema below. "
    "No markdown fences. No explanation. No extra text before or after. "
    "The JSON must be parseable by json.loads() directly."
)


def build_format_prompt(schema: dict | None = None) -> str:
    if schema is None:
        schema = get_structured_schema()
    schema_str = json.dumps(schema, indent=2)
    return f"\n\n{STRUCTURED_FORMAT_INSTRUCTION}\n\nJSON Schema:\n{schema_str}\n"


def parse_answer(raw: str) -> StructuredAnswer | None:
    """Try to parse LLM output into StructuredAnswer. Returns None on failure."""
    if not raw or not raw.strip():
        return None
    cleaned = raw.strip()
    if cleaned.startswith("```"):
        for fence in ("```json\n", "```\n", "```json", "```"):
            if cleaned.startswith(fence):
                cleaned = cleaned[len(fence):]
                break
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
    try:
        return StructuredAnswer.model_validate_json(cleaned)
    except Exception as e:
        logger.warning("StructuredAnswer parse failed: %s — %s", type(e).__name__, cleaned[:200])
        return None


def validate_answer(answer: StructuredAnswer, chunks: Sequence[dict]) -> list[str]:
    """Check every source_quote exists verbatim in its referenced chunk.

    Returns a list of error messages (empty = all valid).
    """
    errors: list[str] = []
    for i, claim in enumerate(answer.claims):
        idx = claim.source_chunk_index
        if idx < 0 or idx >= len(chunks):
            errors.append(f"Claim {i}: source_chunk_index {idx} out of range (0-{len(chunks)-1})")
            continue
        chunk_text = chunks[idx].get("text", "")
        if claim.source_quote not in chunk_text:
            errors.append(f"Claim {i}: quote not found verbatim in chunk {idx}")
    return errors


def fallback_answer(raw: str, question: str, chunks: Sequence[dict]) -> dict:
    """Build a safe fallback dict when structured parsing fails.

    Tries partial recovery first, then raw text, then graceful refusal.
    """
    answer_text = raw.strip() if raw and raw.strip() else None
    try:
        data = json.loads(answer_text or "{}")
        if isinstance(data, dict) and data.get("answer"):
            return {
                "question": question,
                "answer": str(data["answer"]),
                "sources": chunks,
                "verification_errors": [],
                "structured_fallback": True,
                "structured_failure_reason": "schema_mismatch",
            }
    except Exception:
        pass

    if answer_text:
        return {
            "question": question,
            "answer": answer_text,
            "sources": chunks,
            "verification_errors": [],
            "structured_fallback": True,
            "structured_failure_reason": "parse_error",
        }

    return {
        "question": question,
        "answer": "I cannot answer this question based on the available SEC filing excerpts.",
        "sources": chunks,
        "verification_errors": [],
        "structured_fallback": True,
        "structured_failure_reason": "empty_response",
    }


# ── Phase 2: Claim Decomposition ──────────────────────────────────────────

DECOMPOSITION_SYSTEM_PROMPT = """You are a claim decomposition assistant. Break financial answer text into atomic, single-fact claims.

Rules:
- Each claim must contain exactly ONE verifiable fact
- Resolve pronouns to the actual metric name (e.g., "it" -> "revenue")
- Keep numbers, percentages, dates exact — do NOT round or paraphrase
- Preserve period context (e.g., "in Q3 2024")
- Return ONLY valid JSON: {"claims": ["...", "..."]}

Examples:
Input: "Revenue increased 7.4% to $3.1 billion driven by menu price increases."
Output: {"claims": ["Revenue increased 7.4%.", "Revenue was $3.1 billion.", "Revenue growth was driven by menu price increases."]}

Input: "Comparable sales decreased 2.1% in Q3 2024."
Output: {"claims": ["Comparable sales decreased 2.1% in Q3 2024."]}"""


def decompose_claims(answer_text: str, llm) -> list[str]:
    """Decompose an answer into atomic, single-fact claims using the LLM."""
    if not answer_text or not answer_text.strip():
        return []
    try:
        result = llm.generate(
            answer_text,
            system=DECOMPOSITION_SYSTEM_PROMPT,
            max_tokens=500,
            temperature=0.0,
        )
        cleaned = result.strip()
        if cleaned.startswith("```"):
            for fence in ("```json\n", "```\n", "```json", "```"):
                if cleaned.startswith(fence):
                    cleaned = cleaned[len(fence):]
                    break
            if cleaned.endswith("```"):
                cleaned = cleaned[:-3]
        data = json.loads(cleaned)
        claims = data.get("claims", [])
        if isinstance(claims, list) and all(isinstance(c, str) for c in claims):
            return claims
        return []
    except Exception:
        logger.exception("Claim decomposition failed")
        return []


def verify_claims_nli(
    claims: list[str],
    chunks: Sequence[dict],
    nli_client,
    threshold: float = 0.72,
) -> list[dict]:
    """Verify each atomic claim against top-N source chunks via NLI."""
    if not claims or not chunks:
        return []
    chunk_texts = [c.get("text", "") for c in chunks[:3]]
    return nli_client.verify_batch(claims, chunk_texts, threshold)


def aggregate_verdicts(verdicts: list[dict]) -> dict:
    """Aggregate per-claim NLI verdicts into overall assessment.

    Returns dict with total/supported/unsupported counts and pass/fail.
    """
    if not verdicts:
        return {"total": 0, "supported": 0, "unsupported": 0, "unsupported_ratio": 0.0, "overall": "pass"}
    total = len(verdicts)
    supported = sum(1 for v in verdicts if v.get("supported"))
    unsupported = total - supported
    ratio = unsupported / total if total > 0 else 0.0
    return {
        "total": total,
        "supported": supported,
        "unsupported": unsupported,
        "unsupported_ratio": ratio,
        "overall": "fail" if ratio > 0.5 else "pass",
    }
