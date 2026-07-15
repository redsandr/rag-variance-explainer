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
Your job: check whether each factual claim in an answer is supported by the source chunks.

Rules:
- FAITHFUL: The source chunks support the claim. The claim may use different wording or rephrase the source data.
- PARTIALLY FAITHFUL: The source chunks support the general direction but not the specific detail (e.g. wrong number, wrong period).
- UNFAITHFUL: The source chunks contradict the claim or do not contain the information at all.
- Numbers, percentages, and dollar amounts must match to be FAITHFUL. If the source uses a different number, it is PARTIALLY FAITHFUL or UNFAITHFUL.
- If a claim cites a specific filing label, verify the information is actually in that filing's chunk.

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
    score = parsed.get("faithfulness_score", 0)
    if score > 1:
        score = score / 100
    pct = round(score * 100)
    f = parsed.get("faithful_count", 0)
    p = parsed.get("partial_count", 0)
    u = parsed.get("unfaithful_count", 0)
    return f"{pct}% ({f}F/{p}P/{u}U)"


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

    llm = LLMClient()
    results = []
    times = []

    for i, item in enumerate(eval_set, 1):
        qid = item["id"]
        question = item["question"]
        ticker = item.get("ticker_filter")

        elapsed_prompt = f" [~{fmt_time(sum(times)/len(times) * (len(eval_set)-i+1))} remaining]" if times else ""
        logger.info("[%s/%s] [%s] %s...%s", i, len(eval_set), qid, question[:50], elapsed_prompt)

        t0 = time.time()

        try:
            rag_result = answer_question(question, ticker_filter=ticker, top_k=5, llm=llm)
        except Exception as e:
            logger.error("  -> RAG FAILED: %s", e)
            results.append({"id": qid, "question": question, "error": str(e)})
            continue
        answer = rag_result["answer"]
        sources = rag_result["sources"]

        prompt = build_judge_prompt(question, answer, sources)
        response = llm.generate(prompt, system=JUDGE_SYSTEM_PROMPT, max_tokens=2048)
        parsed = parse_judge_response(response)
        total_time = round(time.time() - t0, 1)
        times.append(total_time)

        if parsed:
            logger.info("  -> %s [%s]", display_score(parsed), fmt_time(total_time))
            results.append({"id": qid, "question": question, **parsed})
        else:
            logger.warning("  -> PARSE FAILED [%s]", fmt_time(total_time))
            results.append({"id": qid, "question": question, "error": response})

    total_f = sum(r.get("faithful_count", 0) for r in results if "error" not in r)
    total_p = sum(r.get("partial_count", 0) for r in results if "error" not in r)
    total_u = sum(r.get("unfaithful_count", 0) for r in results if "error" not in r)
    total = total_f + total_p + total_u
    overall = total_f / total if total > 0 else 0
    if total > 0 and overall != (total_f + 0.5 * total_p) / total:
        logger.info("Weighted faithfulness: %.1f%% (partial weighted 0.5)", (total_f + 0.5 * total_p) / total * 100)
    ok = sum(1 for r in results if "error" not in r)

    summary = (
        f"\n{'='*60}\n"
        f"OVERALL FAITHFULNESS: {overall:.1%} ({total_f}F / {total_p}P / {total_u}U)\n"
        f"Evaluated: {ok}/{len(results)} questions, {total} total claims\n"
        f"Total time: {fmt_time(sum(times))}\n"
        f"{'='*60}"
    )
    logger.info(summary)

    with open(RESULT_FILE, "w") as f:
        json.dump({
            "overall_faithfulness": round(overall, 4),
            "total_claims": total,
            "faithful": total_f,
            "partial": total_p,
            "unfaithful": total_u,
            "results": results,
        }, f, indent=2)

    logger.info("Saved to %s", RESULT_FILE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
