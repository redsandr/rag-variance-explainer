"""Evaluate NLI labels against draft filing-grounded claim cases.

Prints per-case results and confusion counts. Does not change app settings or write scores.
"""

import argparse
import json
from collections import Counter
from pathlib import Path

from nli import NLIClient
from retrieval import get_client, get_collection

DATASET = Path(__file__).resolve().parent.parent / "data" / "nli_claim_eval.json"
LABELS = {"supported": "entailment", "refuted": "contradiction", "not-enough-info": "neutral"}


def score_cases(cases: list[dict], passages: dict[str, str], nli: NLIClient, *, mode: str) -> list[dict]:
    rows = []
    for case in cases:
        premise = case["evidence"] if mode == "excerpt" else passages[case["source"]]
        verdict = nli.verify(case["claim"], [premise])
        predicted = verdict["verdict"] if verdict["supported"] or verdict["verdict"] != "entailment" else "neutral"
        rows.append({"id": case["id"], "ticker": case["ticker"], "category": case["category"],
                     "gold": LABELS[case["label"]], "predicted": predicted,
                     "score": verdict["confidence"], "entailment": verdict["max_entailment"]})
    return rows


def summarize(rows: list[dict]) -> dict:
    confusion = Counter((row["gold"], row["predicted"]) for row in rows)
    return {
        "count": len(rows),
        "correct": sum(row["gold"] == row["predicted"] for row in rows),
        "false_accept": sum(row["gold"] != "entailment" and row["predicted"] == "entailment" for row in rows),
        "false_reject": sum(row["gold"] == "entailment" and row["predicted"] != "entailment" for row in rows),
        "confusion": {f"{gold} -> {predicted}": count for (gold, predicted), count in sorted(confusion.items())},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--model", default="MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli")
    parser.add_argument("--threshold", type=float, default=0.40)
    args = parser.parse_args()

    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    cases = dataset["cases"]
    ids = [case["source"] for case in cases]
    if len({case["id"] for case in cases}) != len(cases):
        raise ValueError("Duplicate evaluation case ID")
    if not all(case["label"] in LABELS for case in cases):
        raise ValueError("Unknown evaluation label")

    indexed = get_collection(get_client()).get(ids=list(set(ids)), include=["documents"])
    passages = dict(zip(indexed["ids"], indexed["documents"], strict=True))
    if missing := set(ids) - passages.keys():
        raise ValueError(f"Missing indexed evidence: {sorted(missing)}")

    nli = NLIClient(model_name=args.model, device=args.device, threshold=args.threshold)
    print(json.dumps({"dataset": dataset["version"], "label_status": dataset["label_status"],
                      "model": args.model, "device": args.device, "threshold": args.threshold,
                      "cases": len(cases), "tickers": sorted({case["ticker"] for case in cases})}))
    for mode in ("excerpt", "indexed-passage"):
        rows = score_cases(cases, passages, nli, mode=mode)
        print(json.dumps({"mode": mode, "results": rows, "summary": summarize(rows)}))


if __name__ == "__main__":
    main()
