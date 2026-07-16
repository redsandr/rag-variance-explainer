"""
SEC EDGAR data fetchers.

SEC requires a descriptive User-Agent on every request (not optional —
requests without one get rejected). Replace the placeholder below with
your actual name/email before running anything.
"""

import requests
import time
from bs4 import BeautifulSoup
import re

HEADERS = {"User-Agent": "Sebas (your@email.com)"}

TICKERS = {
    "CMG": "Chipotle Mexican Grill",
    "DRI": "Darden Restaurants",
    "CBRL": "Cracker Barrel",
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
    """Fetch raw HTML of a filing document."""
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    time.sleep(0.15)
    return response.text


def _find_mda_start(text: str) -> re.Match | None:
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

    return best_match


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


def extract_mda_section(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    _convert_tables_to_text(soup)
    text = soup.get_text(separator="\n")

    start_match = _find_mda_start(text)

    end_pattern = re.compile(r"^[ \t]*Item\s+\d+[A]?\.", re.IGNORECASE | re.MULTILINE)
    end_match = end_pattern.search(text, pos=start_match.end())
    end_pos = end_match.start() if end_match else len(text)

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
    url = "https://www.sec.gov/files/company_tickers.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    data = response.json()

    ticker_upper = ticker.upper()
    for entry in data.values():
        if entry["ticker"] == ticker_upper:
            return str(entry["cik_str"]).zfill(10)

    raise ValueError(f"Ticker {ticker} not found in SEC ticker file")

def fetch_companyfacts(cik: str) -> dict:
    """Fetch all XBRL-tagged facts for a company."""
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    time.sleep(0.15)  # stay comfortably under SEC's 10 req/sec cap
    return response.json()


def fetch_submissions(cik: str) -> dict:
    """Fetch filing history/metadata (accession numbers, forms, dates)."""
    url = f"https://data.sec.gov/submissions/CIK{cik}.json"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    time.sleep(0.15)
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


