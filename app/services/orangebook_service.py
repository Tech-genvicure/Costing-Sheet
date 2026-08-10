from datetime import datetime


def extract_latest_patent_expiry(patents):

    dates = []

    for patent in patents:

        expiry = patent.get(
            "Patent_Expire_Date_Text"
        )

        if not expiry:
            continue

        try:

            parsed = datetime.strptime(
                expiry,
                "%b %d, %Y"
            )

            dates.append(parsed)

        except:
            continue

    if not dates:
        return None

    latest = max(dates)

    return latest.strftime("%Y-%m-%d")


def extract_latest_exclusivity(exclusivities):

    dates = []

    for item in exclusivities:

        expiry = item.get(
            "Exclusivity_Date"
        )

        if not expiry:
            continue

        try:

            parsed = datetime.strptime(
                expiry,
                "%b %d, %Y"
            )

            dates.append(parsed)

        except:
            continue

    if not dates:
        return None

    latest = max(dates)

    return latest.strftime("%Y-%m-%d")


def calculate_patent_risk(
    patent_count,
    exclusivity_count
):

    score = 0

    if patent_count >= 20:
        score += 50

    elif patent_count >= 10:
        score += 30

    elif patent_count > 0:
        score += 15

    if exclusivity_count > 0:
        score += 30

    if score >= 70:
        return "HIGH"

    if score >= 40:
        return "MEDIUM"

    return "LOW"


def build_commercial_summary_from_profile(profile):

    if not profile:
        return None

    patents = profile.get(
        "patents",
        []
    )

    exclusivities = profile.get(
        "exclusivities",
        []
    )

    latest_patent_expiry = (
        extract_latest_patent_expiry(
            patents
        )
    )

    latest_exclusivity = (
        extract_latest_exclusivity(
            exclusivities
        )
    )

    patent_count = len(patents)

    exclusivity_count = len(exclusivities)

    patent_risk = calculate_patent_risk(
        patent_count,
        exclusivity_count
    )

    return {

        "application_number":
            profile.get(
                "application_no"
            ),

        "patent_count":
            patent_count,

        "exclusivity_count":
            exclusivity_count,

        "latest_patent_expiry":
            latest_patent_expiry,

        "latest_exclusivity":
            latest_exclusivity,

        "patent_risk":
            patent_risk
    }