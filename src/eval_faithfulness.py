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

logger = logging.getLogger(__name__)

from llm import LLMClient
from prompts import JUDGE_SYSTEM_PROMPT_FULL, build_judge_prompt
from rag import answer_question

EVAL_FILE = Path(__file__).parent.parent / "data" / "eval_questions.json"
RESULT_FILE = Path(__file__).parent.parent / "data" / "faithfulness_results.json"


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


def _load_eval_set(args) -> list[dict]:
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

    return eval_set


NO_INFO_PATTERNS = [
    "do not discuss", "not mentioned", "no information",
    "does not provide", "not addressed", "not covered",
    "do not provide", "the provided filings do not",
]


def _has_answer_content(answer: str) -> bool:
    return not any(p in answer.lower() for p in NO_INFO_PATTERNS)


def _summarize_sources(sources: list[dict]) -> list[dict]:
    return [
        {
            "ticker": s["metadata"]["ticker"],
            "form": s["metadata"]["form"],
            "filing_date": s["metadata"]["filing_date"],
            "relevance": s.get("hybrid_score", s.get("relevance", 0)),
            "text": s["text"],
        }
        for s in sources
    ]


def _process_question(item: dict, llm: LLMClient, times: list[float], i: int, n: int) -> dict | None:
    qid = item["id"]
    question = item["question"]
    ticker = item.get("ticker_filter")

    elapsed_prompt = f" [~{fmt_time(sum(times)/len(times) * (n-i+1))} remaining]" if times else ""
    logger.info("[%s/%s] [%s] %s...%s", i, n, qid, question[:50], elapsed_prompt)

    t0 = time.time()

    try:
        rag_result = answer_question(question, ticker_filter=ticker, top_k=5, llm=llm)
    except Exception as e:
        logger.error("  -> RAG FAILED: %s", e)
        return {"id": qid, "question": question, "error": str(e)}

    answer = rag_result["answer"]
    sources = rag_result["sources"]
    total_time = round(time.time() - t0, 1)

    if not _has_answer_content(answer):
        times.append(total_time)
        logger.info("  -> RETRIEVAL GAP — answer has no info [%s]", fmt_time(total_time))
        return {
            "id": qid, "question": question,
            "retrieval_gap": True,
            "answer": answer,
            "sources": _summarize_sources(sources),
        }

    prompt = build_judge_prompt(question, answer, sources)
    response = llm.generate(prompt, system=JUDGE_SYSTEM_PROMPT_FULL, max_tokens=4096)
    parsed = parse_judge_response(response)
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
        return {
            "id": qid,
            "question": question,
            "answer": answer,
            "sources": _summarize_sources(sources),
            **parsed,
        }

    logger.warning("  -> PARSE FAILED [%s]", fmt_time(total_time))
    return {"id": qid, "question": question, "error": response}


def _aggregate_results(results: list[dict], times: list[float]) -> dict:
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

    return {
        "overall_faithfulness_strict": round(overall, 4),
        "overall_faithfulness_weighted": round(weighted, 4),
        "total_claims": total,
        "faithful": total_f,
        "partial": total_p,
        "unfaithful": total_u,
        "retrieval_gaps": gaps,
        "results": results,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=int, default=None, help="Run first N questions")
    parser.add_argument("--ids", nargs="*", default=None, help="Specific eval IDs to run")
    args = parser.parse_args()

    eval_set = _load_eval_set(args)

    logger.info("Running RAG + faithfulness eval for %s questions...", len(eval_set))
    logger.info("(each question = 2 LLM calls: 1 generate + 1 judge)\n")

    results = []
    times = []

    for i, item in enumerate(eval_set, 1):
        LLMClient.reset()
        llm = LLMClient()
        result = _process_question(item, llm, times, i, len(eval_set))
        results.append(result)
        _save_checkpoint(results)

    full = _aggregate_results(results, times)

    with open(RESULT_FILE, "w") as f:
        json.dump(full, f, indent=2)

    logger.info("Saved to %s", RESULT_FILE)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
