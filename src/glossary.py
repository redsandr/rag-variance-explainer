GLOSSARY = {
    "revenue": {
        "CMG": ["Revenues"],
        "DRI": ["RevenueFromContractWithCustomerExcludingAssessedTax"],
        "CBRL": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax"],
    },
    "cogs": {
        "CMG": None,  # not a single tag — must sum Food/Labor/Occupancy components
        "DRI": ["CostOfGoodsAndServicesSold"],
        "CBRL": ["CostOfGoodsAndServicesSold"],
    },
    "sga": {
        "CMG": ["GeneralAndAdministrativeExpense"],
        "DRI": ["SellingGeneralAndAdministrativeExpense", "GeneralAndAdministrativeExpense"],
        "CBRL": ["GeneralAndAdministrativeExpense"],
    },
    "marketing": {
        "CMG": ["MarketingAndAdvertisingExpense"],
        "DRI": ["MarketingExpense"],
        "CBRL": None,  # not separately tagged
    },
    "operating_income": {
        "CMG": ["OperatingIncomeLoss"],
        "DRI": ["OperatingIncomeLoss"],
        "CBRL": ["OperatingIncomeLoss"],
    },
}