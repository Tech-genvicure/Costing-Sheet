import pandas as pd
import os


ORANGE_BOOK_DIR = "data/orangebook"

PRODUCT_FILE = os.path.join(
    ORANGE_BOOK_DIR,
    "products.txt"
)

PATENT_FILE = os.path.join(
    ORANGE_BOOK_DIR,
    "patent.txt"
)

EXCLUSIVITY_FILE = os.path.join(
    ORANGE_BOOK_DIR,
    "exclusivity.txt"
)


def load_products():

    return pd.read_csv(
        PRODUCT_FILE,
        sep="~",
        dtype=str
    )


def load_patents():

    return pd.read_csv(
        PATENT_FILE,
        sep="~",
        dtype=str
    )


def load_exclusivities():

    return pd.read_csv(
        EXCLUSIVITY_FILE,
        sep="~",
        dtype=str
    )


def search_orange_book(drug_name):

    products = load_products()

    matches = products[
        products["Trade_Name"]
        .str.upper()
        .str.contains(
            drug_name.upper(),
            na=False
        )
    ]

    return matches.to_dict(
        orient="records"
    )


def get_patents(app_no):

    patents = load_patents()

    matches = patents[
        patents["Appl_No"] == str(app_no)
    ]

    return matches.to_dict(
        orient="records"
    )


def get_exclusivities(app_no):

    exclusivities = load_exclusivities()

    matches = exclusivities[
        exclusivities["Appl_No"] == str(app_no)
    ]

    return matches.to_dict(
        orient="records"
    )


def build_orange_book_summary(drug_name):

    products = search_orange_book(
        drug_name
    )

    if not products:
        return None

    primary = products[0]

    app_no = primary.get("Appl_No")

    patents = get_patents(app_no)

    exclusivities = get_exclusivities(app_no)

    return {
        "application_number": app_no,
        "product": primary,
        "patents": patents,
        "exclusivities": exclusivities,
        "patent_count": len(patents),
        "exclusivity_count": len(exclusivities)
    }

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



def build_commercial_summary(
    orange_book_data
):

    if not orange_book_data:
        return None

    patents = orange_book_data.get(
        "patents",
        []
    )

    exclusivities = orange_book_data.get(
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

    risk = calculate_patent_risk(
        patent_count,
        exclusivity_count
    )

    return {

        "application_number":
            orange_book_data.get(
                "application_number"
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
            risk
    }