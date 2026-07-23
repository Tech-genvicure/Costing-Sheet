print("\n========== BUILD DRUG PROFILE ==========")
def build_drug_profile(
    openfda_data=None,
    rxnorm_data=None,
    orangebook_data=None,
    pipeline_data=None
):
    
    print("\n========== BUILD DRUG PROFILE ==========")
    print("OpenFDA:")
    print(openfda_data)

    print("\nRxNorm:")
    print(rxnorm_data)

    print("\nOrange Book:")
    print(orangebook_data)

    print("\nPipeline:")
    print(pipeline_data)

    # ------------------------------------------------
    # DEFAULTS
    # ------------------------------------------------

    openfda_data = openfda_data or {}
    rxnorm_data = rxnorm_data or {}
    orange = pipeline_data.get(
        "orange_book",
        {}
    )
    pipeline_data = pipeline_data or {}

    parsed = pipeline_data.get("parsed_data", {})

    # ------------------------------------------------
    # BRAND
    # ------------------------------------------------

    brand_name = openfda_data.get(
        "brand_name"
    )

    if not brand_name:

        synonym = rxnorm_data.get(
            "synonym"
        )

        if synonym:

            brand_name = synonym.split()[0]

    if not brand_name:

        brand_name = "N/A"

    # ------------------------------------------------
    # GENERIC
    # ------------------------------------------------

    generic = parsed.get(
        "active_ingredients",
        []
    )

    if generic:

        generic_name = ", ".join(

            x.title()

            for x in generic

        )

    else:

        generic_name = openfda_data.get(
            "generic_name",
            "N/A"
        )

    # ------------------------------------------------
    # MANUFACTURER
    # ------------------------------------------------

    # Keep OpenFDA manufacturer
    manufacturer = openfda_data.get(
        "manufacturer_name",
        "N/A"
    )

    # ------------------------------------------------
    # DOSAGE FORM
    # ------------------------------------------------

    dosage_forms = parsed.get(
        "dosage_form",
        []
    )

    if dosage_forms:
        dosage_form = ", ".join(dosage_forms)
    else:
        dosage_form = "N/A"

    # ------------------------------------------------
    # ROUTE
    # ------------------------------------------------

    routes = parsed.get(
        "route",
        []
    )

    if routes:
        route = ", ".join(routes)
    else:
        route = openfda_data.get(
            "route",
            "N/A"
        )

    # ------------------------------------------------
    # SUBSTANCE
    # ------------------------------------------------

    substance = ", ".join(
        x.title()
        for x in generic
    )

    # ------------------------------------------------
    # RETURN
    # ------------------------------------------------

    return {

        "overview": {

            "brand_name": brand_name,

            "generic_name": generic_name,

            "manufacturer": manufacturer,

            "dosage_form": dosage_form,

            "route": route
        },

        "clinical": {

            "substance_name": substance
        },

        "regulatory": {

            "status": "Approved",

            "source": "DailyMed"
        },

        "rxnorm": {

            "rxcui": rxnorm_data.get(
                "rxcui",
                "N/A"
            ),

            "rxnorm_name": rxnorm_data.get(
                "rxnorm_name",
                "N/A"
            ),

            "tty": rxnorm_data.get(
                "tty",
                "N/A"
            )
        },

        "orangebook": {

            "application_no": orange.get("application_number","N/A"),

            "patent_count": orange.get("patent_count",0),

            "exclusivity_count": orange.get("exclusivity_count",0),

            "latest_patent_expiry": orange.get("latest_patent_expiry","N/A"),

            "latest_exclusivity": orange.get("latest_exclusivity","N/A"),

            "patent_risk": orange.get("patent_risk","LOW")
        },

        "portfolio": {

            "market_potential": "8.4 / 10",

            "competition": "Moderate",

            "patent_risk": orange.get(
                "patent_risk",
                "LOW"
            )
        }
    }


