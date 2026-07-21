"""
Shared constants for the RAG pipeline — single source of truth for
ticker names, sectors, and company metadata.

Every file should import from here instead of redefining dicts.
"""

TICKERS: dict[str, str] = {
    "CMG": "Chipotle Mexican Grill",
    "DRI": "Darden Restaurants",
    "CBRL": "Cracker Barrel",
    "WMT": "Walmart",
    "TGT": "Target",
    "JNJ": "Johnson & Johnson",
    "XOM": "Exxon Mobil",
}

SECTORS: dict[str, str] = {
    "CMG": "Restaurant",
    "DRI": "Restaurant",
    "CBRL": "Restaurant",
    "WMT": "Retail",
    "TGT": "Retail",
    "JNJ": "Healthcare",
    "XOM": "Energy",
}

SECTOR_LIST: list[str] = ["Restaurant", "Retail", "Healthcare", "Energy"]

TICKER_OPTIONS: list[str] = [
    "All",
    "CMG (Chipotle)",
    "DRI (Darden)",
    "CBRL (Cracker Barrel)",
    "WMT (Walmart)",
    "TGT (Target)",
    "JNJ (Johnson & Johnson)",
    "XOM (Exxon Mobil)",
]

TICKER_MAP: dict[str, str | None] = {
    "All": None,
    "CMG (Chipotle)": "CMG",
    "DRI (Darden)": "DRI",
    "CBRL (Cracker Barrel)": "CBRL",
    "WMT (Walmart)": "WMT",
    "TGT (Target)": "TGT",
    "JNJ (Johnson & Johnson)": "JNJ",
    "XOM (Exxon Mobil)": "XOM",
}

COMPANY_SHORT: dict[str, str] = {
    "CMG": "Chipotle",
    "DRI": "Darden",
    "CBRL": "Cracker Barrel",
    "WMT": "Walmart",
    "TGT": "Target",
    "JNJ": "Johnson & Johnson",
    "XOM": "Exxon Mobil",
}
