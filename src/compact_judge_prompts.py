"""
Create compact Claude-friendly judge prompts from existing exports.
No model needed — just reformats existing files.
"""

import logging
import re
from pathlib import Path

from prompts import JUDGE_SYSTEM_PROMPT_COMPACT

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_DIR = DATA_DIR


def extract_question(text: str) -> str:
    m = re.search(r"Question:\s*(.+)", text)
    return m.group(1).strip() if m else ""


def extract_answer(text: str) -> str:
    m = re.search(r"Answer to evaluate:\n(.+)", text, re.DOTALL)
    return m.group(1).strip() if m else ""


def extract_sources(text: str) -> list[dict]:
    lines = text.split("\n")
    sources = []
    current_label = None
    current_text = []
    in_sources = False
    for line in lines:
        if line.startswith("Source chunks:"):
            in_sources = True
            continue
        if line.strip() == "---" and in_sources:
            if current_label and current_text:
                sources.append({"label": current_label, "text": "\n".join(current_text).strip()})
            break
        if not in_sources:
            continue
        if line.startswith("[") and "]" in line:
            if current_label and current_text:
                sources.append({"label": current_label, "text": "\n".join(current_text).strip()})
            current_label = line.strip()
            current_text = []
        else:
            current_text.append(line)
    if current_label and current_text and in_sources:
        sources.append({"label": current_label, "text": "\n".join(current_text).strip()})
    return sources


def main():
    files = sorted(OUT_DIR.glob("judge_prompt_eval-*.txt"))
    if not files:
        logger.error("No judge prompt files found. Run export_judge_prompts.py first.")
        return

    outputs = []
    for f in files:
        text = f.read_text(encoding="utf-8")
        qid = f.stem.replace("judge_prompt_", "")
        question = extract_question(text)
        sources = extract_sources(text)
        answer = extract_answer(text)

        # Compact source chunks (800 chars each)
        compact_sources = []
        for s in sources:
            chunk = s["text"]
            if len(chunk) > 800:
                chunk = chunk[:800] + "..."
            compact_sources.append(f"{s['label']}\n{chunk}")

        prompt = f"Question: {question}\n\nSource chunks:\n{chr(10)+chr(10).join(compact_sources) if compact_sources else '(no sources)'}\n\n---\n\nAnswer:\n{answer}"
        outputs.append({"id": qid, "prompt": prompt, "question": question, "size": len(prompt)})

    # Sort by ID
    outputs.sort(key=lambda x: x["id"])

    # Calculate sizes
    sys_size = len(JUDGE_SYSTEM_PROMPT_COMPACT)
    total_per_question = sum(o["size"] for o in outputs)
    total = sys_size + total_per_question

    logger.info("=== Size Analysis ===")
    logger.info("System prompt: %s chars (~%s tokens)", sys_size, sys_size // 4)
    per_q = [f"{o['id']}: {o['size']} chars (~{o['size']//4} tokens)" for o in outputs]
    logger.info("Per question: %s", per_q)
    logger.info("All questions total: %s chars (~%s tokens)", total_per_question, total_per_question // 4)
    logger.info("Grand total (with system): %s chars (~%s tokens)", total, total // 4)

    # Determine how many fit per batch for Claude free (~4000 tokens ≈ 16000 chars)
    BUDGET_CHARS = 35000  # ~8700 tokens per batch (Claude free: ~10-15K limit)
    batches = []
    current_batch = []
    current_size = sys_size

    for o in outputs:
        if current_size + o["size"] > BUDGET_CHARS and current_batch:
            batches.append(current_batch)
            current_batch = []
            current_size = sys_size
        current_batch.append(o)
        current_size += o["size"]
    if current_batch:
        batches.append(current_batch)

    # Write batch files
    for i, batch in enumerate(batches, 1):
        path = OUT_DIR / f"claude_batch_{i}_of_{len(batches)}.txt"
        with open(path, "w", encoding="utf-8") as f:
            f.write("=" * 60 + "\n")
            f.write("SYSTEM PROMPT — paste ONCE as first message:\n")
            f.write("=" * 60 + "\n")
            f.write(JUDGE_SYSTEM_PROMPT_COMPACT)
            f.write("\n\n")
            f.write("=" * 60 + "\n")
            f.write(f"BATCH {i} of {len(batches)} — {len(batch)} questions\n")
            f.write(f"Paste each question one at a time as a follow-up message.\n")
            f.write("=" * 60 + "\n\n")
            for o in batch:
                f.write("-" * 40 + "\n")
                f.write(f"QUESTION: {o['id']} — {o['question']}\n")
                f.write("-" * 40 + "\n")
                f.write(o["prompt"])
                f.write("\n\n")
        size_kb = path.stat().st_size / 1024
        logger.info("  %s: %s questions, %s KB (~%s tokens)", path.name, len(batch), f"{size_kb:.0f}", path.stat().st_size // 4)

    # Summary per batch with question IDs
    logger.info("=== Workflow ===")
    logger.info("Total: %s questions, split into %s Claude sessions", len(outputs), len(batches))
    for i, batch in enumerate(batches, 1):
        ids = [o["id"] for o in batch]
        logger.info("  Session %s: %s", i, ", ".join(ids))
    logger.info("For each session:")
    logger.info("  1. Open Claude web, paste SYSTEM PROMPT as first message")
    logger.info("  2. Paste question prompts one at a time as follow-ups")
    logger.info("  3. Claude returns JSON — copy and send to me")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    main()
