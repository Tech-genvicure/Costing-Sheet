def clean_value(value):

    if not value:
        return "N/A"

    if isinstance(value, list):
        value = value[0]

    return str(value).title()


def normalize_drug_data(openfda):

    return {
        "brand_name": clean_value(openfda.get("brand_name")),
        "generic_name": clean_value(openfda.get("generic_name")),
        "manufacturer_name": clean_value(openfda.get("manufacturer_name")),
        "dosage_form": clean_value(openfda.get("dosage_form")),
        "route": clean_value(openfda.get("route")),
        "substance_name": clean_value(openfda.get("substance_name")),
    }