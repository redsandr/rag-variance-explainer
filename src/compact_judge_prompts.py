"""
Create compact Claude-friendly judge prompts from existing exports.
No model needed — just reformats existing files.
"""

import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUT_DIR = DATA_DIR

JUDGE_SYSTEM_PROMPT = """You are a strict but fair faithfulness evaluator for financial RAG systems.

Rules:
- FAITHFUL: Source supports claim verbatim or minor rephrasing. Numbers must match exactly.
- PARTIALLY FAITHFUL: Source supports general direction but specific detail is wrong.
- UNFAITHFUL: Source contradicts claim or does not contain the information.
- Evaluate each claim independently against ALL sources.

Return ONLY valid JSON:
{"claims": [{"claim": "...", "verdict": "FAITHFUL|PARTIALLY FAITHFUL|UNFAITHFUL"}], "faithful_count": N, "partial_count": N, "unfaithful_count": N, "total_claims": N}"""


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
        print("No judge prompt files found. Run export_judge_prompts.py first.")
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
    sys_size = len(JUDGE_SYSTEM_PROMPT)
    total_per_question = sum(o["size"] for o in outputs)
    total = sys_size + total_per_question

    print(f"=== Size Analysis ===")
    print(f"System prompt: {sys_size} chars (~{sys_size//4} tokens)")
    per_q = [f"{o['id']}: {o['size']} chars (~{o['size']//4} tokens)" for o in outputs]
    print(f"Per question: {per_q}")
    print(f"All questions total: {total_per_question} chars (~{total_per_question//4} tokens)")
    print(f"Grand total (with system): {total} chars (~{total//4} tokens)")
    print()

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
            f.write(JUDGE_SYSTEM_PROMPT)
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
        print(f"  {path.name}: {len(batch)} questions, {size_kb:.0f} KB (~{path.stat().st_size//4} tokens)")

    # Summary per batch with question IDs
    print(f"\n=== Workflow ===")
    print(f"Total: {len(outputs)} questions, split into {len(batches)} Claude sessions")
    for i, batch in enumerate(batches, 1):
        ids = [o["id"] for o in batch]
        print(f"  Session {i}: {', '.join(ids)}")
    print(f"\nFor each session:")
    print(f"  1. Open Claude web, paste SYSTEM PROMPT as first message")
    print(f"  2. Paste question prompts one at a time as follow-ups")
    print(f"  3. Claude returns JSON — copy and send to me")


if __name__ == "__main__":
    main()
