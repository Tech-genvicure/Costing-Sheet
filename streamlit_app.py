import streamlit as st # type: ignore
import pandas as pd
from app.services.dailymed_service import search_drug
from app.services.openfda_service import get_drug_label
from app.utils.drug_profile_builder import build_drug_profile
from app.services.rxnorm_service import get_rxnorm_data
from app.services.orangebook_service import build_orange_book_summary
from app.services.pipeline_service import process_drug
from app.services.commercial_service import build_commercial_model


# =====================================================
# PAGE CONFIG
# =====================================================
st.set_page_config(
    page_title="Genvicure Costing Sheet ",
    page_icon="💊",
    layout="wide"
)


st.markdown("""
<style>

/* ==========================================================
   GENVICURE ENTERPRISE THEME v1
========================================================== */

/* ---------- App Background ---------- */

.stApp{
    background:#F8FAFC;
}


/* ---------- Main Container ---------- */

.block-container{

    max-width:1600px;

    padding-top:1.5rem;

    padding-bottom:2rem;

}


/* ---------- Headings ---------- */

h1{

    color:#152026;

    font-weight:700;

}

h2,h3{

    color:#1B3D59;

    font-weight:700;

}


/* ---------- Horizontal Rule ---------- */

hr{

    border:1px solid #E7EEF4;

}


/* ---------- Input Boxes ---------- */

.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div{

    background:white !important;

    border:1px solid #D8E3EC !important;

    border-radius:8px !important;

}


/* ==========================================================
   ALL BUTTONS
========================================================== */

.stButton > button,
.stForm button,
button[kind="primary"],
button[kind="secondary"],
button[data-testid*="baseButton"] {

    background: #1B3D59 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
}

/* Force ALL text inside buttons to white */

.stButton > button *,
.stForm button *,
button[kind="primary"] *,
button[kind="secondary"] *,
button[data-testid*="baseButton"] * {

    color: #FFFFFF !important;

}

/* Hover */

.stButton > button:hover,
.stForm button:hover,
button[kind="primary"]:hover,
button[kind="secondary"]:hover,
button[data-testid*="baseButton"]:hover {

    background: #152026 !important;
    color: white !important;

}

.stButton > button:hover *,
.stForm button:hover *,
button[kind="primary"]:hover *,
button[kind="secondary"]:hover *,
button[data-testid*="baseButton"]:hover * {

    color: white !important;

}


/* ---------- Metrics ---------- */

div[data-testid="metric-container"]{

    background:white;

    border:1px solid #E4ECF3;

    border-radius:12px;

    padding:18px;

    box-shadow:0 2px 8px rgba(0,0,0,.05);

}


/* ---------- Tabs ---------- */

button[data-baseweb="tab"]{

    color:#425466;

    font-weight:600;

}

button[data-baseweb="tab"][aria-selected="true"]{

    color:#1B3D59;

    border-bottom:3px solid #1B3D59;

}


/* ---------- Data Editor ---------- */

div[data-testid="stDataEditor"]{

    background:white;

    border-radius:12px;

    border:1px solid #DDE6EE;

    box-shadow:0 2px 10px rgba(0,0,0,.04);

}


/* ---------- DataFrame ---------- */

div[data-testid="stDataFrame"]{

    background:white;

    border-radius:12px;

    border:1px solid #DDE6EE;

    box-shadow:0 2px 10px rgba(0,0,0,.04);

}


/* ---------- Sidebar ---------- */

section[data-testid="stSidebar"]{

    background:#FFFFFF;

    border-right:1px solid #E5EDF4;

}


/* ---------- Labels ---------- */

label{

    color:#425466 !important;

    font-weight:600;

}


/* ---------- Markdown Text ---------- */

p{

    color:#152026;

}


/* ---------- Success ---------- */

.stAlert{

    border-radius:10px;

}


/* ---------- Expander ---------- */

.streamlit-expanderHeader{

    font-weight:600;

    color:#1B3D59;

}

/* ==========================================================
   GENVICURE DATA EDITOR THEME
========================================================== */

/* Overall grid */
div[data-testid="stDataEditor"] {
    border: 1px solid #DDE6EE !important;
    border-radius: 12px !important;
    overflow: hidden !important;
}

/* Header row */
div[data-testid="stDataEditor"] [role="columnheader"] {
    background: #1B3D59 !important;
    color: #FFFFFF !important;
    font-weight: 700 !important;
}

/* Header text */
div[data-testid="stDataEditor"] [role="columnheader"] * {
    color: #FFFFFF !important;
    fill: #FFFFFF !important;
}

/* Data cells */
div[data-testid="stDataEditor"] [role="gridcell"] {
    background: #FFFFFF !important;
    color: #152026 !important;
}

/* Selected cell */
div[data-testid="stDataEditor"] [aria-selected="true"] {
    background: #EAF4FB !important;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================
st.title("💊 Genvicure Drug Research ")

st.markdown(
    """
    Intelligent platform for analyzing Reference Listed Drugs (RLDs),
    regulatory intelligence, formulation costing,
    and generic portfolio opportunities.
    """
)


# =====================================================
# SESSION STATE
# =====================================================
if "analysis_done" not in st.session_state:
    st.session_state.analysis_done = False

if "profile" not in st.session_state:
    st.session_state.profile = None

if "drug_name_saved" not in st.session_state:
    st.session_state.drug_name_saved = ""

if "strength_tables" not in st.session_state:
    st.session_state.strength_tables = {}

if "dosage_form_saved" not in st.session_state:
    st.session_state.dosage_form_saved = "Tablet"

if "bottle_count_saved" not in st.session_state:
    st.session_state.bottle_count_saved = 30

if "parsed_pipeline_data" not in st.session_state:
    st.session_state.parsed_pipeline_data = None

if "ingredient_costs" not in st.session_state:
    st.session_state.ingredient_costs = {}

if "deleted_tables" not in st.session_state:
    st.session_state.deleted_tables = {}

if "commercial_table" not in st.session_state:
    st.session_state.commercial_table = pd.DataFrame()

if "commercial_input_table" not in st.session_state:
    st.session_state.commercial_input_table = {}

if "drug_records" not in st.session_state:
    st.session_state.drug_records = {}

if "parsed_cache" not in st.session_state:
    st.session_state.parsed_cache = {}

if "strength_tables_initialized" not in st.session_state:
    st.session_state.strength_tables_initialized = False

if "master_df" not in st.session_state:
    st.session_state.master_df = pd.DataFrame()

if "economics_df" not in st.session_state:
    st.session_state.economics_df = pd.DataFrame()

if "strength_totals" not in st.session_state:
    st.session_state.strength_totals = {}

if "discount_values" not in st.session_state:
    st.session_state.discount_values = {}

if "year1_values" not in st.session_state:
    st.session_state.year1_values = {}

if "api_price_values" not in st.session_state:
    st.session_state.api_price_values = {}

if "drug_name_saved" not in st.session_state:
    st.session_state.drug_name_saved = None

if "manufacturer_saved" not in st.session_state:
    st.session_state.manufacturer_saved = None

if "strength_tables_initialized" not in st.session_state:
    st.session_state.strength_tables_initialized = False

# =====================================================
# SEARCH SECTION
# =====================================================
st.divider()

col1, col2, col3 = st.columns([4, 3, 1])

# -----------------------------------------
# DRUG NAME
# -----------------------------------------
with col1:

    drug_name = st.text_input(
        "Search Brand / Generic Drug",
        placeholder="Example: Wegovy",
        key="drug_search"
    )

# -----------------------------------------
# DYNAMIC MANUFACTURER LIST
# -----------------------------------------
manufacturer_options = ["ANY"]

if drug_name:

    records = search_drug(drug_name)

    manufacturers = []

    for record in records:

        title = record.get(
            "title",
            ""
        )

        if "[" in title and "]" in title:

            manufacturer_name = (
                title
                .split("[")[-1]
                .replace("]", "")
                .strip()
            )

            if (
                manufacturer_name
                and
                manufacturer_name not in manufacturers
            ):

                manufacturers.append(
                    manufacturer_name
                )

    manufacturer_options.extend(
        manufacturers
    )

# -----------------------------------------
# MANUFACTURER DROPDOWN
# -----------------------------------------
with col2:

    manufacturer = st.selectbox(
        "Manufacturer",
        manufacturer_options,
        key="manufacturer_select"
    )

# -----------------------------------------
# ANALYZE BUTTON
# -----------------------------------------
with col3:

    st.write("")
    st.write("")

    analyze_button = st.button(
        "Analyze",
        key="analyze_button"
    )

# =====================================================
# ANALYZE BUTTON
# =====================================================
if analyze_button:

    if not drug_name:

        st.warning(
            "Please enter a drug name."
        )

    else:

        with st.spinner(
            "Fetching regulatory intelligence..."
        ):

            # -----------------------------------------
            # CACHE DAILYMED SEARCH
            # -----------------------------------------
            records = search_drug(
                drug_name
            )

            st.session_state.drug_records[
                drug_name
            ] = records

            # -----------------------------------------
            # EXISTING SERVICES
            # -----------------------------------------
            drug_data = get_drug_label(
                drug_name
            )

            rxnorm_data = get_rxnorm_data(
                drug_name
            )

            orangebook_data = (
                build_orange_book_summary(
                    drug_name
                )
            )

            # -----------------------------------------
            # SAVE FOR LATER
            # -----------------------------------------
            st.session_state.drug_data = (
                drug_data
            )

            st.session_state.rxnorm_data = (
                rxnorm_data
            )

            st.session_state.orangebook_data = (
                orangebook_data
            )

            st.session_state.analysis_done = True

# =====================================================
# MANUFACTURER CHANGE
# =====================================================
if (

    st.session_state.analysis_done

    and

    drug_name in st.session_state.drug_records

):

    records = st.session_state.drug_records[
        drug_name
    ]

    pipeline_data = process_drug(

        drug_name,

        None
        if manufacturer == "ANY"
        else manufacturer,

        records=records

    )


    st.session_state.parsed_pipeline_data = (
        pipeline_data
    )

    if pipeline_data:

        # =========================================
        # MANUFACTURER
        # =========================================
        st.session_state.selected_manufacturer = (

            pipeline_data["parsed_data"][
                "manufacturer"
            ]

        )

        # =========================================
        # BUILD PROFILE
        # =========================================
        profile = build_drug_profile(

            st.session_state.drug_data,

            st.session_state.rxnorm_data,

            st.session_state.orangebook_data,

            st.session_state.parsed_pipeline_data

        )

        st.session_state.profile = (
            profile
        )

        # =========================================
        # RESET TABLES WHEN DRUG OR MANUFACTURER CHANGES
        # =========================================

        current_manufacturer = pipeline_data["parsed_data"]["manufacturer"]

        drug_changed = (
            drug_name != st.session_state.drug_name_saved
        )

        manufacturer_changed = (
            current_manufacturer != st.session_state.manufacturer_saved
        )

        if drug_changed or manufacturer_changed:

            st.session_state.strength_tables = {}

            st.session_state.ingredient_costs = {}

            st.session_state.strength_totals = {}

            st.session_state.year1_values = {}

            st.session_state.discount_values = {}

            st.session_state.markup_values = {}

            st.session_state.eb_tables = {}

            st.session_state.strength_tables_initialized = False

        # =========================================
        # SAVE CURRENT DRUG & MANUFACTURER
        # =========================================
        st.session_state.drug_name_saved = drug_name

        st.session_state.manufacturer_saved = current_manufacturer
# =====================================================
# DISPLAY ANALYSIS
# =====================================================
if st.session_state.analysis_done:

    profile = st.session_state.profile

    drug_name = st.session_state.drug_name_saved

    pipeline_data = (
        st.session_state.parsed_pipeline_data
    )

    # =================================================
    # EXECUTIVE SUMMARY
    # =================================================
    st.divider()

    st.subheader("Executive Summary")

    k1, k2, k3, k4 = st.columns(4)

    with k1:
        st.metric(
            "Brand",
            profile["overview"]["brand_name"]
        )

    with k2:
        st.metric(
            "Generic",
            profile["overview"]["generic_name"]
        )

    with k3:
        st.metric(
            "Dosage Form",
            profile["overview"]["dosage_form"]
        )

    with k4:
        st.metric(

            "Manufacturer",

            st.session_state.get(
                "selected_manufacturer",
                "N/A"
            )

        )

    # =================================================
    # TABS
    # =================================================
    st.divider()

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Regulatory",
        "Formulation Costing",
        "Commercial Model",
        "Product Economics",
        "API Calculations"
    ])

    # =================================================
    # REGULATORY TAB
    # =================================================
    with tab1:

        st.subheader("Regulatory Overview")

        r1, r2 = st.columns(2)

        with r1:
            st.info(
                f"Route: {profile['overview']['route']}"
            )

        with r2:
            st.info(
                f"Source: {profile['regulatory']['source']}"
            )

        st.success(
            f"Approval Status: "
            f"{profile['regulatory']['status']}"
        )

        st.divider()

        st.subheader("Orange Book Intelligence")

        orange_book = (
            st.session_state.parsed_pipeline_data["orange_book"]
        )

        o1, o2, o3, o4 = st.columns(4)

        with o1:
            st.metric(
                "Application No",
                orange_book["application_number"]
            )

        with o2:
            st.metric(
                "Patent Count",
                orange_book["patent_count"]
            )

        with o3:
            st.metric(
                "Exclusivity Count",
                orange_book["exclusivity_count"]
            )

        with o4:
            st.metric(
                "Patent Risk",
                orange_book["patent_risk"]
            )

    # =================================================
    # FORMULATION COSTING TAB
    # =================================================
    with tab2:

        st.subheader("Formulation Costing Engine")

        st.divider()

        parsed_data = (
            pipeline_data.get("parsed_data", {})
            if pipeline_data
            else {}
        )

        formulations = parsed_data.get(
            "formulations",
            []
        )

        # =================================================
        # DOSAGE FORM
        # =================================================
        dosage_forms = list(set([

            f.get("dosage_form", "TABLET")

            for f in formulations
        ]))

        c1, c2 = st.columns(2)

        with c1:

            dosage_form = st.selectbox(
                "Dosage Form",
                dosage_forms
                if dosage_forms
                else ["TABLET"]
            )

        with c2:

            bottle_count = st.number_input(
                "Bottle Count",
                min_value=1,
                value=30
            )

        st.divider()

        # =================================================
        # INITIAL / REBUILD TABLE GENERATION
        # =================================================
        if formulations:

            # Current strengths for selected dosage form
            current_strengths = sorted([
                f["strength"]
                for f in formulations
                if f.get("dosage_form") == dosage_form
            ])

            # Existing strengths already loaded
            existing_strengths = sorted(
                list(st.session_state.strength_tables.keys())
            )

            # -------------------------------------------------
            # REBUILD ONLY IF STRENGTHS HAVE CHANGED
            # -------------------------------------------------
            if current_strengths != existing_strengths:

                # Clear old manufacturer data
                st.session_state.strength_tables = {}
                st.session_state.ingredient_costs = {}
                st.session_state.strength_totals = {}

                # Build new strength tables
                for formulation in formulations:

                    # -----------------------------------------
                    # DOSAGE FORM FILTER
                    # -----------------------------------------
                    if (
                        formulation.get("dosage_form")
                        != dosage_form
                    ):
                        continue

                    # -----------------------------------------
                    # STRENGTH
                    # -----------------------------------------
                    strength = formulation.get(
                        "strength",
                        "0"
                    )

                    # -----------------------------------------
                    # API NAME
                    # -----------------------------------------
                    api_name = formulation.get(
                        "api_name",
                        "API"
                    ).upper()

                    # -----------------------------------------
                    # MG VALUE
                    # -----------------------------------------
                    try:

                        mg_value = float(
                            strength
                            .lower()
                            .replace("mg", "")
                            .strip()
                        )

                    except:

                        mg_value = 0.0

                    # -----------------------------------------
                    # DEFAULT ROWS
                    # -----------------------------------------
                    rows = [

                        {
                            "Formulation": api_name,
                            "mg per unit": mg_value
                        },

                        {
                            "Formulation": "EXCIPIENT 1",
                            "mg per unit": 0.0
                        },

                        {
                            "Formulation": "EXCIPIENT 2",
                            "mg per unit": 0.0
                        }

                    ]

                    # -----------------------------------------
                    # BUILD DATAFRAME
                    # -----------------------------------------
                    df = pd.DataFrame(rows)

                    st.session_state.strength_tables[
                        strength
                    ] = df

                    # -----------------------------------------
                    # REGISTER INGREDIENTS
                    # -----------------------------------------
                    for row in rows:

                        ingredient = (
                            str(row["Formulation"])
                            .upper()
                            .strip()
                        )

                        if (
                            ingredient
                            not in st.session_state.ingredient_costs
                        ):

                            st.session_state.ingredient_costs[
                                ingredient
                            ] = {

                                "per_kg_cost": 0.0,
                                "per_mg_cost": 0.0

                            }

                # -----------------------------------------
                # RESET DOWNSTREAM CALCULATIONS
                # -----------------------------------------
                st.session_state.year1_values = {}
                st.session_state.discount_values = {}
                st.session_state.markup_values = {}
                st.session_state.eb_tables = {}

                st.session_state.strength_tables_initialized = True

        # =================================================
        # GLOBAL COST MASTER
        # =================================================
        st.subheader("Global Ingredient Cost Master")

        converted_costs = {}

        for ingredient, value in (
            st.session_state.ingredient_costs.items()
        ):

            # OLD FLOAT FORMAT
            if isinstance(value, (int, float)):

                converted_costs[ingredient] = {

                    "per_kg_cost": float(value),

                    "per_mg_cost": float(value) / 1000000
                }

            # NEW DICT FORMAT
            elif isinstance(value, dict):

                converted_costs[ingredient] = {

                    "per_kg_cost": value.get(
                        "per_kg_cost",
                        0.0
                    ),

                    "per_mg_cost": value.get(
                        "per_mg_cost",
                        0.0
                    )
                }

        # SAVE FIXED FORMAT
        st.session_state.ingredient_costs = (
            converted_costs
        )

        # =============================================
        # BUILD MASTER TABLE
        # =============================================
        master_rows = []

        for ingredient, cost_data in (
            st.session_state.ingredient_costs.items()
        ):

            master_rows.append({

                "Ingredient": ingredient,

                "Per Kg Cost ($)": cost_data.get(
                    "per_kg_cost",
                    0.0
                ),

                "Per Mg Cost ($)": cost_data.get(
                    "per_mg_cost",
                    0.0
                )
            })

        master_df = pd.DataFrame(master_rows)

        # =============================================
        # MASTER EDITOR + SAVE BUTTON
        # =============================================
        with st.form("global_master_form"):

            edited_master_df = st.data_editor(

                master_df,

                use_container_width=True,

                hide_index=True,

                num_rows="dynamic",

                key="global_cost_master_editor"
            )

            save_master = st.form_submit_button(
                "💾 Save Global Master"
            )

        # =============================================
        # SAVE MASTER TABLE
        # =============================================
        if save_master:

            updated_costs = {}

            for _, row in edited_master_df.iterrows():

                ingredient = str(
                    row["Ingredient"]
                ).upper().strip()

                if ingredient == "":
                    continue

                # -----------------------------------------
                # PER KG COST
                # -----------------------------------------
                try:

                    per_kg_cost = float(
                        row["Per Kg Cost ($)"]
                    )

                except:

                    per_kg_cost = 0.0

                # -----------------------------------------
                # PER MG COST
                # -----------------------------------------
                try:

                    per_mg_cost = float(
                        row["Per Mg Cost ($)"]
                    )

                except:

                    per_mg_cost = 0.0

                # -----------------------------------------
                # AUTO CALCULATE IF EMPTY
                # -----------------------------------------
                if per_mg_cost == 0 and per_kg_cost > 0:

                    per_mg_cost = (
                        per_kg_cost / 1000000
                    )

                updated_costs[ingredient] = {

                    "per_kg_cost": per_kg_cost,

                    "per_mg_cost": per_mg_cost
                }

            # =========================================
            # SAVE SESSION STATE
            # =========================================
            st.session_state.ingredient_costs = (
                updated_costs
            )

            st.success(
                "Global Master Saved Successfully"
            )

            st.rerun()
        # =============================================
        # AUTO SYNC TO ALL STRENGTH TABLES
        # =============================================
        all_master_ingredients = list(
            st.session_state.ingredient_costs.keys()
        )

        for strength_name, table_df in (
            st.session_state.strength_tables.items()
        ):

            existing_ingredients = (
                table_df["Formulation"]
                .astype(str)
                .str.upper()
                .str.strip()
                .tolist()
            )

            # ==========================================
            # ADD MISSING INGREDIENTS
            # ==========================================
            for ingredient in all_master_ingredients:

                if ingredient not in existing_ingredients:

                    ingredient_data = (
                        st.session_state
                        .ingredient_costs
                        .get(ingredient, {})
                    )

                    new_row = pd.DataFrame([{

                        "Formulation": ingredient,

                        "mg per unit": 0.0,

                        "per kg cost":
                            ingredient_data.get(
                                "per_kg_cost",
                                0.0
                            ),

                        "per mg cost":
                            ingredient_data.get(
                                "per_mg_cost",
                                0.0
                            ),

                        "cost per unit": 0.0
                    }])

                    table_df = pd.concat(
                        [table_df, new_row],
                        ignore_index=True
                    )

            # ==========================================
            # UPDATE COSTS FROM MASTER ONLY IF COLUMN
            # DOES NOT EXIST
            # ==========================================
            if "per kg cost" not in table_df.columns:

                table_df["per kg cost"] = 0.0

            if "per mg cost" not in table_df.columns:

                table_df["per mg cost"] = 0.0

            if "cost per unit" not in table_df.columns:

                table_df["cost per unit"] = 0.0

            # ==========================================
            # FILL EMPTY VALUES ONLY
            # (DON'T OVERWRITE MANUAL CHANGES)
            # ==========================================
            for idx, row in table_df.iterrows():

                ingredient = str(
                    row["Formulation"]
                ).upper().strip()

                ingredient_data = (
                    st.session_state
                    .ingredient_costs
                    .get(ingredient, {})
                )

                if pd.isna(row["per kg cost"]) or row["per kg cost"] == 0:

                    table_df.at[
                        idx,
                        "per kg cost"
                    ] = ingredient_data.get(
                        "per_kg_cost",
                        0.0
                    )

                if pd.isna(row["per mg cost"]) or row["per mg cost"] == 0:

                    table_df.at[
                        idx,
                        "per mg cost"
                    ] = ingredient_data.get(
                        "per_mg_cost",
                        0.0
                    )

            # ==========================================
            # REMOVE DELETED INGREDIENTS
            # ==========================================
            table_df = table_df[

                table_df["Formulation"]
                .astype(str)
                .str.upper()
                .str.strip()
                .isin(all_master_ingredients)

            ]

            st.session_state.strength_tables[
                strength_name
            ] = table_df.reset_index(
                drop=True
            )
            # -----------------------------------------
            # UPDATE COST COLUMNS
            # -----------------------------------------
            updated_rows = []

            for _, row in table_df.iterrows():

                ingredient = str(
                    row["Formulation"]
                ).upper().strip()

                ingredient_data = (
                    st.session_state
                    .ingredient_costs
                    .get(ingredient, {})
                )

                updated_rows.append({

                    "Formulation": ingredient,

                    "mg per unit":
                        row.get(
                            "mg per unit",
                            0.0
                        ),

                    "per kg cost":
                        row.get(
                            "per kg cost",
                            ingredient_data.get(
                                "per_kg_cost",
                                0.0
                            )
                        ),

                    "per mg cost":
                        row.get(
                            "per mg cost",
                            ingredient_data.get(
                                "per_mg_cost",
                                0.0
                            )
                        ),

                    "cost per unit":
                        row.get(
                            "cost per unit",
                            0.0
                        )
                })

            # -----------------------------------------
            # SAVE BACK
            # -----------------------------------------
            st.session_state.strength_tables[
                strength_name
            ] = pd.DataFrame(
                updated_rows
            ).reset_index(drop=True)

        st.divider()

        # =================================================
        # ADD NEW TABLE
        # =================================================
        st.subheader("Add Strength Table")

        c1, c2 = st.columns([3, 1])

        with c1:

            new_strength = st.text_input(
                "New Strength",
                placeholder="Example: 12 mg"
            )

        with c2:

            st.write("")
            st.write("")

            if st.button("➕ Add Table"):

                if new_strength:

                    try:

                        mg_value = float(

                            new_strength
                            .lower()
                            .replace("mg", "")
                            .strip()
                        )

                    except:

                        mg_value = 0.0

                    # =====================================
                    # INGREDIENTS
                    # =====================================
                    all_ingredients = list(
                        st.session_state
                        .ingredient_costs
                        .keys()
                    )

                    # =====================================
                    # API NAME
                    # =====================================
                    if len(all_ingredients) > 0:

                        api_name = all_ingredients[0]

                    else:

                        api_name = "API"

                    # =====================================
                    # BUILD ROWS
                    # =====================================
                    rows = []

                    for ingredient in all_ingredients:

                        ingredient_data = (
                            st.session_state
                            .ingredient_costs
                            .get(ingredient, {})
                        )

                        rows.append({

                            "Formulation": ingredient,

                            "mg per unit":
                                mg_value
                                if ingredient == api_name
                                else 0.0,

                            "per kg cost":
                                ingredient_data.get(
                                    "per_kg_cost",
                                    0.0
                                ),

                            "per mg cost":
                                ingredient_data.get(
                                    "per_mg_cost",
                                    0.0
                                )
                        })

                    new_df = pd.DataFrame(rows)

                    st.session_state.strength_tables[
                        new_strength
                    ] = new_df

                    st.rerun()

        st.divider()

        # =================================================
        # DISPLAY TABLES
        # =================================================
        strength_items = list(
            st.session_state.strength_tables.items()
        ).copy()

        for i in range(0, len(strength_items), 2):

            col1, col2 = st.columns(2)

            # =============================================
            # LEFT TABLE
            # =============================================
            with col1:

                strength_name, df = strength_items[i]

                st.markdown(
                    f"### {drug_name.upper()} "
                    f"{strength_name} "
                    f"{dosage_form}"
                )

                if st.button(
                        f"🗑 Delete {strength_name}",
                        key=f"delete_{strength_name}"
                    ):

                        del st.session_state.strength_tables[
                            strength_name
                        ]

                        st.rerun()

                    
                edited_df = st.data_editor(

                    df,

                    use_container_width=True,

                    hide_index=True,

                    num_rows="dynamic",

                    key=f"editor_{strength_name}"
                )

                # SAVE
                st.session_state.strength_tables[
                    strength_name
                ] = edited_df.copy()

                calc_df = edited_df.copy()

                # -----------------------------------------
                # CLEAN NUMERIC COLUMNS
                # -----------------------------------------
                for col in [
                    "mg per unit",
                    "per kg cost",
                    "per mg cost",
                    "cost per unit"
                ]:

                    if col not in calc_df.columns:

                        calc_df[col] = 0.0

                    calc_df[col] = pd.to_numeric(
                        calc_df[col],
                        errors="coerce"
                    ).fillna(0)

                # -----------------------------------------
                # AUTO CALCULATE PER MG COST
                # -----------------------------------------
                calc_df.loc[
                    (
                        calc_df["per mg cost"] == 0
                    )
                    &
                    (
                        calc_df["per kg cost"] > 0
                    ),
                    "per mg cost"
                ] = (

                    calc_df["per kg cost"]

                    / 1000000
                )

                # -----------------------------------------
                # AUTO CALCULATE COST PER UNIT
                # ONLY WHEN EMPTY
                # -----------------------------------------
                calc_df.loc[
                    calc_df["cost per unit"] == 0,
                    "cost per unit"
                ] = round(

                    calc_df["mg per unit"]

                    *

                    calc_df["per mg cost"],

                    6
                )

                # -----------------------------------------
                # COST PER BOTTLE
                # -----------------------------------------
                calc_df[
                    f"cost per bottle ({bottle_count})"
                ] = round(

                    calc_df["cost per unit"]

                    * bottle_count,

                    6
                )

                # -----------------------------------------
                # TOTALS
                # -----------------------------------------
                total_unit_cost = round(

                    calc_df[
                        "cost per unit"
                    ].sum(),

                    6
                )

                total_bottle_cost = round(

                    total_unit_cost

                    * bottle_count,

                    6
                )

                # -----------------------------------------
                # TOTAL ROW
                # -----------------------------------------
                total_row = pd.DataFrame([{

                    "Formulation": "TOTAL",

                    "mg per unit": "",

                    "per kg cost": "",

                    "per mg cost": "",

                    "cost per unit":
                        total_unit_cost,

                    f"cost per bottle ({bottle_count})":
                        total_bottle_cost
                }])

                final_df = pd.concat(

                    [calc_df, total_row],

                    ignore_index=True
                )

                st.metric(

                    "Cost Per Bottle",

                    f"${total_bottle_cost}"
                )

                st.dataframe(

                    final_df,

                    use_container_width=True,

                    height=350
                )
                # -----------------------------------------
                # SAVE STRENGTH TOTALS
                # -----------------------------------------
                st.session_state.strength_totals[
                    strength_name
                ] = {

                    "unit_cost": total_unit_cost,

                    "bottle_cost": total_bottle_cost

                }

            # =============================================
            # RIGHT TABLE
            # =============================================
            if i + 1 < len(strength_items):

                with col2:

                    strength_name, df = (
                        strength_items[i + 1]
                    )

                    st.markdown(
                        f"### {drug_name.upper()} "
                        f"{strength_name} "
                        f"{dosage_form}"
                    )

                    if st.button(
                            f"🗑 Delete {strength_name}",
                            key=f"delete_{strength_name}"
                        ):

                            del st.session_state.strength_tables[
                                strength_name
                            ]

                            st.rerun()


                    edited_df = st.data_editor(

                        df,

                        use_container_width=True,

                        hide_index=True,

                        num_rows="dynamic",

                        key=f"editor_{strength_name}"
                    )

                    # SAVE
                    st.session_state.strength_tables[
                        strength_name
                    ] = edited_df.copy()

                    calc_df = edited_df.copy()

                    # -----------------------------------------
                    # CLEAN NUMERIC COLUMNS
                    # -----------------------------------------
                    for col in [
                        "mg per unit",
                        "per kg cost",
                        "per mg cost",
                        "cost per unit"
                    ]:

                        if col not in calc_df.columns:

                            calc_df[col] = 0.0

                        calc_df[col] = pd.to_numeric(
                            calc_df[col],
                            errors="coerce"
                        ).fillna(0)

                    # -----------------------------------------
                    # AUTO CALCULATE PER MG COST
                    # -----------------------------------------
                    calc_df.loc[
                        (
                            calc_df["per mg cost"] == 0
                        )
                        &
                        (
                            calc_df["per kg cost"] > 0
                        ),
                        "per mg cost"
                    ] = (

                        calc_df["per kg cost"]

                        / 1000000
                    )

                    # -----------------------------------------
                    # AUTO CALCULATE COST PER UNIT
                    # ONLY WHEN EMPTY
                    # -----------------------------------------
                    calc_df.loc[
                        calc_df["cost per unit"] == 0,
                        "cost per unit"
                    ] = round(

                        calc_df["mg per unit"]

                        *

                        calc_df["per mg cost"],

                        6
                    )

                    # -----------------------------------------
                    # COST PER BOTTLE
                    # -----------------------------------------
                    calc_df[
                        f"cost per bottle ({bottle_count})"
                    ] = round(

                        calc_df["cost per unit"]

                        * bottle_count,

                        6
                    )

                    # -----------------------------------------
                    # TOTALS
                    # -----------------------------------------
                    total_unit_cost = round(

                        calc_df[
                            "cost per unit"
                        ].sum(),

                        6
                    )

                    total_bottle_cost = round(

                        total_unit_cost

                        * bottle_count,

                        6
                    )

                    # -----------------------------------------
                    # TOTAL ROW
                    # -----------------------------------------
                    total_row = pd.DataFrame([{

                        "Formulation": "TOTAL",

                        "mg per unit": "",

                        "per kg cost": "",

                        "per mg cost": "",

                        "cost per unit":
                            total_unit_cost,

                        f"cost per bottle ({bottle_count})":
                            total_bottle_cost
                    }])

                    final_df = pd.concat(

                        [calc_df, total_row],

                        ignore_index=True
                    )

                    st.metric(
                        "Cost Per Bottle",
                        f"${total_bottle_cost}"
                    )

                    st.dataframe(

                        final_df,

                        use_container_width=True,

                        height=350
                    )

                    # -----------------------------------------
                    # SAVE STRENGTH TOTALS
                    # -----------------------------------------
                    st.session_state.strength_totals[
                        strength_name
                    ] = {

                        "unit_cost": total_unit_cost,

                        "bottle_cost": total_bottle_cost

                    }

            st.divider()

    # ==========================================
    # COMMERCIAL MODEL
    # ==========================================
    with tab3:

        strengths = list(
            st.session_state.strength_tables.keys()
        )

        # =====================================
        # GLOBAL MASTER
        # =====================================
        st.subheader("Global Master")

        master_metrics = [
            "Genv Volume",
            "EB Volume",
            "Batch Cost",
            "Batch Size"
        ]

        # -------------------------------------
        # BUILD TABLE
        # -------------------------------------
        master_df = pd.DataFrame({
            "Metric": master_metrics
        })

        for strength in strengths:
            master_df[strength] = 0.0

        # -------------------------------------
        # LOAD PREVIOUS VALUES
        # -------------------------------------
        if (
            "master_df" in st.session_state
            and
            not st.session_state.master_df.empty
            and
            "Metric" in st.session_state.master_df.columns
        ):

            old_df = st.session_state.master_df.copy()

            for strength in strengths:

                if strength in old_df.columns:

                    master_df[strength] = old_df[strength]

        # -------------------------------------
        # SHOW EDITOR
        # -------------------------------------
        edited_master_df = st.data_editor(
            master_df,
            use_container_width=True,
            hide_index=True,
            num_rows="fixed",
            key="master_table"
        )

        # -------------------------------------
        # SAVE
        # -------------------------------------
        st.session_state.master_df = edited_master_df
        st.divider()

        # =====================================
        # PER TABLET ECONOMICS
        # =====================================
        st.subheader(
            "Per Tablet Economics"
        )

        economics_rows = []

        for strength in strengths:

            # ---------------------------------
            # API COST
            # ---------------------------------
            api_cost = float(

                st.session_state

                .strength_totals

                .get(

                    strength,

                    {}

                )

                .get(

                    "unit_cost",

                    0.0

                )

            )

            # ---------------------------------
            # RM + PM = 2%
            # ---------------------------------
            rm_cost = api_cost * 0.02

            pm_cost = api_cost * 0.02

            # ---------------------------------
            # MFG COST
            # ---------------------------------
            try:

                batch_cost = float(

                    edited_master_df.loc[

                        edited_master_df["Metric"]

                        ==

                        "Batch Cost",

                        strength

                    ].iloc[0]

                )

            except:

                batch_cost = 0.0

            try:

                batch_size = float(

                    edited_master_df.loc[

                        edited_master_df["Metric"]

                        ==

                        "Batch Size",

                        strength

                    ].iloc[0]

                )

            except:

                batch_size = 0.0

            mfg_cost = (

                batch_cost / batch_size

                if batch_size > 0

                else 0.0

            )

            # ---------------------------------
            # KEEP USER MARKUP
            # ---------------------------------
            markup = 70.0

            if (

                not st.session_state.economics_df.empty

                and

                strength in st.session_state.economics_df["Strength"].values

            ):

                try:

                    markup = float(

                        st.session_state.economics_df.loc[

                            st.session_state.economics_df["Strength"]

                            ==

                            strength,

                            "Markup %"

                        ].iloc[0]

                    )

                except:

                    markup = 70.0

            # ---------------------------------
            # COGS
            # ---------------------------------
            cogs = (

                api_cost

                + rm_cost

                + pm_cost

                + mfg_cost

            )

            # ---------------------------------
            # SELLING PRICE
            # ---------------------------------
            selling_price = (

                cogs

                * (

                    1

                    + markup / 100

                )

            )

            economics_rows.append(

                {

                    "Strength": strength,

                    "API Cost": round(

                        api_cost,

                        6

                    ),

                    "RM Cost": round(

                        rm_cost,

                        6

                    ),

                    "PM Cost": round(

                        pm_cost,

                        6

                    ),

                    "Mfg Cost": round(

                        mfg_cost,

                        6

                    ),

                    "COGS": round(

                        cogs,

                        6

                    ),

                    "Markup %": markup,

                    "Selling Price": round(

                        selling_price,

                        6

                    )

                }

            )

        economics_df = pd.DataFrame(

            economics_rows

        )

        st.session_state.economics_df = st.data_editor(

            economics_df,

            use_container_width=True,

            hide_index=True,

            num_rows="fixed",

            key="economics_table"

        )
    

    # ==========================================================
    # BUILD COMMERCIAL CALCULATION TABLE
    # ==========================================================
    with tab4:
        strengths = list(st.session_state.strength_tables.keys())

        rows = []

        for strength in strengths:

            # ------------------------------------------------------
            # Bottle Count
            # ------------------------------------------------------
            bottle_count_local = bottle_count

            # ------------------------------------------------------
            # Per Tablet Selling Price
            # ------------------------------------------------------
            selling_price_per_tablet = economics_df.loc[
                economics_df["Strength"] == strength,
                "Selling Price"
            ].iloc[0]

            # ------------------------------------------------------
            # TP
            # ------------------------------------------------------
            tp = selling_price_per_tablet * bottle_count_local

            # ------------------------------------------------------
            # Annual Volume
            # ------------------------------------------------------
            annual_volume = edited_master_df.loc[
                edited_master_df["Metric"] == "Genv Volume",
                strength
            ].iloc[0]

            # ------------------------------------------------------
            # Annual COX
            # ------------------------------------------------------
            annual_cox = tp * annual_volume

            # ------------------------------------------------------
            # Discount
            # ------------------------------------------------------
            discount = st.session_state.discount_values.get(
                strength,
                10.0
            )

            # ------------------------------------------------------
            # Selling Price
            # ------------------------------------------------------
            selling_price = annual_cox * discount

            # ------------------------------------------------------
            # Marketing & Logistics Cost
            # Remaining 86%
            # ------------------------------------------------------
            marketing_logistics_cost = selling_price * 0.86

            # ------------------------------------------------------
            # Total Profit
            # ------------------------------------------------------
            total_profit = marketing_logistics_cost - annual_cox

            # ------------------------------------------------------
            # Profit Share
            # Remaining 60%
            # ------------------------------------------------------
            profit_share = total_profit * 0.60

            rows.append(
                {
                    "Strength": strength,
                    "TP": tp,
                    "Annual Volume": annual_volume,
                    "Annual COX": annual_cox,
                    "Discount": discount,
                    "Selling Price": selling_price,
                    "Marketing & Logistics Cost": marketing_logistics_cost,
                    "Total Profit": total_profit,
                    "Profit Share": profit_share
                }
            )


        commercial_df = pd.DataFrame(rows)


        # ==========================================================
        # EDITABLE TABLE
        # ==========================================================
        edited_commercial_df = st.data_editor(
            commercial_df,
            use_container_width=True,
            hide_index=True,
            key="commercial_calc_table",
            disabled=[
                "Strength",
                "TP",
                "Annual Volume",
                "Annual COX",
                "Selling Price",
                "Marketing & Logistics Cost",
                "Total Profit",
                "Profit Share"
            ]
        )


        # ==========================================================
        # SAVE DISCOUNT VALUES
        # ==========================================================
        discount_changed = False

        for _, row in edited_commercial_df.iterrows():

            strength = row["Strength"]

            try:
                new_discount = float(row["Discount"])
            except:
                new_discount = 10.0

            old_discount = st.session_state.discount_values.get(
                strength,
                10.0
            )

            if new_discount != old_discount:

                st.session_state.discount_values[strength] = new_discount

                discount_changed = True


        # ==========================================================
        # RERUN IF DISCOUNT CHANGED
        # ==========================================================
        if discount_changed:
            st.rerun()
    
    # ==========================================================
    # TAB 5 : API COMMERCIAL PLANNING
    # ==========================================================
    with tab5:

        st.subheader("API Commercial Planning")

        strengths = list(st.session_state.strength_tables.keys())

        rows = [
            "mg",
            "Year 1",
            "No. of Tablets",
            "Total API Requirement",
            "Total API (Kg)",
            "Price of API (per kg)"
        ]

        commercial_data = {
            "Commercial": rows
        }

        # ------------------------------------------------------
        # BUILD TABLE
        # ------------------------------------------------------
        for strength in strengths:

            mg_value = float(
                str(strength).replace(" mg", "")
            )

            if strength not in st.session_state.year1_values:
                st.session_state.year1_values[strength] = 0

            year1 = st.session_state.year1_values[strength]

            # Get the formulation table for this strength
            formulation_df = st.session_state.strength_tables.get(strength)

            api_price = 0

            if formulation_df is not None and len(formulation_df) > 0:

                api_name = formulation_df.iloc[0]["Formulation"]

                api_price = (
                    st.session_state.ingredient_costs
                    .get(api_name, {})
                    .get("per_kg_cost", 0)
                )

            no_of_tablets = year1 * bottle_count

            total_api_requirement = (
                no_of_tablets * mg_value
            )

            total_api_kg = (
                total_api_requirement / 1_000_000
            )

            commercial_data[strength] = [
                mg_value,
                year1,
                no_of_tablets,
                total_api_requirement,
                total_api_kg,
                api_price
            ]

        commercial_df = pd.DataFrame(
            commercial_data
        )

        # ------------------------------------------------------
        # DISPLAY TABLE
        # ------------------------------------------------------
        edited_df = st.data_editor(
            commercial_df,
            use_container_width=True,
            hide_index=True,
            key="commercial_api_table"
        )

        # ------------------------------------------------------
        # SAVE EDITS
        # ------------------------------------------------------
        table_changed = False

        for strength in strengths:

            new_year1 = float(
                edited_df.loc[
                    edited_df["Commercial"] == "Year 1",
                    strength
                ].iloc[0]
            )

            old_year1 = (
                st.session_state.year1_values.get(
                    strength,
                    0
                )
            )

            if new_year1 != old_year1:

                st.session_state.year1_values[
                    strength
                ] = new_year1

                table_changed = True


        if table_changed:
            st.rerun()

        # ------------------------------------------------------
        # TOTAL API COST COMMERCIAL
        # ------------------------------------------------------
        total_api_cost_commercial = 0

        for strength in strengths:

            mg_value = float(
                str(strength).replace(" mg", "")
            )

            year1 = (
                st.session_state.year1_values.get(
                    strength,
                    0
                )
            )

            formulation_df = st.session_state.strength_tables.get(strength)

            api_price = 0

            if formulation_df is not None and len(formulation_df) > 0:

                api_name = formulation_df.iloc[0]["Formulation"]

                api_price = (
                    st.session_state.ingredient_costs
                    .get(api_name, {})
                    .get("per_kg_cost", 0)
                )

            no_of_tablets = (
                year1 * bottle_count
            )

            total_api_requirement = (
                no_of_tablets * mg_value
            )

            total_api_kg = (
                total_api_requirement / 1_000_000
            )

            total_api_cost_commercial += (
                total_api_kg * api_price
            )

        st.metric(
            "Total API Cost Commercial ($)",
            f"{total_api_cost_commercial:,.2f}"
        )  

        # ==========================================================
        # EB SCENARIOS
        # ==========================================================

        import math

        st.markdown("---")
        st.subheader("EB Planning")


        # ==========================================================
        # SESSION STATE
        # ==========================================================

        if "eb_tables" not in st.session_state:

            st.session_state.eb_tables = {
                "EB Scenario 1": {
                    "batch_sizes": {},
                    "manual_total_cost": 0
                }
            }


        # ==========================================================
        # ADD SCENARIO BUTTON
        # ==========================================================

        if st.button("➕ Add EB Scenario"):

            scenario_no = len(
                st.session_state.eb_tables
            ) + 1

            st.session_state.eb_tables[
                f"EB Scenario {scenario_no}"
            ] = {

                "batch_sizes": {},

                "manual_total_cost": 0
            }

            st.rerun()


        # ==========================================================
        # DISPLAY EACH SCENARIO
        # ==========================================================

        strengths = list(
            st.session_state.strength_tables.keys()
        )

        for scenario_name, scenario_data in (
            st.session_state.eb_tables.items()
        ):

            title_col, delete_col = st.columns([6, 2])

            with title_col:
                st.markdown(f"### {scenario_name}")

            with delete_col:

                if (
                    scenario_name != "EB Scenario 1"
                    and st.button(
                        f"Delete",
                        key=f"delete_{scenario_name}"
                    )
                ):

                    del st.session_state.eb_tables[
                        scenario_name
                    ]

                    st.rerun()

            rows = [
                "mg",
                "EB Batch Size",
                "EB API Quantity (kg)",
                "EB API Quantity (4 Batches)",
                "Price of API"
            ]

            eb_data = {
                "EB": rows
            }

            # ------------------------------------------------------
            # BUILD TABLE
            # ------------------------------------------------------

            for strength in strengths:

                mg_value = float(
                    str(strength).replace(" mg", "")
                )

                if (
                    strength
                    not in scenario_data["batch_sizes"]
                ):
                    scenario_data["batch_sizes"][
                        strength
                    ] = 0

                eb_batch_size = (
                    scenario_data["batch_sizes"][
                        strength
                    ]
                )

                eb_api_qty = (
                    mg_value * eb_batch_size
                ) / 1_000_000

                # As per your sheet logic
                eb_api_qty_4_batches = (
                    eb_api_qty * 3
                )

                formulation_df = st.session_state.strength_tables.get(strength)

                api_price = 0

                if formulation_df is not None and len(formulation_df) > 0:

                    api_name = formulation_df.iloc[0]["Formulation"]

                    api_price = (
                        st.session_state.ingredient_costs
                        .get(api_name, {})
                        .get("per_kg_cost", 0)
                    )

                eb_data[strength] = [

                    mg_value,

                    eb_batch_size,

                    eb_api_qty,

                    eb_api_qty_4_batches,

                    api_price
                ]

            eb_df = pd.DataFrame(
                eb_data
            )

            # ------------------------------------------------------
            # DISPLAY EDITOR
            # ------------------------------------------------------

            edited_eb_df = st.data_editor(
                eb_df,
                use_container_width=True,
                hide_index=True,
                key=f"eb_editor_{scenario_name}"
            )

            # ------------------------------------------------------
            # SAVE CHANGES
            # ------------------------------------------------------

            changed = False

            for strength in strengths:

                try:

                    new_batch_size = float(
                        edited_eb_df.loc[
                            edited_eb_df["EB"]
                            == "EB Batch Size",
                            strength
                        ].iloc[0]
                    )

                except:

                    new_batch_size = 0

                old_batch_size = (
                    scenario_data["batch_sizes"].get(
                        strength,
                        0
                    )
                )

                if new_batch_size != old_batch_size:

                    scenario_data["batch_sizes"][
                        strength
                    ] = new_batch_size

                    changed = True

            if changed:
                st.rerun()

            # ------------------------------------------------------
            # TOTALS
            # ------------------------------------------------------

            total_api_kg = 0

            total_api_cost = 0

            for strength in strengths:

                mg_value = float(
                    str(strength).replace(" mg", "")
                )

                batch_size = (
                    scenario_data["batch_sizes"].get(
                        strength,
                        0
                    )
                )

                api_price = (
                    st.session_state.api_price_values.get(
                        strength,
                        50000
                    )
                )

                eb_api_qty = (
                    mg_value * batch_size
                ) / 1_000_000

                eb_api_qty_4_batches = (
                    eb_api_qty * 3
                )

                total_api_kg += (
                    eb_api_qty_4_batches
                )

                total_api_cost += (
                    eb_api_qty_4_batches
                    * api_price
                )

            # ------------------------------------------------------
            # ROUND TO NEXT 10 KG
            # ------------------------------------------------------

            rounded_api_kg = (
                math.ceil(
                    total_api_kg / 10
                ) * 10
            )

            # ------------------------------------------------------
            # MANUAL COST
            # ------------------------------------------------------

            manual_cost = st.number_input(
                f"{scenario_name} - Total API Cost for EB (Rounded)",
                value=float(
                    scenario_data.get(
                        "manual_total_cost",
                        0
                    )
                ),
                key=f"manual_cost_{scenario_name}"
            )

            scenario_data[
                "manual_total_cost"
            ] = manual_cost

            # ------------------------------------------------------
            # SUMMARY
            # ------------------------------------------------------

            col1, col2, col3 = st.columns(3)

            with col1:

                st.metric(
                    "Total API for EB (kg)",
                    f"{total_api_kg:,.2f}"
                )

            with col2:

                st.metric(
                    "Total API for EB (kg) Rounded",
                    f"{rounded_api_kg:,.2f}"
                )

            with col3:

                st.metric(
                    "Total API Cost for EB",
                    f"{total_api_cost:,.2f}"
                )

            st.markdown("---")