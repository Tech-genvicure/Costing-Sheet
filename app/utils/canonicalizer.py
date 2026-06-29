# =========================================================
# DOSAGE FORM MAPPING
# =========================================================

DOSAGE_FORM_MAP = {

    "TABLET": "TABLET",
    "TABLETS": "TABLET",

    "CAPSULE": "CAPSULE",
    "CAPSULES": "CAPSULE",

    "INJECTION": "INJECTION",
    "INJECTABLE": "INJECTION",
    "SOLUTION FOR INJECTION": "INJECTION",

    "SOLUTION": "SOLUTION",
    "SUSPENSION": "SUSPENSION",

    "CREAM": "CREAM",
    "OINTMENT": "OINTMENT",

    "PATCH": "PATCH"
}


# =========================================================
# ROUTE MAPPING
# =========================================================

ROUTE_MAP = {

    "ORAL": "ORAL",

    "SUBCUTANEOUS": "SUBCUTANEOUS",
    "SUBCUT": "SUBCUTANEOUS",

    "INTRAVENOUS": "INTRAVENOUS",
    "IV": "INTRAVENOUS",

    "TOPICAL": "TOPICAL",

    "INHALATION": "INHALATION"
}


# =========================================================
# NORMALIZE DOSAGE FORM
# =========================================================

def normalize_dosage_form(value):

    if not value:
        return "UNKNOWN"

    value = value.upper().strip()

    for key, normalized in DOSAGE_FORM_MAP.items():

        if key in value:
            return normalized

    return value


# =========================================================
# NORMALIZE ROUTE
# =========================================================

def normalize_route(value):

    if not value:
        return "UNKNOWN"

    value = value.upper().strip()

    for key, normalized in ROUTE_MAP.items():

        if key in value:
            return normalized

    return value