def normalize_text(value):

    if not value:
        return ""

    return (
        value
        .strip()
        .upper()
    )