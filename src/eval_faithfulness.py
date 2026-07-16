"""
LLM-as-judge faithfulness evaluation.

Does BOTH RAG generation AND judging in one pass, using the SAME source
chunks. This ensures the judge evaluates against exactly what the LLM saw.

Usage:
    python src/eval_faithfulness.py
    python src/eval_faithfulness.py --sample 3
    python src/eval_faithfulness.py --ids eval-001 eval-007
"""

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

logger = logging.getLogger(__name__)

from llm import LLMClient
from rag import answer_question

EVAL_FILE = Path(__file__).parent.parent / "data" / "eval_questions.json"
RESULT_FILE = Path(__file__).parent.parent / "data" / "faithfulness_results.json"

JUDGE_SYSTEM_PROMPT = """You are a strict but fair faithfulness evaluator for financial RAG systems.
Your job: extract each factual claim from the Answer text ONLY, then check if that claim is supported by the Source chunks.

CRITICAL: Extract claims ONLY from the Answer. Do NOT extract claims from the Source chunks. If the Answer says "comparable sales increased 7.4%", your claim is "comparable sales increased 7.4%" — not "revenue increased 6.4%" just because that number appears in the sources.

Rules:
- FAITHFUL: The source chunks support the claim verbatim or with minor rephrasing. Numbers, percentages, and dollar amounts must match exactly.
- PARTIALLY FAITHFUL: The source chunks support the general direction but the specific detail is wrong (e.g. wrong number, wrong period).
- UNFAITHFUL: The source chunks contradict the claim or do not contain the information at all.
- If a claim cites a specific filing label, verify the information is actually in that filing's chunk.
- Evaluate each claim independently against ALL source chunks. A claim about one period is FAITHFUL if its exact numbers match the source for that period — even if a different claim references a different period with different numbers. Do NOT penalize a claim just because other claims in the answer discuss different periods.

Examples:
  Answer: "Revenue increased 7.4%." Source: "Comparable sales increased 7.4%."
  → Claim: "Revenue increased 7.4%." Verdict: UNFAITHFUL (source says comparable sales, not revenue)

  Answer: "Comparable sales increased 7.4%." Source: "Comparable sales increased 7.4%."
  → Claim: "Comparable sales increased 7.4%." Verdict: FAITHFUL (verbatim match)

  Answer: "Labor costs decreased 0.2%." Source: "Labor costs decreased 0.2%."
  → Claim: "Labor costs decreased 0.2%." Verdict: FAITHFUL (rephrasing OK, number matches)

  Answer: "Comparable sales decreased 0.4% for Mar 31, 2025." Source: "Comparable restaurant sales decreased 0.4% for the three months ended March 31, 2025."
  → Claim: "Comparable sales decreased 0.4% for Mar 31, 2025." Verdict: FAITHFUL (number 0.4% matches exactly, period matches, minor abbreviation OK)

  Answer: "As of Jan 30, 2026, we operated 656 stores." Source: "As of January 30, 2026, we operated 656 Cracker Barrel stores in 43 states."
  → Claim: "As of Jan 30, 2026, we operated 656 stores." Verdict: FAITHFUL (number 656 matches, date matches, minor wording difference OK)

  Answer: "Revenue increased 6.4% to $3.1 billion." Source: "Revenue was $3.0 billion, up 7.5%."
  → Claim: "Revenue increased 6.4% to $3.1 billion." Verdict: UNFAITHFUL (source says 7.5% and $3.0B, not 6.4% and $3.1B)

Return ONLY valid JSON with these exact keys:
claims (list of {claim, verdict}), faithful_count, partial_count, unfaithful_count, total_claims, faithfulness_score (0.0 to 1.0)"""


