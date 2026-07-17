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


def _strip_json_trailing(text: str) -> str:
    """Remove trailing comments (//) and parenthetical explanations after JSON values."""
    lines = text.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        in_string = False
        for i, ch in enumerate(stripped):
            if ch == '"' and (i == 0 or stripped[i-1] != '\\'):
                in_string = not in_string
            if not in_string:
                if stripped[i:i+2] == "//":
                    result.append(stripped[:i].rstrip())
                    break
                if ch == '"' and i > 0 and stripped[i-1] not in ('\\', ':'):
                    rest = stripped[i+1:]
                    if rest.startswith(")") or rest.startswith(" ("):
                        result.append(stripped[:i+1])
                        break
        else:
            result.append(line)
    return "\n".join(result)


def _try_parse_one(obj_str: str) -> dict | None:
    for _ in range(3):
        try:
            return json.loads(obj_str)
        except json.JSONDecodeError:
            last_brace = obj_str.rfind("}")
            penultimate_brace = obj_str.rfind("}", 0, last_brace) if last_brace > 0 else -1
            if penultimate_brace != -1:
                obj_str = obj_str[:penultimate_brace + 1]
                continue
            break
    return None


def _merge_judge_results(objects: list[dict]) -> dict:
    claims = []
    faithful = partial = unfaithful = 0
    for obj in objects:
        claims.extend(obj.get("claims", []))
        faithful += obj.get("faithful_count", 0)
        partial += obj.get("partial_count", 0)
        unfaithful += obj.get("unfaithful_count", 0)
    total = faithful + partial + unfaithful
    score = faithful / total if total > 0 else 0.0
    return {
        "claims": claims,
        "faithful_count": faithful,
        "partial_count": partial,
        "unfaithful_count": unfaithful,
        "total_claims": total,
        "faithfulness_score": round(score, 4),
    }


def parse_judge_response(response: str) -> dict | None:
    cleaned = response.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    cleaned = _strip_json_trailing(cleaned)
    if cleaned.endswith("},"):
        cleaned = cleaned[:-1]
    # Try direct parse first
    parsed = _try_parse_one(cleaned)
    if parsed is not None:
        return parsed
    # Handle multiple concatenated JSON objects (one per fiscal period)
    import re as _re
    objects = []
    idx = 0
    while idx < len(cleaned):
        brace_start = cleaned.find("{", idx)
        if brace_start == -1:
            break
        depth = 0
        for end_idx in range(brace_start, len(cleaned)):
            ch = cleaned[end_idx]
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    candidate = cleaned[brace_start:end_idx + 1]
                    obj = _try_parse_one(candidate)
                    if obj is not None:
                        objects.append(obj)
                    idx = end_idx + 1
                    break
        else:
            break
    if objects:
        return _merge_judge_results(objects)
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
        logger.error("%s not found.", EVAL_FILE)
        sys.exit(1)

    with open(EVAL_FILE) as f:
        eval_set = json.load(f)

    if args.ids and args.sample:
        logger.warning("Both --ids and --sample provided. Using --ids, ignoring --sample.")
    if args.ids:
        eval_set = [q for q in eval_set if q["id"] in args.ids]
    elif args.sample:
        eval_set = eval_set[:args.sample]

    if not eval_set:
        logger.error("No matching questions found.")
        sys.exit(1)

    return eval_set


_SECTION_PATTERN = re.compile(
    r"^-\s*\[.*?\]\s*(?:-\s*)?.*?(?:Not directly discussed|not discussed|no information|"
    r"not mentioned|does not provide|not addressed|not covered)", re.MULTILINE
)


def _has_answer_content(answer: str) -> bool:
    answer_lower = answer.lower()
    stripped = _SECTION_PATTERN.sub("", answer_lower).strip()
    if not stripped:
        return False
    no_info = ["do not discuss", "no information", "does not provide",
               "not addressed", "the provided filings do not"]
    return not any(p in stripped for p in no_info)


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

    avg = sum(times) / len(times) if times else 0
    warm = min(len(times), 3)
    recent = sum(times[-warm:]) / warm if times else 0
    rate = min(avg, recent * 1.2)
    remaining = int(rate * (n - i))
    elapsed_prompt = f" [~{fmt_time(remaining)} remaining]" if times else ""
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
