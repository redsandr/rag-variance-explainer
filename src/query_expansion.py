from config import config

FINANCIAL_SYNONYMS = {
    "labor": ["labor", "labour", "payroll", "wage", "wages", "staffing", "employee", "employment", "compensation", "personnel"],
    "cost": ["cost", "costs", "expense", "expenses", "spending", "expenditure"],
    "revenue": ["revenue", "sales", "income", "turnover", "top line"],
    "marketing": ["marketing", "advertising", "media", "promotion", "promotional", "brand"],
    "food": ["food", "ingredient", "supply", "commodity", "beverage", "packaging"],
    "operating": ["operating", "store operating", "opex", "operational", "occupancy"],
    "general": ["general", "administrative", "G&A", "SG&A", "overhead", "corporate"],
    "restaurant": ["restaurant", "restaurants", "dining", "store", "stores", "unit", "units"],
    "comparable": ["comparable", "same-store", "same store", "SRS", "comp", "comps"],
    "sales": ["sales", "revenue", "transaction", "transactions", "volume", "traffic"],
    "margin": ["margin", "profitability", "profit", "profits"],
    "price": ["price", "pricing", "menu price", "inflation", "check average"],
    "wage": ["wage", "wages", "minimum wage", "wage inflation", "pay", "salary"],
    "development": ["development", "opening", "openings", "new store", "expansion", "Chipotlane", "new restaurant", "restaurant count", "new unit"],
    "acquisition": ["acquisition", "acquire", "acquired", "merger", "M&A", "purchase"],
    "change": ["change", "changed", "increase", "decrease", "variance", "fluctuation", "trend", "decline", "growth", "drive"],
    "cost of goods": ["cost of goods", "cogs", "food cost", "cost of sales", "cost of revenue"],
    "segment": ["segment", "division", "brand", "concept", "chain", "segment sales", "segment profit", "segment margin"],
    "quarter": ["quarter", "quarterly", "Q1", "Q2", "Q3", "Q4", "fiscal", "period", "three months"],
    "inventory": ["inventory", "inventory turnover", "inventory management", "inventory levels", "days in inventory", "inventory position"],
    "shrinkage": ["shrinkage", "shrink", "inventory shrink", "lost inventory", "inventory loss"],
    "merchandise": ["merchandise", "merchandising", "product cost", "merchandise cost", "cost of merchandise", "procurement"],
    "ecommerce": ["e-commerce", "ecommerce", "digital", "online", "online sales", "omnichannel", "digital sales", "direct-to-consumer"],
    "supply_chain": ["supply chain", "logistics", "distribution", "warehouse", "fulfillment", "transportation", "freight"],
    "segment_retail": ["segment", "walmart us", "walmart international", "sam's club", "target segment", "retail segment"],
    "store": ["store", "stores", "retail store", "supercenter", "discount store", "location", "retail location"],
    "traffic": ["traffic", "customer traffic", "foot traffic", "customer visits", "transactions", "store traffic"],
    "ticket": ["ticket", "average ticket", "basket size", "average transaction", "units per transaction"],
    "private_label": ["private label", "private brand", "own brand", "exclusive brand", "owned brand"],
    "membership": ["membership", "membership income", "membership fee", "subscription", "sam's club membership"],
    "cannibalization": ["cannibalization", "cannibalize", "store overlap", "market saturation", "sales transfer"],
    "inflation_retail": ["inflation", "price inflation", "cost inflation", "input cost", "commodity cost"],
    "capital_expenditure": ["capex", "capital expenditure", "capital spend", "store remodel", "renovation", "investment"],
    "promotion": ["promotion", "promotional", "markdown", "discount", "price investment", "everyday low price"],
}


def expand_query(query: str, n_extra_terms: int = None) -> str:
    if n_extra_terms is None:
        n_extra_terms = config.expansion_n_terms

    tokens = set(query.lower().split())
    extra = []
    for word, syns in FINANCIAL_SYNONYMS.items():
        if any(t.startswith(word) or word.startswith(t) for t in tokens):
            for s in syns:
                if s not in tokens and s not in extra:
                    extra.append(s)
    return query + " " + " ".join(extra[:n_extra_terms])