def build_judge_prompt(question: str, answer: str, sources: list[dict]) -> str:
    context_blocks = []
    for s in sources:
        meta = s.get("metadata", {})
        label = (
            f"[{meta.get('ticker', '?')} {meta.get('form', '?')} "
            f"filed {meta.get('filing_date', '?')} | relevance: {s.get('hybrid_score', s.get('relevance', 0)):.2f}]"
        )
        text = s.get("text", "")
        if len(text) > 2000:
            text = text[:2000] + "..."
        context_blocks.append(f"{label}\n{text}")

    return f"""Question: {question}

Source chunks:
{chr(10)+chr(10).join(context_blocks) if context_blocks else "(no sources available)"}

---

Answer to evaluate:
{answer}

---

Evaluate each factual claim in the answer against the source chunks.
Return JSON only."""


def parse_judge_response(response: str) -> dict | None:
    cleaned = response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    if cleaned.endswith("},"):
        cleaned = cleaned[:-1]
    for _ in range(3):
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            last_brace = cleaned.rfind("}")
            penultimate_brace = cleaned.rfind("}", 0, last_brace) if last_brace > 0 else -1
            if penultimate_brace != -1:
                cleaned = cleaned[:penultimate_brace + 1]
                continue
            break
    return None


def display_score(parsed: dict) -> str:
    f = parsed.get("faithful_count", 0)
    p = parsed.get("partial_count", 0)
    u = parsed.get("unfaithful_count", 0)
    total = f + p + u
    strict = round(f / total * 100) if total > 0 else 0
    weighted = round((f + 0.5 * p) / total * 100) if total > 0 else 0
    return f"{strict}% strict / {weighted}% weighted ({f}F/{p}P/{u}U)"


def _save_checkpoint(results: list) -> None:
    with open(RESULT_FILE, "w") as f:
        json.dump({"results": results}, f, indent=2)


