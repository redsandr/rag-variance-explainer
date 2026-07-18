"""
SEC EDGAR data fetchers.

SEC requires a descriptive User-Agent on every request (not optional —
requests without one get rejected). Replace the placeholder below with
your actual name/email before running anything.
"""

import logging
import os
import re
import time
from typing import cast

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import config

logger = logging.getLogger(__name__)

HEADERS = {"User-Agent": config.sec_user_agent}

_SESSION = requests.Session()
_SESSION.headers.update(HEADERS)
retry_strategy = Retry(
    total=5,
    backoff_factor=1.0,
    status_forcelist=[429, 500, 502, 503, 504],
    allowed_methods=["GET"],
    raise_on_status=False,
)
_SESSION.mount("https://", HTTPAdapter(max_retries=retry_strategy))

SEC_REQUEST_DELAY = float(os.getenv("SEC_REQUEST_DELAY", "0.2"))
_LAST_REQUEST_TIME = 0.0


def _rate_limited_get(url: str, max_retries: int = 5, base_delay: float = 5.0) -> requests.Response:
    """Fetch *url* with rate limiting, retry on 429 and transient errors.

    - Enforces minimum *SEC_REQUEST_DELAY* between requests (SEC mandate).
    - Retries on 429 (respecting Retry-After header) and connection errors
      (timeout, DNS, reset) with exponential backoff, up to *max_retries*.
    - Applies 30 s connection / 60 s read timeout to prevent hangs.
    """
    global _LAST_REQUEST_TIME
    last_exception = None
    for attempt in range(1, max_retries + 1):
        try:
            elapsed = time.time() - _LAST_REQUEST_TIME
            if elapsed < SEC_REQUEST_DELAY:
                time.sleep(SEC_REQUEST_DELAY - elapsed)
            response = _SESSION.get(url, timeout=(30, 60))
            _LAST_REQUEST_TIME = time.time()
            if response.status_code == 429:
                wait = int(response.headers.get("Retry-After", str(base_delay)))
                logger.warning(
                    "SEC rate limited (429). Attempt %d/%d. Waiting %ds...",
                    attempt, max_retries, wait,
                )
                time.sleep(wait)
                continue
            response.raise_for_status()
            return response
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError) as e:
            last_exception = e
            if attempt < max_retries:
                delay = base_delay * (2 ** (attempt - 1))
                logger.warning(
                    "SEC request failed (attempt %d/%d): %s. Retrying in %.1fs...",
                    attempt, max_retries, e, delay,
                )
                time.sleep(delay)
            continue
    raise RuntimeError(
        f"SEC request failed after {max_retries} attempts. Last error: {last_exception}"
    ) from last_exception

TICKERS = {
    "CMG": "Chipotle Mexican Grill",
    "DRI": "Darden Restaurants",
    "CBRL": "Cracker Barrel",
    "WMT": "Walmart",
    "TGT": "Target",
    "JNJ": "Johnson & Johnson",
    "XOM": "Exxon Mobil",
}

CANDIDATE_TAGS = [
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "CostOfGoodsAndServicesSold",
    "CostOfRevenue",
    "SellingGeneralAndAdministrativeExpense",
    "GeneralAndAdministrativeExpense",
    "MarketingExpense",
    "OperatingIncomeLoss",
]




### FETCHING ###

def fetch_filing_html(url: str) -> str:
    """Fetch raw HTML of a filing document with rate limiting and retry."""
    response = _rate_limited_get(url)
    return response.text


def _find_mda_start(text: str) -> re.Match[str]:
    heading_pattern = re.compile(
        r"Item\s+\d+[A]?\.\s*Management.{0,3}s\s+Discussion\s+and\s+Analysis",
        re.IGNORECASE,
    )
    item_pattern = re.compile(r"^[ \t]*Item\s+\d+[A]?\.", re.IGNORECASE | re.MULTILINE)

    candidates = list(heading_pattern.finditer(text))
    if not candidates:
        raise ValueError("Could not locate MD&A heading in filing")

    best_match, best_gap = None, -1
    for m in candidates:
        next_item = item_pattern.search(text, pos=m.end())
        gap = (next_item.start() if next_item else len(text)) - m.end()
        if gap > best_gap:
            best_gap = gap
            best_match = m

    return cast("re.Match[str]", best_match)


