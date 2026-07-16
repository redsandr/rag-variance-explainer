"""
End-to-end pipeline: fetch filings -> extract MD&A -> chunk -> embed & store.
"""

import logging

from ingest import (
    TICKERS,
    get_cik,
    fetch_submissions,
    list_10k_10q_filings,
    get_mda_for_filing,
)
from chunking import chunk_document
from retrieval import get_client, get_collection, add_chunks
from config import config

logger = logging.getLogger(__name__)


def build_index() -> None:
    client = get_client()
    collection = get_collection(client)

    total_chunks_indexed = 0
    failures = []

    for ticker in TICKERS:
        logger.info("=== %s ===", ticker)
        cik = get_cik(ticker)
        submissions = fetch_submissions(cik)
        filings = list_10k_10q_filings(submissions)[:config.build_filings_per_company]

        for filing in filings:
            accession = filing["accessionNumber"]
            form = filing["form"]
            filing_date = filing["filingDate"]

            try:
                mda_text = get_mda_for_filing(
                    cik, accession, filing["primaryDocument"]
                )
                chunks = chunk_document(mda_text, chunk_size=500, chunk_overlap=50)

                add_chunks(
                    collection,
                    chunks=chunks,
                    ticker=ticker,
                    accession_number=accession,
                    form=form,
                    filing_date=filing_date,
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


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(message)s")
    build_index()