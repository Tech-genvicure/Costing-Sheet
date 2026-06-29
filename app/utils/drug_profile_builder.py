def build_drug_profile(
    openfda_data,
    rxnorm_data=None,
    orangebook_data=None,
    pipeline_data=None
):

    # ------------------------------------------------
    # DEFAULT VALUES
    # ------------------------------------------------
    manufacturer = openfda_data.get(
        "manufacturer_name",
        "N/A"
    )

    dosage_form = "N/A"

    route = openfda_data.get(
        "route",
        "N/A"
    )

    # ------------------------------------------------
    # USE PARSED SPL DATA IF AVAILABLE
    # ------------------------------------------------
    if pipeline_data:

        parsed_data = pipeline_data.get(
            "parsed_data",
            {}
        )

        manufacturer = parsed_data.get(
            "manufacturer",
            manufacturer
        )

        formulations = parsed_data.get(
            "formulations",
            []
        )

        if formulations:

            dosage_forms = list(set(

                f.get("dosage_form")

                for f in formulations

                if f.get("dosage_form")

            ))

            routes = list(set(

                f.get("route")

                for f in formulations

                if f.get("route")

            ))

            if dosage_forms:

                dosage_form = ", ".join(
                    dosage_forms
                )

            if routes:

                route = ", ".join(
                    routes
                )

    return {

        # ------------------------------------------------
        # OVERVIEW
        # ------------------------------------------------
        "overview": {

            "brand_name": openfda_data.get(
                "brand_name",
                "N/A"
            ),

            "generic_name": openfda_data.get(
                "generic_name",
                "N/A"
            ),

            "manufacturer": manufacturer,

            "dosage_form": dosage_form,

            "route": route,
        },

        # ------------------------------------------------
        # CLINICAL
        # ------------------------------------------------
        "clinical": {

            "substance_name": openfda_data.get(
                "substance_name",
                "N/A"
            ),
        },

        # ------------------------------------------------
        # REGULATORY
        # ------------------------------------------------
        "regulatory": {

            "status": "Approved",

            "source": "OpenFDA"
        },

        # ------------------------------------------------
        # RXNORM
        # ------------------------------------------------
        "rxnorm": {

            "rxcui": (
                rxnorm_data.get(
                    "rxcui",
                    "N/A"
                )
                if rxnorm_data else "N/A"
            ),

            "rxnorm_name": (
                rxnorm_data.get(
                    "rxnorm_name",
                    "N/A"
                )
                if rxnorm_data else "N/A"
            ),

            "tty": (
                rxnorm_data.get(
                    "tty",
                    "N/A"
                )
                if rxnorm_data else "N/A"
            )
        },

        # ------------------------------------------------
        # ORANGE BOOK
        # ------------------------------------------------
        "orangebook": {

            "application_no": (
                orangebook_data.get(
                    "application_number",
                    "N/A"
                )
                if orangebook_data else "N/A"
            ),

            "patent_count": (
                orangebook_data.get(
                    "patent_count",
                    "N/A"
                )
                if orangebook_data else "N/A"
            ),

            "exclusivity_count": (
                orangebook_data.get(
                    "exclusivity_count",
                    "N/A"
                )
                if orangebook_data else "N/A"
            ),

            "latest_patent_expiry": (
                orangebook_data.get(
                    "latest_patent_expiry",
                    "N/A"
                )
                if orangebook_data else "N/A"
            ),

            "latest_exclusivity": (
                orangebook_data.get(
                    "latest_exclusivity",
                    "N/A"
                )
                if orangebook_data else "N/A"
            ),

            "patent_risk": (
                orangebook_data.get(
                    "patent_risk",
                    "N/A"
                )
                if orangebook_data else "N/A"
            )
        },

        # ------------------------------------------------
        # PORTFOLIO INTELLIGENCE
        # ------------------------------------------------
        "portfolio": {

            "market_potential": "8.4 / 10",

            "competition": "Moderate",

            "patent_risk": (
                orangebook_data.get(
                    "patent_risk",
                    "N/A"
                )
                if orangebook_data else "N/A"
            )
        }
    }