def fmt_time(seconds: float) -> str:
    if seconds < 60:
        return f"{seconds:.0f}s"
    return f"{seconds/60:.0f}m {seconds%60:.0f}s"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=None, help="Run first N questions")
    parser.add_argument("--ids", nargs="*", default=None, help="Specific eval IDs to run")
    args = parser.parse_args()

    if not EVAL_FILE.exists():
        print(f"ERROR: {EVAL_FILE} not found.")
        sys.exit(1)

    with open(EVAL_FILE) as f:
        eval_set = json.load(f)

    if args.ids and args.sample:
        print("Warning: both --ids and --sample provided. Using --ids, ignoring --sample.")
    if args.ids:
        eval_set = [q for q in eval_set if q["id"] in args.ids]
    elif args.sample:
        eval_set = eval_set[:args.sample]

    if not eval_set:
        print("No matching questions found.")
        sys.exit(1)

    logger.info("Running RAG + faithfulness eval for %s questions...", len(eval_set))
    logger.info("(each question = 2 LLM calls: 1 generate + 1 judge)\n")

    results = []
    times = []

    for i, item in enumerate(eval_set, 1):
        qid = item["id"]
        question = item["question"]
        ticker = item.get("ticker_filter")

        elapsed_prompt = f" [~{fmt_time(sum(times)/len(times) * (len(eval_set)-i+1))} remaining]" if times else ""
        logger.info("[%s/%s] [%s] %s...%s", i, len(eval_set), qid, question[:50], elapsed_prompt)

        LLMClient.reset()
        llm = LLMClient()
        t0 = time.time()

        try:
            rag_result = answer_question(question, ticker_filter=ticker, top_k=5, llm=llm)
        except Exception as e:
            logger.error("  -> RAG FAILED: %s", e)
            results.append({"id": qid, "question": question, "error": str(e)})
            continue
        answer = rag_result["answer"]
        sources = rag_result["sources"]

        NO_INFO_PATTERNS = [
            "do not discuss", "not mentioned", "no information",
            "does not provide", "not addressed", "not covered",
            "do not provide", "the provided filings do not",
        ]
        has_content = not any(p in answer.lower() for p in NO_INFO_PATTERNS)

        if not has_content:
            total_time = round(time.time() - t0, 1)
            times.append(total_time)
            logger.info("  -> RETRIEVAL GAP — answer has no info [%s]", fmt_time(total_time))
            results.append({
                "id": qid, "question": question,
                "retrieval_gap": True,
                "answer": answer,
                "sources": [
                    {"ticker": s["metadata"]["ticker"], "form": s["metadata"]["form"],
                     "filing_date": s["metadata"]["filing_date"],
                     "relevance": s.get("hybrid_score", s.get("relevance", 0)),
                     "text": s["text"]}
                    for s in sources
                ],
            })
            _save_checkpoint(results)
            continue

        prompt = build_judge_prompt(question, answer, sources)
        response = llm.generate(prompt, system=JUDGE_SYSTEM_PROMPT, max_tokens=4096)
        parsed = parse_judge_response(response)
        total_time = round(time.time() - t0, 1)
        times.append(total_time)

        if parsed and isinstance(parsed, dict):
            claims = parsed.get("claims", [])
            faithful = sum(1 for c in claims if c.get("verdict") == "FAITHFUL")
            partial = sum(1 for c in claims if c.get("verdict") == "PARTIALLY FAITHFUL")
            unfaithful = sum(1 for c in claims if c.get("verdict") == "UNFAITHFUL")
            parsed["total_claims"] = len(claims)
            parsed["faithful_count"] = faithful
            parsed["partial_count"] = partial
            parsed["unfaithful_count"] = unfaithful
            total = faithful + partial + unfaithful
            parsed["faithfulness_score"] = round(faithful / total, 4) if total > 0 else 0.0
            logger.info("  -> %s [%s]", display_score(parsed), fmt_time(total_time))
            results.append({
                "id": qid,
                "question": question,
                "answer": answer,
                "sources": [
                    {"ticker": s["metadata"]["ticker"], "form": s["metadata"]["form"],
                     "filing_date": s["metadata"]["filing_date"],
                     "relevance": s.get("hybrid_score", s.get("relevance", 0)),
                     "text": s["text"]}
                    for s in sources
                ],
                **parsed,
            })
        else:
            logger.warning("  -> PARSE FAILED [%s]", fmt_time(total_time))
            results.append({"id": qid, "question": question, "error": response})
        _save_checkpoint(results)

    total_f = sum(r.get("faithful_count", 0) for r in results if "error" not in r and not r.get("retrieval_gap"))
    total_p = sum(r.get("partial_count", 0) for r in results if "error" not in r and not r.get("retrieval_gap"))
    total_u = sum(r.get("unfaithful_count", 0) for r in results if "error" not in r and not r.get("retrieval_gap"))
    total = total_f + total_p + total_u
    gaps = sum(1 for r in results if r.get("retrieval_gap"))
    ok = sum(1 for r in results if "error" not in r and not r.get("retrieval_gap"))
    overall = total_f / total if total > 0 else 0
    weighted = (total_f + 0.5 * total_p) / total if total > 0 else 0

    summary = (
        f"\n{'='*60}\n"
        f"OVERALL FAITHFULNESS (strict): {overall:.1%} ({total_f}F / {total_p}P / {total_u}U)\n"
        f"OVERALL FAITHFULNESS (weighted): {weighted:.1%}  (partial weighted 0.5)\n"
        f"Evaluated: {ok} judged + {gaps} retrieval gaps / {len(results)} questions, {total} total claims\n"
        f"Total time: {fmt_time(sum(times))}\n"
        f"{'='*60}"
    )
    logger.info(summary)

    with open(RESULT_FILE, "w") as f:
        json.dump({
            "overall_faithfulness_strict": round(overall, 4),
            "overall_faithfulness_weighted": round(weighted, 4),
            "total_claims": total,
            "faithful": total_f,
            "partial": total_p,
            "unfaithful": total_u,
            "retrieval_gaps": gaps,
            "results": results,
        }, f, indent=2)

    logger.info("Saved to %s", RESULT_FILE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
