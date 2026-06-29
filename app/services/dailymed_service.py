import os
import time
import requests # type: ignore

BASE_URL = "https://dailymed.nlm.nih.gov/dailymed/services/v2"

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


# =====================================================
# SEARCH ALL SPL RECORDS
# =====================================================
def search_drug(
    drug_name,
    manufacturer_name=None,
    retries=3
):
    """
    Search DailyMed SPL records.

    If manufacturer_name is provided,
    return only records belonging to
    that manufacturer.

    Otherwise return all records.
    """

    url = (
        f"{BASE_URL}/spls.json"
        f"?drug_name={drug_name}"
    )

    for attempt in range(retries):

        try:

            response = requests.get(
                url,
                headers=HEADERS,
                timeout=20
            )

            response.raise_for_status()

            data = response.json()

            spls = data.get(
                "data",
                []
            )

            if not spls:

                return []

            # =========================================
            # FILTER BY MANUFACTURER
            # =========================================
            if manufacturer_name:

                filtered_spls = []

                for record in spls:

                    labeler = str(
                        record.get(
                            "labeler_name",
                            ""
                        )
                    ).upper()

                    if (
                        manufacturer_name.upper()
                        in labeler
                    ):

                        filtered_spls.append(
                            record
                        )

                return filtered_spls

            # =========================================
            # RETURN ALL RECORDS
            # =========================================
            return spls

        except Exception as e:

            print(
                f"Attempt {attempt + 1} failed: {e}"
            )

            time.sleep(2)

    return []


# =====================================================
# GET UNIQUE MANUFACTURERS
# =====================================================
def get_manufacturers(
    drug_name
):

    records = search_drug(
        drug_name
    )

    manufacturers = []

    for record in records:

        title = record.get(
            "title",
            ""
        )

        company = ""

        if "[" in title and "]" in title:

            company = (
                title
                .split("[")[-1]
                .replace("]", "")
                .strip()
            )

        if (
            company
            and company not in manufacturers
        ):

            manufacturers.append(
                company
            )

    return manufacturers

# =====================================================
# GET RECORD BY MANUFACTURER
# =====================================================
def get_record_by_manufacturer(
    drug_name,
    manufacturer
):

    records = search_drug(
        drug_name
    )

    for record in records:

        title = record.get(
            "title",
            ""
        )

        company = ""

        if "[" in title and "]" in title:

            company = (
                title
                .split("[")[-1]
                .replace("]", "")
                .strip()
            )

        if (
            company.upper()
            ==
            manufacturer.upper()
        ):

            return record

    return None

# =====================================================
# DOWNLOAD SPL XML
# =====================================================
def download_spl_xml(
    setid
):
    """
    Download SPL XML from DailyMed.
    """

    url = (
        f"{BASE_URL}/spls/"
        f"{setid}.xml"
    )

    response = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    os.makedirs(
        "data/raw_dailymed",
        exist_ok=True
    )

    file_path = (
        f"data/raw_dailymed/{setid}.xml"
    )

    with open(
        file_path,
        "wb"
    ) as file:

        file.write(
            response.content
        )

    return file_path


# =====================================================
# OPTIONAL HELPER
# =====================================================
def get_setid_by_manufacturer(
    drug_name,
    manufacturer
):
    """
    Return setid for the selected
    manufacturer.
    """

    record = get_record_by_manufacturer(
        drug_name,
        manufacturer
    )

    if record:

        return record.get(
            "setid"
        )

    return None