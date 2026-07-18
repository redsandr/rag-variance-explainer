"""
Evaluation: measure retrieval recall@k against ground-truth chunks.

Usage:
    python src/eval_recall.py
"""

import json
import logging
from pathlib import Path
from collections import defaultdict

from retrieval import get_client, get_collection, query_multi

logger = logging.getLogger(__name__)

EVAL_FILE = Path(__file__).parent.parent / "data" / "eval_questions.json"
K_VALUES = [1, 3, 5, 8, 10, 15, 20]


def load_eval_set(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def _format_row(parts: list) -> str:
    return "".join(parts)


def evaluate() -> None:
    eval_set = load_eval_set(EVAL_FILE)
    client = get_client()
    collection = get_collection(client)

    lines = []
    header_parts = [f"{'Question':<50} {'golden':<6} {'best_rank':<9}"]
    header_parts += [f"  recall@{k:<4}" for k in K_VALUES]
    lines.append(_format_row(header_parts))
    lines.append("-" * 100)

    all_recalls = {k: [] for k in K_VALUES}
    reciprocal_ranks = []
    by_ticker = defaultdict(lambda: {"recalls": {k: [] for k in K_VALUES}, "rrs": []})

    for item in eval_set:
        qid = item["id"]
        question = item["question"]
        ticker = item.get("ticker_filter")
        golden = set(item["golden_chunk_ids"])

        results = query_multi(
            collection,
            question,
            top_k=max(K_VALUES),
            min_relevance=0.0,
            ticker_filter=ticker,
        )

        retrieved_ids = []
        for r in results:
            meta = r["metadata"]
            cid = f"{meta['ticker']}_{meta['accession_number']}_{meta['chunk_index']}"
            retrieved_ids.append(cid)

        best_rank = None
        for rank, cid in enumerate(retrieved_ids, 1):
            if cid in golden:
                best_rank = rank
                break
        rr = 1.0 / best_rank if best_rank else 0.0
        reciprocal_ranks.append(rr)

        label = f"{qid}: {question[:40]}"
        best_str = str(best_rank) if best_rank else "-"
        parts = [f"{label:<50} {len(golden):<6} {best_str:<9}"]

        ticker = item.get("ticker_filter") or "ALL"
        for k in K_VALUES:
            retrieved_at_k = set(retrieved_ids[:k])
            hits = len(golden & retrieved_at_k)
            recall = hits / len(golden) if golden else 0
            all_recalls[k].append(recall)
            by_ticker[ticker]["recalls"][k].append(recall)
            parts.append(f"  {recall:.2f}    ")
        by_ticker[ticker]["rrs"].append(rr)
        lines.append(_format_row(parts))

    n = len(eval_set)
    mrr = sum(reciprocal_ranks) / n
    lines.append("-" * 100)
    avg_parts = [f"{'AVERAGE':<50} {'':<6} {'':<9}"]
    for k in K_VALUES:
        avg = sum(all_recalls[k]) / n
        avg_parts.append(f"  {avg:.2f}    ")
    lines.append(_format_row(avg_parts))
    lines.append(f"\nMRR (Mean Reciprocal Rank): {mrr:.4f}")
    lines.append(f"Questions with golden chunk NOT in top-20: {reciprocal_ranks.count(0.0)}/{n}")

    lines.append("\n--- By Ticker ---")
    for ticker in sorted(by_ticker):
        d = by_ticker[ticker]
        m = len(d["rrs"])
        t_mrr = sum(d["rrs"]) / m
        lines.append(f"\n  {ticker} ({m} questions, MRR={t_mrr:.4f}):")
        ticker_parts = []
        for k in K_VALUES:
            avg = sum(d["recalls"][k]) / m
            ticker_parts.append(f"    recall@{k:<2} = {avg:.2f}")
        lines.append("".join(ticker_parts))

    logger.info("\n".join(lines))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    evaluate()
