COUNTRY_REGISTRY = {
    "IS": "Iceland",
    "SK": "Slovakia",
    # "CZ": "Czech Republic",
    # "IT": "Italy",
}

def get_country_config(country_code: str):
    if country_code == "IS":
        from countries.IS import config
        return config
    elif country_code == "SK":
        from countries.SK import config
        return config
    raise ValueError(f"Unknown country: {country_code}")

def get_document_registry(country_code: str):
    if country_code == "IS":
        from countries.IS.document_types import IS_DOCUMENT_REGISTRY
        return IS_DOCUMENT_REGISTRY
    elif country_code == "SK":
        from countries.SK.document_types import SK_DOCUMENT_REGISTRY
        return SK_DOCUMENT_REGISTRY
    raise ValueError(f"Unknown country: {country_code}")
