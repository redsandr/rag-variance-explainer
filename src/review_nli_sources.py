"""Compare indexed evaluation passages with their original SEC filings without an LLM."""

import json
import re
from pathlib import Path
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from ingest import fetch_filing_html
from retrieval import get_client, get_collection

DATASET = Path(__file__).resolve().parent.parent / "data" / "nli_claim_eval.json"


def passage_overlap(indexed: str, filing_html: str) -> tuple[int, int]:
    original = BeautifulSoup(filing_html, "html.parser").get_text(" ", strip=True)
    tokens = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", indexed.lower())
    original_tokens = re.findall(r"[a-z0-9]+(?:\.[0-9]+)?", original.lower())
    original_ngrams = {tuple(original_tokens[i:i + 8]) for i in range(max(0, len(original_tokens) - 7))}
    selected = [tuple(tokens[i:i + 8]) for i in range(0, max(0, len(tokens) - 7), 8)]
    return sum(ngram in original_ngrams for ngram in selected), len(selected)


def main() -> None:
    dataset = json.loads(DATASET.read_text(encoding="utf-8"))
    sources = dataset["filings"]
    indexed = get_collection(get_client()).get(ids=list(sources), include=["documents"])
    passages = dict(zip(indexed["ids"], indexed["documents"], strict=True))
    if missing := sources.keys() - passages.keys():
        raise ValueError(f"Missing indexed passages: {sorted(missing)}")

    for source, url in sources.items():
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.netloc != "www.sec.gov" or not parsed.path.startswith("/Archives/edgar/data/"):
            raise ValueError(f"Not a SEC filing URL for {source}")
        try:
            html = fetch_filing_html(url)
            matched, sampled = passage_overlap(passages[source], html)
            print(json.dumps({"source": source, "sec_url": url, "matched_windows": matched,
                              "sampled_windows": sampled, "status": "compared"}))
        except Exception as exc:
            print(json.dumps({"source": source, "sec_url": url, "status": "fetch_failed",
                              "error_type": type(exc).__name__}))


if __name__ == "__main__":
    main()
