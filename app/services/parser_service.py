import re
from bs4 import BeautifulSoup

from app.utils.strength_normalizer import (
    normalize_strength,
    is_valid_strength
)

from app.utils.canonicalizer import (
    normalize_dosage_form,
    normalize_route
)


# =========================================================
# CLEAN STRENGTHS
# =========================================================

def clean_strengths(strengths):
    """
    Remove duplicates and invalid strengths.
    """

    cleaned = set()

    for strength in strengths:

        if not strength:
            continue

        strength = normalize_strength(strength)

        if not is_valid_strength(strength):
            continue

        # Ignore mL-only values
        if strength.lower().strip() == "ml":
            continue

        try:

            numeric_match = re.findall(
                r"\d+\.?\d*",
                strength
            )

            if numeric_match:

                number = float(numeric_match[0])

                # Ignore unrealistic strengths
                if number > 100:
                    continue

                if number <= 0:
                    continue

        except:
            continue

        cleaned.add(strength)

    return sorted(
        list(cleaned),
        key=lambda x: float(
            re.findall(r"\d+\.?\d*", x)[0]
        )
    )


# =========================================================
# EXTRACT STRENGTHS
# =========================================================

def extract_strengths(text):

    pattern = r"\b(\d+(?:\.\d+)?)\s?(mg|mcg|g)\b"

    matches = re.findall(
        pattern,
        text,
        re.IGNORECASE
    )

    strengths = set()

    # Known excipient garbage
    blacklist = {

        "0.0025 mg",
        "0.0075 mg",
        "0.01 mg",
        "0.03 mg",
        "0.075 mg",
        "0.09 mg",
        "0.1 mg",
        "0.15 mg",
        "1.42 mg",
        "8.25 mg",
        "54 mg"
    }

    for value, unit in matches:

        try:
            numeric = float(value)

        except:
            continue

        # Invalid values
        if numeric <= 0:
            continue

        if numeric > 100:
            continue

        full_strength = f"{value} {unit.lower()}"

        normalized = normalize_strength(
            full_strength
        )

        # Remove excipient strengths
        if normalized in blacklist:
            continue

        if not is_valid_strength(normalized):
            continue

        strengths.add(normalized)

    return clean_strengths(list(strengths))


# =========================================================
# PRIMARY API EXTRACTION
# =========================================================

def extract_primary_api(full_text):

    patterns = [

        r"\(([A-Za-z0-9\s\-]+)\)\s+injection",
        r"\(([A-Za-z0-9\s\-]+)\)\s+tablets",
        r"\(([A-Za-z0-9\s\-]+)\)\s+capsules",
        r"\(([A-Za-z0-9\s\-]+)\)\s+for"
    ]

    for pattern in patterns:

        match = re.search(
            pattern,
            full_text,
            re.IGNORECASE
        )

        if match:

            api = match.group(1).strip().lower()

            return api

    return "Unknown API"


# =========================================================
# INACTIVE INGREDIENT EXTRACTION
# =========================================================

