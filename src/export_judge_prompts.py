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
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from llm import LLMClient
from rag import answer_question

EVAL_FILE = Path(__file__).parent.parent / "data" / "eval_questions.json"
OUT_DIR = Path(__file__).parent.parent / "data"

JUDGE_SYSTEM_PROMPT = """You are a strict but fair faithfulness evaluator for financial RAG systems.

Your job: extract each factual claim from the Answer text ONLY, then check if that claim is supported by the Source chunks.

CRITICAL: Extract claims ONLY from the Answer. Do NOT extract claims from the Source chunks.

Rules:
- FAITHFUL: Source supports the claim verbatim or minor rephrasing. Numbers, percentages, dollar amounts must match exactly.
- PARTIALLY FAITHFUL: Source supports general direction but specific detail is wrong (e.g. wrong number, wrong period).
- UNFAITHFUL: Source contradicts the claim or does not contain the information.
- Evaluate each claim independently against ALL sources. A claim about one period is FAITHFUL if its numbers match the source for that period.

Return ONLY valid JSON:
{"claims": [{"claim": "...", "verdict": "FAITHFUL|PARTIALLY FAITHFUL|UNFAITHFUL"}], "faithful_count": N, "partial_count": N, "unfaithful_count": N, "total_claims": N}"""


def build_judge_prompt_compact(question: str, answer: str, sources: list[dict]) -> str:
    context_blocks = []
    for s in sources:
        meta = s.get("metadata", {})
        label = f"[{meta.get('ticker', '?')} {meta.get('form', '?')} filed {meta.get('filing_date', '?')}]"
        text = s.get("text", "")
        # Truncate to 800 chars per source chunk
        if len(text) > 800:
            text = text[:800] + "..."
        context_blocks.append(f"{label}\n{text}")
    return f"Question: {question}\n\nSource chunks:\n{chr(10)+chr(10).join(context_blocks) if context_blocks else '(no sources)'}\n\n---\n\nAnswer:\n{answer}"


def _generate_from_cache(eval_set: list[dict], split: int | None) -> None:
    """Re-export judge prompts from cached faithfulness_results.json (no model needed)."""
    cache_path = Path(__file__).parent.parent / "data" / "faithfulness_results.json"
    if not cache_path.exists():
        print(f"ERROR: {cache_path} not found. Run src/eval_faithfulness.py first.")
        sys.exit(1)

    with open(cache_path) as f:
        cache = json.load(f)

    cache_map = {r["id"]: r for r in cache.get("results", []) if "answer" in r}

    outputs = []
    for item in eval_set:
        qid = item["id"]
        cached = cache_map.get(qid)
        if not cached or cached.get("retrieval_gap"):
            print(f"  SKIP {qid}: no cached answer found")
            continue

        answer = cached["answer"]
        sources = cached.get("sources", [])
        prompt = build_judge_prompt_compact(item["question"], answer, sources)
        outputs.append({"id": qid, "prompt": prompt, "question": item["question"], "answer_preview": answer[:80]})
        print(f"  [{qid}] {item['question'][:50]}... done")

    if not outputs:
        print("No cached results to export.")
        return

    _write_batches(outputs, split)
    print(f"  Exported {len(outputs)} questions from cache")


def _write_batches(outputs: list[dict], split: int | None) -> None:
    """Write individual and batch files (shared between live and cached modes)."""
    path_all = OUT_DIR / "claude_all_questions.txt"
    with open(path_all, "w", encoding="utf-8") as f:
        f.write("=" * 60 + "\n")
        f.write("FAITHFULNESS EVALUATION — ALL QUESTIONS\n")
        f.write("=" * 60 + "\n\n")
        f.write("INSTRUCTION: Evaluate each question below. Return JSON for each.\n")
        f.write("System prompt:\n")
        f.write(JUDGE_SYSTEM_PROMPT)
        f.write("\n\n")
        for o in outputs:
            f.write("-" * 40 + "\n")
            f.write(f"QUESTION: {o['id']} — {o['question']}\n")
            f.write("-" * 40 + "\n")
            f.write(o["prompt"])
            f.write("\n\n")
    print(f"  Saved {path_all.name} ({path_all.stat().st_size} bytes)")

    # Individual
    for o in outputs:
        path = OUT_DIR / f"claude_{o['id']}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write(o["prompt"])
        print(f"  Saved {path.name}")

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
                f.write(JUDGE_SYSTEM_PROMPT)
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
            print(f"  Saved {path.name} ({len(batch)} questions, {path.stat().st_size} bytes)")


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
        print("No matching questions found.")
        sys.exit(1)

    if args.from_cache:
        _generate_from_cache(eval_set, args.split)
        return

    try:
        llm = LLMClient()
    except ValueError as e:
        print(f"ERROR: Cannot load LLM model: {e}")
        print()
        print("Options:")
        print("  1. Set LLAMA_CPP_MODEL_PATH in .env to your .gguf file")
        print("  2. Use --from-cache to re-export from cached eval results")
        sys.exit(1)
    outputs = []
    TOT_SYSTEM_PROMPT = "You are an AI assistant that helps export RAG evaluation data. Respond with 'OK' when you receive data."

    for item in eval_set:
        qid = item["id"]
        question = item["question"]
        ticker = item.get("ticker_filter")
        print(f"  [{qid}] {question[:50]}... ", end="", flush=True)

        rag_result = answer_question(question, ticker_filter=ticker, top_k=5, llm=llm)
        answer = rag_result["answer"]
        sources = rag_result["sources"]
        prompt = build_judge_prompt_compact(question, answer, sources)
        outputs.append({"id": qid, "prompt": prompt, "question": question, "answer_preview": answer[:80]})
        print(f"done ({len(answer)} chars)")

    _write_batches(outputs, args.split)


if __name__ == "__main__":
    main()