def _convert_tables_to_text(soup: BeautifulSoup) -> None:
    """Join table row cells so numbers stay with their labels.

    SEC filing HTML uses one <td> per token for visual alignment. When
    get_text() flattens this, each token lands on its own orphaned line
    (e.g. "Revenue", "$", "3,072", "$", "2,859"). This function replaces
    each <table> with a <div> that joins cells within each row so they
    stay together as "Revenue $ 3,072 $ 2,859", giving the embedding
    model the column context it needs.
    """
    for table in soup.find_all('table'):
        row_texts = []
        for row in table.find_all('tr'):
            cells = row.find_all(['th', 'td'])
            parts = [c.get_text(strip=True) for c in cells if c.get_text(strip=True)]
            if parts:
                row_texts.append(" ".join(parts))

        if row_texts:
            table_text = "\n".join(row_texts)
            new_div = soup.new_tag('div')
            new_div.string = table_text
            table.replace_with(new_div)


def _parse_item_num(item_text: str) -> float:
    m = re.match(r"^[ \t]*Item\s+(\d+)[A-Z]?\.", item_text, re.IGNORECASE)
    return float(m.group(1)) if m else 0


def extract_mda_section(html: str) -> str:
    """Extract the Management's Discussion & Analysis section from SEC HTML.

    Parses the SEC filing HTML, converts tables to readable text, then
    locates the MD&A heading and extracts all text up to the next Item
    heading. Returns clean, minimally-formatted text ready for chunking.
    """
    soup = BeautifulSoup(html, "html.parser")
    _convert_tables_to_text(soup)
    text = soup.get_text(separator="\n")

    start_match = _find_mda_start(text)
    mda_item_num = _parse_item_num(text[start_match.start():])

    end_pattern = re.compile(r"^[ \t]*Item\s+\d+[A-Z]?\.", re.IGNORECASE | re.MULTILINE)
    end_pos = len(text)
    for m in end_pattern.finditer(text, pos=start_match.end()):
        if _parse_item_num(m.group()) >= mda_item_num:
            # Skip matches inside quotes (e.g. "see Item 5." references within narrative)
            preceding = text[max(0, m.start()-30):m.start()].strip()
            if preceding and preceding[-1] in ('"', '\u201c', '\u201d', '\u201e', '\u201f'):
                continue
            end_pos = m.start()
            break

    def _clean_text(text: str) -> str:
        text = text.replace("\u200b", "")
        text = text.replace("\xa0", " ")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    return _clean_text(text[start_match.start():end_pos])


def get_mda_for_filing(cik: str, accession_number: str, primary_document: str) -> str:
    """Convenience wrapper: fetch a filing and extract just its MD&A text."""
    url = filing_document_url(cik, accession_number, primary_document)
    html = fetch_filing_html(url)
    return extract_mda_section(html)


def get_cik(ticker: str) -> str:
    response = _rate_limited_get("https://www.sec.gov/files/company_tickers.json")
    data = response.json()

    ticker_upper = ticker.upper()
    for entry in data.values():
        if entry["ticker"] == ticker_upper:
            return str(entry["cik_str"]).zfill(10)

    raise ValueError(f"Ticker {ticker} not found in SEC ticker file")

def fetch_companyfacts(cik: str) -> dict:
    """Fetch all XBRL-tagged facts for a company."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = _rate_limited_get(url)
    return response.json()


def fetch_submissions(cik: str) -> dict:
    """Fetch filing history/metadata (accession numbers, forms, dates)."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = _rate_limited_get(url)
    return response.json()


def list_10k_10q_filings(submissions: dict) -> list[dict]:
    """
    Extract just the 10-K/10-Q filings from a submissions payload,
    as a list of {accessionNumber, form, filingDate, primaryDocument}.
    """
    recent = submissions["filings"]["recent"]
    results = []
    for i, form in enumerate(recent["form"]):
        if form in ("10-K", "10-Q"):
            results.append({
                "accessionNumber": recent["accessionNumber"][i],
                "form": form,
                "filingDate": recent["filingDate"][i],
                "primaryDocument": recent["primaryDocument"][i],
            })
    return results


def filing_document_url(cik: str, accession_number: str, primary_document: str) -> str:
    """
    Build the URL to the main filing HTML document, given a CIK,
    accession number (with dashes, as returned by submissions API),
    and primary document filename.
    """
    accession_no_dashes = accession_number.replace("-", "")
    cik_no_padding = str(int(cik))  # Archives URLs use unpadded CIK
    return (
        f"https://www.sec.gov/Archives/edgar/data/"
        f"{cik_no_padding}/{accession_no_dashes}/{primary_document}"
    )


