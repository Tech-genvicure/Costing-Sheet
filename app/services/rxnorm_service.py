import requests


BASE_URL = "https://rxnav.nlm.nih.gov/REST/drugs.json"


def get_rxnorm_data(drug_name):

    url = f"{BASE_URL}?name={drug_name}"

    try:

        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            drug_group = data.get("drugGroup", {})

            concept_group = drug_group.get("conceptGroup", [])

            for group in concept_group:

                properties = group.get("conceptProperties")

                if properties:

                    first_drug = properties[0]

                    return {
                        "rxcui": first_drug.get("rxcui", "N/A"),
                        "rxnorm_name": first_drug.get("name", "N/A"),
                        "synonym": first_drug.get("synonym", "N/A"),
                        "tty": first_drug.get("tty", "N/A"),
                    }

        return None

    except Exception as e:

        print("RxNorm Error:", e)

        return None