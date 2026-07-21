"""
End-to-end pipeline: fetch filings -> extract MD&A -> chunk -> embed & store.
"""

import logging

from chunking import chunk_document
from config import config
from constants import TICKERS
from ingest import (
    fetch_submissions,
    get_cik,
    get_mda_for_filing,
    list_10k_10q_filings,
)
from post_process import tag_chunk
from retrieval import add_chunks, delete_chunks_for_filing, flush_bm25_cache, get_client, get_collection

logger = logging.getLogger(__name__)


def build_index() -> None:
    client = get_client()
    collection = get_collection(client)

    total_chunks_indexed = 0
    failures = []

    for ticker in TICKERS:
        logger.info("=== %s ===", ticker)

        try:
            cik = get_cik(ticker)
            submissions = fetch_submissions(cik)
            filings = list_10k_10q_filings(submissions)[
                : config.build_filings_per_company
            ]
        except Exception as e:
            logger.error("  SKIP %s — pre-processing failed: %s", ticker, e)
            failures.append((ticker, "N/A", "N/A", "N/A", str(e)))
            continue

        for filing in filings:
            accession = filing["accessionNumber"]
            form = filing["form"]
            filing_date = filing["filingDate"]

            try:
                mda_text = get_mda_for_filing(
                    cik, accession, filing["primaryDocument"]
                )
                chunks = chunk_document(mda_text, chunk_size=500, chunk_overlap=50)

                delete_chunks_for_filing(collection, ticker, accession)

                enriched_metadatas = []
                for i, chunk in enumerate(chunks):
                    base = {
                        "ticker": ticker,
                        "accession_number": accession,
                        "form": form,
                        "filing_date": filing_date,
                        "chunk_index": i,
                    }
                    enriched = tag_chunk(chunk, base)
                    enriched_metadatas.append(enriched)

                add_chunks(
                    collection,
                    chunks=chunks,
                    ticker=ticker,
                    accession_number=accession,
                    form=form,
                    filing_date=filing_date,
                    metadatas=enriched_metadatas,
                )

                logger.info("  OK %s %s - %s chunks", form, filing_date, len(chunks))
                total_chunks_indexed += len(chunks)

            except Exception as e:
                logger.error("  FAIL %s %s - FAILED: %s", form, filing_date, e)
                failures.append((ticker, accession, form, filing_date, str(e)))

    logger.info("%s", "=" * 50)
    logger.info("Total chunks indexed: %s", total_chunks_indexed)
    logger.info("Failures: %s", len(failures))
    if failures:
        logger.warning("Failed filings (review these before assuming full coverage):")
        for ticker, accession, form, filing_date, error in failures:
            logger.warning("  %s %s %s (%s): %s", ticker, form, filing_date, accession, error)

    flush_bm25_cache()
    logger.info("BM25 cache flushed — stale indexes cleared")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    build_index()
