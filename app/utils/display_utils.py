"""
display_utils.py

Utility functions for converting raw FDA database values into
business-friendly values for the Streamlit UI.
"""

# ==========================================================
# DOSAGE FORM DISPLAY MAP
# ==========================================================

DOSAGE_FORM_MAP = {

    # Injectables
    ("SOLUTION", "SUBCUTANEOUS"): "Injection",
    ("SOLUTION", "INTRAVENOUS"): "Injection",
    ("SOLUTION", "INTRAMUSCULAR"): "Injection",
    ("SOLUTION", "INTRADERMAL"): "Injection",

    # Oral
    ("TABLET", "ORAL"): "Tablet",
    ("CAPSULE", "ORAL"): "Capsule",
    ("SUSPENSION", "ORAL"): "Oral Suspension",
    ("SOLUTION", "ORAL"): "Oral Solution",
    ("POWDER", "ORAL"): "Powder",

    # Topical
    ("CREAM", "TOPICAL"): "Cream",
    ("GEL", "TOPICAL"): "Gel",
    ("OINTMENT", "TOPICAL"): "Ointment",
    ("LOTION", "TOPICAL"): "Lotion",

    # Nasal
    ("SPRAY", "NASAL"): "Nasal Spray",

    # Oral Spray
    ("SPRAY", "ORAL"): "Oral Spray",

    # Ophthalmic
    ("SOLUTION", "OPHTHALMIC"): "Eye Drops",

    # Otic
    ("SOLUTION", "OTIC"): "Ear Drops",

    # Pulmonary
    ("AEROSOL", "RESPIRATORY"): "Inhaler",
    ("POWDER", "RESPIRATORY"): "Dry Powder Inhaler",

}


# ==========================================================
# MARKETING STATUS
# ==========================================================

MARKETING_STATUS_MAP = {

    1: "Prescription Drug",
    2: "Over-the-Counter (OTC)",
    3: "Discontinued",
    4: "Tentative Approval",

}


# ==========================================================
# PATENT RISK COLOR
# (Useful later for colored badges/charts)
# ==========================================================

PATENT_RISK_COLOR = {

    "LOW": "green",
    "MEDIUM": "orange",
    "HIGH": "red",

}


# ==========================================================
# PRODUCT DETAILS
# ==========================================================

def extract_product_details(product: dict) -> dict:
    """
    Converts FDA product information into
    UI-friendly dosage form and route.

    Example:
    FDA:
        Form = "SOLUTION;SUBCUTANEOUS"

    Returns:
        {
            "dosage_form": "Injection",
            "route": "Subcutaneous"
        }
    """

    if not product:

        return {

            "dosage_form": "N/A",

            "route": "N/A"

        }

    form = product.get("Form", "")

    if ";" in form:

        dosage_form, route = form.split(";", 1)

    else:

        dosage_form = form

        route = "N/A"

    dosage_form = dosage_form.strip().upper()

    route = route.strip().upper()

    display_form = DOSAGE_FORM_MAP.get(

        (dosage_form, route),

        dosage_form.title()

    )

    return {

        "dosage_form": display_form,

        "route": route.title()

    }


# ==========================================================
# MARKETING STATUS
# ==========================================================

def get_marketing_status(profile: dict) -> str:
    """
    Converts FDA MarketingStatusID
    into a readable label.
    """

    marketing = profile.get("marketing_status", {})

    status_id = marketing.get("MarketingStatusID")

    return MARKETING_STATUS_MAP.get(

        status_id,

        "Unknown"

    )


# ==========================================================
# FIRST PRODUCT
# ==========================================================

def get_first_product(profile: dict) -> dict:
    """
    Safely returns the first FDA product.
    """

    products = profile.get("products", [])

    if products:

        return products[0]

    return {}


# ==========================================================
# STRENGTHS
# ==========================================================

def format_strengths(profile: dict) -> str:
    """
    Converts strengths list into a display string.
    """

    strengths = profile.get("strengths", [])

    if not strengths:

        return "N/A"

    return ", ".join(strengths)


# ==========================================================
# PATENT SUMMARY
# ==========================================================

def get_patent_summary(profile: dict) -> dict:
    """
    Returns patent statistics.
    """

    patents = profile.get("patents", [])

    exclusivities = profile.get("exclusivities", [])

    return {

        "patent_count": len(patents),

        "exclusivity_count": len(exclusivities)

    }


# ==========================================================
# APPLICANT
# ==========================================================

def get_manufacturer(profile: dict) -> str:
    """
    Returns manufacturer short name.
    """

    applicant = profile.get("applicant", {})

    return applicant.get(

        "short_name",

        "N/A"

    )