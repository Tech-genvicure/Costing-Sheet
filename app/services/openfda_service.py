import requests
from app.utils.data_cleaner import normalize_drug_data


BASE_URL = "https://api.fda.gov/drug/label.json"


def get_drug_label(drug_name):

    query = f'?search=openfda.brand_name:"{drug_name}"&limit=1'

    url = BASE_URL + query

    try:
        response = requests.get(url)

        if response.status_code == 200:

            data = response.json()

            results = data.get("results", [])

            if not results:
                return None

            drug = results[0]

            openfda = drug.get("openfda", {})

            return normalize_drug_data(openfda)

        return None

    except Exception as e:
        print("ERROR:", e)
        return None