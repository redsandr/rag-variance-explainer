"""
Export judge prompts for manual evaluation via external LLM (e.g. Claude web).
Compact format — optimized for Claude free tier token limits.

Usage:
    python src/export_judge_prompts.py                    # all 20 questions
    python src/export_judge_prompts.py --ids eval-004 eval-009
    python src/export_judge_prompts.py --split 3          # split into 3 batches
"""

import argparse
import json
import logging
import math
import sys
from pathlib import Path

from llm import LLMClient
from prompts import JUDGE_SYSTEM_PROMPT_MEDIUM, build_judge_prompt_compact
from rag import answer_question

logger = logging.getLogger(__name__)

EVAL_FILE = Path(__file__).parent.parent / "data" / "eval_questions.json"
OUT_DIR = Path(__file__).parent.parent / "data"


def _generate_from_cache(eval_set: list[dict], split: int | None) -> None:
    """Re-export judge prompts from cached faithfulness_results.json (no model needed)."""
    cache_path = Path(__file__).parent.parent / "data" / "faithfulness_results.json"
    if not cache_path.exists():
        logger.error("%s not found. Run src/eval_faithfulness.py first.", cache_path)
        sys.exit(1)

    with open(cache_path) as f:
        cache = json.load(f)

    cache_map = {r["id"]: r for r in cache.get("results", []) if "answer" in r}

    outputs = []
    for item in eval_set:
        qid = item["id"]
        cached = cache_map.get(qid)
        if not cached or cached.get("retrieval_gap"):
            logger.info("  SKIP %s: no cached answer found", qid)
            continue

        answer = cached["answer"]
        sources = cached.get("sources", [])
        prompt = build_judge_prompt_compact(item["question"], answer, sources)
        outputs.append({"id": qid, "prompt": prompt, "question": item["question"], "answer_preview": answer[:80]})
        logger.info("  [%s] %s... done", qid, item["question"][:50])

    if not outputs:
        logger.warning("No cached results to export.")
        return

    _write_batches(outputs, split)
    logger.info("  Exported %s questions from cache", len(outputs))


def _write_batches(outputs: list[dict], split: int | None) -> None:
    """Write individual and batch files (shared between live and cached modes)."""
    path_all = OUT_DIR / "claude_all_questions.txt"
    with open(path_all, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("FAITHFULNESS EVALUATION — ALL QUESTIONS\n")
        f.write("=" * 60 + "\n\n")
        f.write("INSTRUCTION: Evaluate each question below. Return JSON for each.\n")
        f.write("System prompt:\n")
        f.write(JUDGE_SYSTEM_PROMPT_MEDIUM)
        f.write("\n\n")
        for o in outputs:
            f.write("-" * 40 + "\n")
            f.write(f"QUESTION: {o['id']} — {o['question']}\n")
            f.write("-" * 40 + "\n")
            f.write(o["prompt"])
            f.write("\n\n")
    logger.info("  Saved %s (%s bytes)", path_all.name, path_all.stat().st_size)

    # Individual
    for o in outputs:
        path = OUT_DIR / f"claude_{o['id']}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(o["prompt"])
        logger.info("  Saved %s", path.name)

    # Batches
    if split and split > 0:
        n = math.ceil(len(outputs) / split)
        batches = [outputs[i:i + n] for i in range(0, len(outputs), n)]
        for i, batch in enumerate(batches, 1):
            path = OUT_DIR / f"claude_batch_{i}_of_{len(batches)}.txt"
            with open(path, "w", encoding="utf-8") as f:
                f.write("=" * 60 + "\n")
                f.write("SYSTEM PROMPT (paste ONCE as first message):\n")
                f.write("=" * 60 + "\n")
                f.write(JUDGE_SYSTEM_PROMPT_MEDIUM)
                f.write("\n\n")
                f.write("=" * 60 + "\n")
                f.write(f"BATCH {i} of {len(batches)} — {len(batch)} questions\n")
                f.write("=" * 60 + "\n\n")
                for o in batch:
                    f.write("-" * 40 + "\n")
                    f.write(f"QUESTION: {o['id']} — {o['question']}\n")
                    f.write("-" * 40 + "\n")
                    f.write(o["prompt"])
                    f.write("\n\n")
            logger.info("  Saved %s (%s questions, %s bytes)", path.name, len(batch), path.stat().st_size)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ids", nargs="*", default=None)
    parser.add_argument("--split", type=int, default=None, help="Split into N batches")
    parser.add_argument("--from-cache", action="store_true",
                        help="Use cached RAG outputs from faithfulness_results.json instead of re-running")
    args = parser.parse_args()

    with open(EVAL_FILE) as f:
        eval_set = json.load(f)

    if args.ids:
        eval_set = [q for q in eval_set if q["id"] in args.ids]

    if not eval_set:
        logger.error("No matching questions found.")
        sys.exit(1)

    if args.from_cache:
        _generate_from_cache(eval_set, args.split)
        return

    try:
        llm = LLMClient()
    except ValueError as e:
        logger.error("Cannot load LLM model: %s", e)
        logger.error("")
        logger.error("Options:")
        logger.error("  1. Set LLAMA_CPP_MODEL_PATH in .env to your .gguf file")
        logger.error("  2. Use --from-cache to re-export from cached eval results")
        sys.exit(1)
    outputs = []

    for item in eval_set:
        qid = item["id"]
        question = item["question"]
        ticker = item.get("ticker_filter")
        logger.info("  [%s] %s...", qid, question[:50])

        rag_result = answer_question(question, ticker_filter=ticker, top_k=5, llm=llm)
        answer = rag_result["answer"]
        sources = rag_result["sources"]
        prompt = build_judge_prompt_compact(question, answer, sources)
        outputs.append({"id": qid, "prompt": prompt, "question": question, "answer_preview": answer[:80]})
        logger.info("  done (%s chars)", len(answer))

    _write_batches(outputs, args.split)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
