"""
Auto-generate corpus stats for README.

Queries the ChromaDB collection and prints a markdown snippet with
current chunk count, filing count, and company list — so README numbers
stay in sync with the actual index without manual updates.
"""

import argparse
import logging
import re
import sys
from pathlib import Path

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "readme.md"


def get_collection_stats() -> dict:
    from src.retrieval import get_client, get_collection

    client = get_client()
    collection = get_collection(client)
    count = collection.count()

    all_metas = collection.get(limit=count, include=["metadatas"])["metadatas"]

    tickers = set()
    accessions = set()
    forms = set()
    for m in all_metas:
        tickers.add(m.get("ticker", "?"))
        accessions.add(m.get("accession_number", "?"))
        forms.add(m.get("form", "?"))

    return {
        "chunks": count,
        "filings": len(accessions),
        "companies": len(tickers),
        "tickers": sorted(tickers),
        "forms": sorted(forms),
    }


def format_stats_block(stats: dict) -> str:
    ticker_list = ", ".join(
        f"{t} ({name})" if name else t
        for t in stats["tickers"]
        for name in [{"CMG": "Chipotle", "DRI": "Darden", "CBRL": "Cracker Barrel",
                       "WMT": "Walmart", "TGT": "Target", "JNJ": "Johnson & Johnson",
                       "XOM": "Exxon Mobil"}.get(t, "")]
    )
    return (
        f"| Index | **{stats['chunks']}+ chunks** from {stats['filings']} filings "
        f"across {stats['companies']} companies ({ticker_list}) |"
    )


def update_readme(stats: dict) -> bool:
    content = README_PATH.read_text(encoding="utf-8")
    new_line = format_stats_block(stats)

    pattern = r"\| Index \| .+ \|"
    if re.search(pattern, content):
        content = re.sub(pattern, new_line, content)
        README_PATH.write_text(content, encoding="utf-8")
        return True
    return False


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Update corpus stats in README from ChromaDB"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Only print stats without modifying README",
    )
    args = parser.parse_args()

    try:
        stats = get_collection_stats()
    except Exception as e:
        logger.error("Failed to query ChromaDB: %s", e)
        sys.exit(1)

    block = format_stats_block(stats)
    print(block)

    if not args.check:
        updated = update_readme(stats)
        if updated:
            print(f"Updated {README_PATH}")
        else:
            print("Could not find Index line in README (pattern mismatch)")
    else:
        print("--check mode: README not modified")


if __name__ == "__main__":
    main()
