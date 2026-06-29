import streamlit as st # type: ignore

from app.services.dailymed_service import (
    search_drug,
    download_spl_xml
)

from app.services.parser_service import (
    parse_spl_xml
)

from app.services.formulation_service import (
    save_parsed_formulations
)

from app.services.product_service import (
    save_product
)

from app.services.scoring_service import (
    build_intelligence_summary
)

from app.services.orangebook_service import (
    build_orange_book_summary,
    build_commercial_summary
)

from app.services.opportunity_service import (
    build_opportunity_summary
)


def process_drug(
    drug_name,
    manufacturer_name=None,
    records=None
):

    print(f"\nProcessing drug: {drug_name}")

    # =====================================================
    # STEP 1 — SEARCH DAILYMED
    # =====================================================

    if records is None:

        records = search_drug(
            drug_name
        )

    if not records:

        print("No SPL records found.")

        return None


    # =====================================================
    # FILTER BY MANUFACTURER
    # =====================================================

    if manufacturer_name:

        selected_record = None

        for record in records:

            title = record.get(
                "title",
                ""
            )

            manufacturer = ""

            if "[" in title and "]" in title:

                manufacturer = (
                    title
                    .split("[")[-1]
                    .replace("]", "")
                    .strip()
                )

            if (

                manufacturer.upper()

                ==

                manufacturer_name.upper()

            ):

                selected_record = record

                break

        if selected_record:

            result = selected_record

        else:

            print(
                "Manufacturer not found."
            )

            return None

    else:

        result = records[0]


    print("\nSEARCH RESULT:\n")

    print(result)

    setid = result["setid"]
    # =====================================================
    # CACHE KEY
    # =====================================================

    cache_key = (
        drug_name.upper(),
        manufacturer_name
    )

    # Create cache if missing
    if "parsed_cache" not in st.session_state:

        st.session_state.parsed_cache = {}

    # =====================================================
    # STEP 2 — DOWNLOAD + PARSE XML
    # =====================================================

    if cache_key in st.session_state.parsed_cache:

        parsed = st.session_state.parsed_cache[
            cache_key
        ]

        print("\nLoaded from cache.")

    else:

        xml_path = download_spl_xml(
            setid
        )

        print("\nXML SAVED:\n")
        print(xml_path)

        parsed = parse_spl_xml(
            xml_path
        )

        st.session_state.parsed_cache[
            cache_key
        ] = parsed

    # =====================================================
    # STEP 3 — VERIFY PARSE
    # =====================================================

    if not parsed:

        print("Parsing failed.")

        return None

    print("\nPARSED DATA:\n")
    print(parsed)

    # =====================================================
    # STEP 4 — FORMULATIONS
    # =====================================================

    formulations = parsed.get(
        "formulations",
        []
    )

    # =====================================================
    # STEP 5 — COMMERCIAL INTELLIGENCE
    # =====================================================

    intelligence_input = {

        "dosage_forms": list(set([
            f.get("dosage_form")
            for f in formulations
            if f.get("dosage_form")
        ])),

        "routes": list(set([
            f.get("route")
            for f in formulations
            if f.get("route")
        ])),

        "strengths": list(set([
            f.get("strength")
            for f in formulations
            if f.get("strength")
        ])),

        "manufacturer":
            parsed.get(
                "manufacturer",
                ""
            )
    }

    intelligence = (
        build_intelligence_summary(
            intelligence_input
        )
    )

    print("\nCOMMERCIAL INTELLIGENCE:\n")
    print(intelligence)

    # =====================================================
    # STEP 6 — ORANGE BOOK
    # =====================================================

    orange_book_raw = (
        build_orange_book_summary(
            drug_name
        )
    )

    orange_book_summary = (
        build_commercial_summary(
            orange_book_raw
        )
    )

    print("\nORANGE BOOK SUMMARY:\n")
    print(orange_book_summary)

    # =====================================================
    # STEP 7 — OPPORTUNITY ENGINE
    # =====================================================

    final_opportunity = (
        build_opportunity_summary(
            intelligence,
            orange_book_summary
        )
    )

    print("\nFINAL OPPORTUNITY:\n")
    print(final_opportunity)

    # =====================================================
    # STEP 8 — SAVE PRODUCT
    # =====================================================

    product_data = {

        "brand_name":
            drug_name.upper(),

        "manufacturer":
            parsed.get(
                "manufacturer"
            ),

        "setid":
            setid,

        "approval_year":
            "2017"
    }

    save_product(
        product_data
    )

    # =====================================================
    # STEP 9 — SAVE FORMULATIONS
    # =====================================================

    save_parsed_formulations(
        setid,
        formulations
    )

    print(
        "\nPipeline completed successfully."
    )

    # =====================================================
    # FINAL RESPONSE
    # =====================================================

    return {

        "drug_name":
            drug_name.upper(),

        "manufacturer":
            parsed.get(
                "manufacturer"
            ),

        "setid":
            setid,

        "parsed_data":
            parsed,

        "commercial_intelligence":
            intelligence,

        "orange_book":
            orange_book_summary,

        "final_opportunity":
            final_opportunity
    }