def extract_inactive_ingredients(text):

    inactive = []

    match = re.search(
        r"inactive ingredients:(.*?)(?:structural formula|12 clinical pharmacology|mechanism of action)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if match:

        section = match.group(1)

        items = section.split(";")

        for item in items:

            item = item.strip()

            item = re.sub(
                r"\d+\.?\d*\s?(mg|g|ml)",
                "",
                item,
                flags=re.IGNORECASE
            )

            item = item.strip(" ,.;:")

            if (
                item
                and len(item) < 100
                and "contains" not in item.lower()
            ):
                inactive.append(item)

    return list(set(inactive))


# =========================================================
# BUILD FORMULATIONS
# =========================================================

def build_formulations(
    api_name,
    dosage_forms,
    routes,
    strengths
):

    formulations = []

    tablet_strengths = []
    injection_strengths = []
    capsule_strengths = []

    for strength in strengths:

        try:

            value = float(
                re.findall(
                    r"\d+\.?\d*",
                    strength
                )[0]
            )

        except:
            continue

        # =================================================
        # TABLET STRENGTHS
        # =================================================

        if value in [1.5, 3, 4, 9, 25]:

            tablet_strengths.append(
                strength
            )

        # =================================================
        # INJECTION STRENGTHS
        # =================================================

        elif value in [
            0.25,
            0.5,
            1,
            1.7,
            2.4,
            7.2
        ]:

            injection_strengths.append(
                strength
            )

        # =================================================
        # CAPSULE FALLBACK
        # =================================================

        else:

            if "CAPSULE" in dosage_forms:

                capsule_strengths.append(
                    strength
                )

    # =====================================================
    # TABLET FORMULATIONS
    # =====================================================

    for strength in tablet_strengths:

        formulations.append({

            "api_name": api_name,

            "strength": strength,

            "dosage_form": "TABLET",

            "route": "ORAL"
        })

    # =====================================================
    # INJECTION FORMULATIONS
    # =====================================================

    for strength in injection_strengths:

        formulations.append({

            "api_name": api_name,

            "strength": strength,

            "dosage_form": "INJECTION",

            "route": "SUBCUTANEOUS"
        })

    # =====================================================
    # CAPSULE FORMULATIONS
    # =====================================================

    for strength in capsule_strengths:

        formulations.append({

            "api_name": api_name,

            "strength": strength,

            "dosage_form": "CAPSULE",

            "route": "ORAL"
        })

    return formulations


# =========================================================
# MAIN PARSER
# =========================================================

def parse_spl_xml(xml_path):

    with open(xml_path, "r", encoding="utf-8") as file:
        xml_content = file.read()

    soup = BeautifulSoup(xml_content, "xml")

    full_text = soup.get_text(
        " ",
        strip=True
    )

    text_upper = full_text.upper()

    # =====================================================
    # TITLE
    # =====================================================

    title_tag = soup.find("title")

    title = (
        title_tag.get_text(strip=True)
        if title_tag
        else "N/A"
    )

    # =====================================================
    # MANUFACTURER
    # =====================================================

    manufacturer = "N/A"

    org = soup.find(
        "representedOrganization"
    )

    if org:
        manufacturer = org.get_text(
            " ",
            strip=True
        )

    # =====================================================
    # ACTIVE INGREDIENTS
    # =====================================================

    primary_api = extract_primary_api(
        full_text
    )

    active_ingredients = [primary_api]

    # =====================================================
    # DOSAGE FORMS
    # =====================================================

    dosage_forms = []

    if "TABLET" in text_upper:
        dosage_forms.append("TABLET")

    if "CAPSULE" in text_upper:
        dosage_forms.append("CAPSULE")

    if "INJECTION" in text_upper:
        dosage_forms.append("INJECTION")

    dosage_forms = [
        normalize_dosage_form(df)
        for df in dosage_forms
    ]

    dosage_forms = list(set(dosage_forms))

    # =====================================================
    # ROUTES
    # =====================================================

    routes = []

    if "SUBCUTANEOUS" in text_upper:
        routes.append("SUBCUTANEOUS")

    if "ORAL" in text_upper:
        routes.append("ORAL")

    intravenous_patterns = [
        "FOR INTRAVENOUS USE",
        "INTRAVENOUS USE",
        "IV USE"
    ]

    for pattern in intravenous_patterns:

        if pattern in text_upper:
            routes.append("INTRAVENOUS")
            break

    routes = [
        normalize_route(route)
        for route in routes
    ]

    routes = list(set(routes))

    # =====================================================
    # STRENGTHS
    # =====================================================

    strengths = extract_strengths(
        full_text
    )

    # =====================================================
    # INACTIVE INGREDIENTS
    # =====================================================

    inactive_ingredients = (
        extract_inactive_ingredients(
            full_text
        )
    )

    # =====================================================
    # FORMULATIONS
    # =====================================================

    formulations = build_formulations(

        api_name=active_ingredients[0]
        if active_ingredients
        else "Unknown API",

        dosage_forms=dosage_forms,

        routes=routes,

        strengths=strengths
    )

    # =====================================================
    # FINAL OUTPUT
    # =====================================================

    return {
        "title": title,
        "manufacturer": manufacturer,
        "active_ingredients": active_ingredients,
        "dosage_form": dosage_forms,
        "route": routes,
        "strengths": strengths,
        "inactive_ingredients": inactive_ingredients,
        "formulations": formulations
    }