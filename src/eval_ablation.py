"""
Ablation study: measure recall@k contribution of each pipeline component.

Runs eval_recall with different component combinations and prints a
comparison table. Each run is a subprocess with isolated env vars so
config mutations don't leak between runs.

Usage:
    python src/eval_ablation.py
"""

import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).parent.parent
EVAL_SCRIPT = ROOT / "src" / "eval_recall.py"

ABLATIONS: list[dict[str, Any]] = [
    {
        "label": "Baseline",
        "env": {
            "RAG_EXPANSION_ENABLED": "false",
            "RAG_HYBRID_SEARCH_ENABLED": "false",
            "RAG_CROSS_ENCODER_ENABLED": "false",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "false",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "label": "+ Query Expansion",
        "env": {
            "RAG_EXPANSION_ENABLED": "true",
            "RAG_HYBRID_SEARCH_ENABLED": "false",
            "RAG_CROSS_ENCODER_ENABLED": "false",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "false",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "label": "+ Hybrid Search",
        "env": {
            "RAG_EXPANSION_ENABLED": "true",
            "RAG_HYBRID_SEARCH_ENABLED": "true",
            "RAG_CROSS_ENCODER_ENABLED": "false",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "false",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "label": "+ Cross-Encoder",
        "env": {
            "RAG_EXPANSION_ENABLED": "true",
            "RAG_HYBRID_SEARCH_ENABLED": "true",
            "RAG_CROSS_ENCODER_ENABLED": "true",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "false",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "label": "+ Forward-Looking Penalty",
        "env": {
            "RAG_EXPANSION_ENABLED": "true",
            "RAG_HYBRID_SEARCH_ENABLED": "true",
            "RAG_CROSS_ENCODER_ENABLED": "true",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "true",
            "RAG_KEYWORD_BOOST_ENABLED": "false",
        },
    },
    {
        "label": "Full Pipeline",
        "env": {
            "RAG_EXPANSION_ENABLED": "true",
            "RAG_HYBRID_SEARCH_ENABLED": "true",
            "RAG_CROSS_ENCODER_ENABLED": "true",
            "RAG_FORWARD_LOOKING_PENALTY_ENABLED": "true",
            "RAG_KEYWORD_BOOST_ENABLED": "true",
        },
    },
]

KEYS = ["recall@1", "recall@3", "recall@5", "recall@10", "MRR"]


def parse_metrics(stdout: str) -> dict[str, str]:
    """Parse AVERAGE and MRR lines from eval_recall.py stdout."""
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


def run_ablation(label: str, env: dict[str, str]) -> dict[str, str]:
    full_env = {**os.environ.copy(), **env}
    result = subprocess.run(
        [sys.executable, str(EVAL_SCRIPT)],
        capture_output=True,
        text=True,
        env=full_env,
        cwd=str(ROOT),
    )
    output = result.stderr or result.stdout
    metrics = parse_metrics(output)
    print(f"  {label}: recall@10={metrics.get('recall@10', '?')}, MRR={metrics.get('MRR', '?')}")
    return metrics


def print_table(results: list[tuple[str, dict[str, str]]]) -> None:
    col_w = 22
    sep = " | "
    header = f"{'Pipeline':<{col_w}}" + sep.join(f"{k:>{10}}" for k in KEYS)
    print("\n" + "=" * len(header))
    print(header)
    print("=" * len(header))
    for label, metrics in results:
        row = f"{label:<{col_w}}" + sep.join(f"{metrics.get(k, '?'):>{10}}" for k in KEYS)
        print(row)
    print("=" * len(header))
    print("\nMetrics: recall@k averaged across all 40 questions (20 restaurant + 20 retail).")
    print("MRR = Mean Reciprocal Rank (lower = golden chunk ranked further down).")


def main() -> None:
    print(f"Ablation Study — {len(ABLATIONS)} configurations")
    print("Eval set: 40 questions (20 restaurant + 20 retail)")
    print("-" * 60)
    results: list[tuple[str, dict[str, str]]] = []
    for cfg in ABLATIONS:
        metrics = run_ablation(cfg["label"], cfg["env"])
        results.append((cfg["label"], metrics))
    print_table(results)


if __name__ == "__main__":
    main()
