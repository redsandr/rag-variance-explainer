"""
Extract dataset statistics from ChromaDB for documentation.

Usage:
    python src/dataset_stats.py
"""

from collections import Counter, defaultdict

from retrieval import get_client, get_collection

SECTOR_MAP = {
    "CMG": "Restaurant",
    "DRI": "Restaurant",
    "CBRL": "Restaurant",
    "WMT": "Retail",
    "TGT": "Retail",
    "JNJ": "Healthcare",
    "XOM": "Energy",
}


def main() -> None:
    client = get_client()
    collection = get_collection(client)
    all_data = collection.get()
    metas = all_data["metadatas"]
    docs = all_data["documents"]

    total_chunks = len(metas)
    total_tokens = sum(len(d.split()) for d in docs)

    ticker_count: Counter = Counter()
    year_count: Counter = Counter()
    form_count: Counter = Counter()
    filing_dates: dict[str, set] = defaultdict(set)
    ticker_filings: dict[str, set] = defaultdict(set)

    for m in metas:
        t = m.get("ticker", "UNKNOWN")
        ticker_count[t] += 1
        form_count[m.get("form", "?")] += 1
        fd = m.get("filing_date", "")
        year = fd[:4] if fd else "?"
        year_count[year] += 1
        filing_dates[t].add(fd)
        ticker_filings[t].add(f"{fd}_{m.get('form', '?')}")

    sector_count: Counter = Counter()
    for t, cnt in ticker_count.items():
        sector_count[SECTOR_MAP.get(t, "Other")] += cnt

    print(f"Total chunks: {total_chunks}")
    print(f"Total tokens (approx): {total_tokens}")
    print(f"Total filings (unique date+form): {sum(len(v) for v in ticker_filings.values())}")
    print()

    print("--- Per Ticker ---")
    for t in sorted(ticker_count):
        n_chunks = ticker_count[t]
        n_filings = len(ticker_filings[t])
        years = sorted(set(fd[:4] for fd in filing_dates[t] if fd))
        print(f"  {t}: {n_chunks} chunks, {n_filings} filings ({', '.join(years)})")

    print()
    print("--- Per Sector ---")
    for s in sorted(sector_count):
        pct = sector_count[s] / total_chunks * 100
        print(f"  {s}: {sector_count[s]} chunks ({pct:.1f}%)")

    print()
    print("--- Per Form ---")
    for f in sorted(form_count):
        print(f"  {f}: {form_count[f]}")

    print()
    print("--- Per Year ---")
    for y in sorted(year_count):
        print(f"  {y}: {year_count[y]} chunks")


if __name__ == "__main__":
    main()
