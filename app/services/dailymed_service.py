import os
import time
import requests # type: ignore
from urllib.parse import quote

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

    drug_name = drug_name.strip()

    url = (
        f"{BASE_URL}/spls.json"
        f"?drug_name={quote(drug_name)}"
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

                    if manufacturer_name.upper() in labeler:

                        filtered_spls.append(record)

                return filtered_spls

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
from requests.exceptions import (
    ChunkedEncodingError,
    ConnectionError,
    Timeout,
)


def download_spl_xml(setid, retries=3):

    os.makedirs(
        "data/raw_dailymed",
        exist_ok=True
    )

    file_path = (
        f"data/raw_dailymed/{setid}.xml"
    )

    # -----------------------------------------
    # Use cached file if already downloaded
    # -----------------------------------------
    if (
        os.path.exists(file_path)
        and
        os.path.getsize(file_path) > 0
    ):
        print(f"Using cached XML: {setid}")
        return file_path

    url = (
        f"{BASE_URL}/spls/{setid}.xml"
    )

    # -----------------------------------------
    # Retry download
    # -----------------------------------------
    for attempt in range(retries):

        try:

            print(
                f"Downloading XML ({attempt+1}/{retries})..."
            )

            with requests.get(
                url,
                headers=HEADERS,
                timeout=120,
                stream=True
            ) as response:

                response.raise_for_status()

                with open(
                    file_path,
                    "wb"
                ) as file:

                    for chunk in response.iter_content(
                        chunk_size=8192
                    ):

                        if chunk:

                            file.write(chunk)

            # -----------------------------------------
            # Validate download
            # -----------------------------------------
            if (
                os.path.exists(file_path)
                and
                os.path.getsize(file_path) > 0
            ):

                print("XML downloaded successfully.")

                return file_path

        except (
            ChunkedEncodingError,
            ConnectionError,
            Timeout,
            requests.RequestException,
        ) as e:

            print(
                f"Download failed ({attempt+1}/{retries})"
            )
            print(e)

            # Delete incomplete file
            if os.path.exists(file_path):

                os.remove(file_path)

            time.sleep(2 ** attempt)

    raise RuntimeError(
        f"Failed to download SPL XML for {setid}"
    )


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