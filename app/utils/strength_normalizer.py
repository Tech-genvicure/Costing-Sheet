import re


VALID_UNITS = [
    "mg",
    "mcg",
    "g",
    "mL",
    "units"
]


def clean_strength(strength_text):
    """
    Clean raw strength text.
    """

    if not strength_text:
        return None

    strength_text = strength_text.strip()

    # Remove duplicate spaces
    strength_text = re.sub(r"\s+", " ", strength_text)

    return strength_text


def is_valid_strength(strength_text):
    """
    Validate whether extracted text is a real strength.
    """

    if not strength_text:
        return False

    strength_text = strength_text.lower()

    # Must contain numeric value
    if not re.search(r"\d", strength_text):
        return False

    # Must contain valid pharma unit
    if not any(unit.lower() in strength_text for unit in VALID_UNITS):
        return False

    # Reject obvious garbage
    garbage_patterns = [
        "inactive",
        "preservative",
        "flavor",
        "color",
        "water",
        "qs",
        "hydrochloric acid",
        "sodium hydroxide"
    ]

    for pattern in garbage_patterns:
        if pattern in strength_text:
            return False

    return True


def normalize_strength(strength_text):
    """
    Normalize common pharma strength formats.
    """

    if not strength_text:
        return None

    strength_text = clean_strength(strength_text)

    # Normalize units
    replacements = {
        "milligram": "mg",
        "milligrams": "mg",
        "microgram": "mcg",
        "micrograms": "mcg",
        "gram": "g",
        "grams": "g",
        "milliliter": "mL",
        "milliliters": "mL"
    }

    normalized = strength_text

    for old, new in replacements.items():
        normalized = re.sub(
            old,
            new,
            normalized,
            flags=re.IGNORECASE
        )

    # Standard spacing
    normalized = re.sub(r"\s*/\s*", "/", normalized)
    normalized = re.sub(r"\s+", " ", normalized)

    return normalized.strip()


def extract_numeric_strength(strength_text):
    """
    Extract numeric portion from strength.
    """

    if not strength_text:
        return None

    match = re.search(r"(\d+\.?\d*)", strength_text)

    if match:
        return float(match.group(1))

    return None


def build_strength_record(strength_text):
    """
    Build structured strength object.
    """

    if not is_valid_strength(strength_text):
        return None

    normalized = normalize_strength(strength_text)

    return {
        "raw_strength": strength_text,
        "normalized_strength": normalized,
        "numeric_value": extract_numeric_strength(normalized)
    }