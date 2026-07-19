"""
Benchmark: compare retrieval methods side-by-side.

Measures recall@k, MRR, and latency for 5 methods:
  - Dense Only (nomic-embed, no BM25/CE)
  - BM25 Only (keyword, no embeddings)
  - Hybrid (dense + BM25, no CE)
  - Hybrid + Cross-Encoder
  - Full Pipeline (expansion + hybrid + CE + penalties)

Usage:
    python src/benchmark_methods.py
"""

import json
import logging
import os
import subprocess
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any

from hybrid_search import bm25_scores, build_bm25
from retrieval import get_client, get_collection

logger = logging.getLogger(__name__)

ROOT = Path(__file__).parent.parent
EVAL_FILE = ROOT / "data" / "eval_questions.json"
EVAL_SCRIPT = ROOT / "src" / "eval_recall.py"
K_VALUES = [1, 3, 5, 10]

METHODS: list[dict[str, Any]] = [
    {
        "name": "Dense Only",
        "subprocess": True,
        "env": {
            "RAG_EXPANSION_ENABLED": "false",
            "RAG_HYBRID_SEARCH_ENABLED": "false",
            "RAG_CROSS_ENCODER_ENABLED": "false",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "false",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "name": "Hybrid (dense + BM25)",
        "subprocess": True,
        "env": {
            "RAG_EXPANSION_ENABLED": "false",
            "RAG_HYBRID_SEARCH_ENABLED": "true",
            "RAG_CROSS_ENCODER_ENABLED": "false",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "false",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "name": "Hybrid + Cross-Encoder",
        "subprocess": True,
        "env": {
            "RAG_EXPANSION_ENABLED": "false",
            "RAG_HYBRID_SEARCH_ENABLED": "true",
            "RAG_CROSS_ENCODER_ENABLED": "true",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "false",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "name": "Full Pipeline",
        "subprocess": True,
        "env": {
            "RAG_EXPANSION_ENABLED": "true",
            "RAG_HYBRID_SEARCH_ENABLED": "true",
            "RAG_CROSS_ENCODER_ENABLED": "true",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "true",
            "RAG_KEYWORD_BOOST_ENABLED": "true",
        },
    },
]


def load_eval_set(path: Path) -> list[dict]:
    with open(path) as f:
        return json.load(f)


def parse_ablation_results(stdout: str) -> dict[str, str]:
    metrics: dict[str, str] = {}
    for line in stdout.splitlines():
        line = line.strip()
        if line.startswith("AVERAGE"):
            parts = line.split()
            vals = [p for p in parts if p.replace(".", "").isdigit()]
            if len(vals) >= 4:
                metrics["recall@1"] = vals[0]
                metrics["recall@3"] = vals[1]
                metrics["recall@5"] = vals[2]
                metrics["recall@10"] = vals[4] if len(vals) > 4 else vals[3]
        if line.startswith("MRR"):
            metrics["MRR"] = line.split(":")[-1].strip()
    return metrics


def run_subprocess(env_overrides: dict[str, str]) -> dict[str, str]:
    full_env = {**os.environ.copy(), **env_overrides}
    result = subprocess.run(
        [sys.executable, str(EVAL_SCRIPT)],
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(ROOT),
    )
    output = result.stderr or result.stdout
    return parse_ablation_results(output)


def run_bm25_only() -> dict[str, str]:
    """Eval for BM25-only retrieval (no dense, no CE, no expansion)."""
    eval_set = load_eval_set(EVAL_FILE)
    client = get_client()
    collection = get_collection(client)

    all_recalls: dict[int, list[float]] = {k: [] for k in K_VALUES}
    reciprocal_ranks: list[float] = []
    timing_log: dict[str, list[float]] = defaultdict(list)

    for item in eval_set:
        question = item["question"]
        ticker = item.get("ticker_filter")
        golden = set(item["golden_chunk_ids"])

        cache_key = ticker or "__ALL__"
        get_kw = {} if cache_key == "__ALL__" else {"where": {"ticker": cache_key}}
        all_docs = collection.get(**get_kw)
        texts = all_docs["documents"]
        metas = all_docs["metadatas"]

        t0 = time.perf_counter()
        bm25 = build_bm25(texts)
        bm25_raw = bm25_scores(bm25, question, texts)
        t1 = time.perf_counter()
        timing_log["bm25_build_score"].append(t1 - t0)

        paired = sorted(
            zip(bm25_raw, texts, metas, strict=True), key=lambda x: -x[0]
        )
        retrieved_ids = []
        for _score, _text, meta in paired[: max(K_VALUES)]:
            cid = f"{meta['ticker']}_{meta['accession_number']}_{meta['chunk_index']}"
            retrieved_ids.append(cid)

        best_rank = None
        for rank, cid in enumerate(retrieved_ids, 1):
            if cid in golden:
                best_rank = rank
                break
        rr = 1.0 / best_rank if best_rank else 0.0
        reciprocal_ranks.append(rr)

        for k in K_VALUES:
            hits = len(set(retrieved_ids[:k]) & golden)
            all_recalls[k].append(hits / len(golden) if golden else 0)

    n = len(eval_set)
    metrics = {}
    for k in K_VALUES:
        metrics[f"recall@{k}"] = f"{sum(all_recalls[k]) / n:.2f}"
    metrics["MRR"] = f"{sum(reciprocal_ranks) / n:.4f}"
    avg_timing = {k: f"{sum(v)/len(v)*1000:.0f}ms" for k, v in timing_log.items()}
    metrics["latency"] = avg_timing.get("bm25_build_score", "?")
    return metrics


def main() -> None:
    print("=" * 70)
    print("  Benchmark: Retrieval Methods Comparison")
    print(f"  Eval set: {len(load_eval_set(EVAL_FILE))} questions")
    print("=" * 70)

    results: list[tuple[str, dict[str, str]]] = []

    # BM25-only runs inline (needs custom pipeline)
    print("\n[1/5] BM25 Only...", end=" ", flush=True)
    bm25_metrics = run_bm25_only()
    print(f"recall@10={bm25_metrics.get('recall@10', '?')}, MRR={bm25_metrics.get('MRR', '?')}")
    results.append(("BM25 Only", bm25_metrics))

    # Remaining methods via subprocess
    for i, method in enumerate(METHODS, 2):
        print(f"[{i}/5] {method['name']}...", end=" ", flush=True)
        metrics = run_subprocess(method["env"])
        print(f"recall@10={metrics.get('recall@10', '?')}, MRR={metrics.get('MRR', '?')}")
        results.append((method["name"], metrics))

    # Output table
    keys = ["recall@1", "recall@3", "recall@5", "recall@10", "MRR"]
    col_w = 26
    sep = " | "
    header = f"{'Method':<{col_w}}" + sep.join(f"{k:>{10}}" for k in keys)
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))
    for name, metrics in results:
        row = f"{name:<{col_w}}" + sep.join(
            f"{metrics.get(k, '?'):>{10}}" for k in keys
        )
        print(row)
    print("=" * len(header))
    print("\nAll methods evaluated on the same 40 ground-truth questions across 7 companies.")
    print("BM25-only runs inline (no subprocess). Other methods via eval_recall.py.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.WARNING)
    main()
