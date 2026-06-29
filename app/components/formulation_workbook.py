import streamlit as st
import pandas as pd


# =====================================================
# INITIALIZE SESSION STATE
# =====================================================

def initialize_workbook():

    if "workbooks" not in st.session_state:
        st.session_state.workbooks = {}


# =====================================================
# CREATE DEFAULT TABLE
# =====================================================

def create_formulation_table(
    ingredients,
    api_strength
):

    rows = []

    for i, ingredient in enumerate(ingredients):

        mg_value = 0.0

        # FIRST INGREDIENT = API
        if i == 0:
            mg_value = api_strength

        rows.append({

            "Formulation": ingredient,

            "mg per capsule": mg_value,

            "per kg cost": 0.0
        })

    return pd.DataFrame(rows)


# =====================================================
# CALCULATIONS
# =====================================================

def calculate_costs(
    df,
    bottle_count
):

    calc_df = df.copy()

    calc_df["cost per tablet"] = round(

        (
            calc_df["mg per capsule"]
            / 1000000
        )

        * calc_df["per kg cost"],

        6
    )

    calc_df[
        f"cost per bottle of {bottle_count}'s"
    ] = round(

        calc_df["cost per tablet"]

        * bottle_count,

        6
    )

    total_tablet = round(
        calc_df["cost per tablet"].sum(),
        6
    )

    total_bottle = round(
        calc_df[
            f"cost per bottle of {bottle_count}'s"
        ].sum(),
        6
    )

    return (
        calc_df,
        total_tablet,
        total_bottle
    )


# =====================================================
# ADD INGREDIENT
# =====================================================

def add_ingredient(
    strength_name
):

    df = st.session_state.workbooks[
        strength_name
    ]

    new_row = pd.DataFrame([{

        "Formulation": "",

        "mg per capsule": 0.0,

        "per kg cost": 0.0
    }])

    st.session_state.workbooks[
        strength_name
    ] = pd.concat(
        [df, new_row],
        ignore_index=True
    )


# =====================================================
# DELETE TABLE
# =====================================================

def delete_table(
    strength_name
):

    if strength_name in st.session_state.workbooks:

        del st.session_state.workbooks[
            strength_name
        ]


# =====================================================
# MAIN RENDER FUNCTION
# =====================================================

def render_formulation_workbook(
    profile
):

    initialize_workbook()

    st.subheader(
        "Formulation Costing Engine"
    )

    st.divider()

    # =================================================
    # BOTTLE CONFIG
    # =================================================

    bottle_count = st.number_input(
        "Bottle Count",
        min_value=1,
        value=30
    )

    st.divider()

    # =================================================
    # LOAD FORMULATIONS
    # =================================================

    formulations = profile.get(
        "parsed_data",
        {}
    ).get(
        "formulations",
        []
    )

    if not formulations:

        st.warning(
            "No formulations found."
        )

        return

    # =================================================
    # GENERATE TABLES
    # =================================================

    if not st.session_state.workbooks:

        for formulation in formulations:

            strength = (
                formulation["strength"]
                .replace(" mg", "")
                .strip()
            )

            dosage_form = formulation[
                "dosage_form"
            ]

            title = (
                f"{strength}mg "
                f"{dosage_form.title()}s"
            )

            ingredients = [

                formulation["api_name"].title(),

                "Salcaprozate Sodium",

                "Magnesium Stearate"
            ]

            api_strength = float(strength)

            st.session_state.workbooks[
                title
            ] = create_formulation_table(
                ingredients,
                api_strength
            )

    # =================================================
    # ADD NEW TABLE
    # =================================================

    st.subheader(
        "Add New Strength Table"
    )

    c1, c2 = st.columns(2)

    with c1:

        new_strength = st.text_input(
            "Strength (mg)",
            placeholder="Example: 12"
        )

    with c2:

        new_dosage = st.selectbox(
            "Dosage Form",
            [
                "Tablet",
                "Capsule",
                "Injection"
            ]
        )

    if st.button("Add New Table"):

        if new_strength:

            table_name = (
                f"{new_strength}mg "
                f"{new_dosage}s"
            )

            ingredients = [

                formulations[0][
                    "api_name"
                ].title(),

                "New Excipient"
            ]

            st.session_state.workbooks[
                table_name
            ] = create_formulation_table(

                ingredients,

                float(new_strength)
            )

            st.success(
                f"{table_name} created."
            )

    st.divider()

    # =================================================
    # DISPLAY TABLES
    # =================================================

    for (
        strength_name,
        df
    ) in list(
        st.session_state.workbooks.items()
    ):

        st.markdown(
            f"## {profile['overview']['brand_name']} "
            f"{strength_name}"
        )

        # =============================================
        # EDITOR
        # =============================================

        edited_df = st.data_editor(

            df,

            use_container_width=True,

            hide_index=True,

            num_rows="dynamic",

            key=f"editor_{strength_name}"
        )

        st.session_state.workbooks[
            strength_name
        ] = edited_df

        # =============================================
        # CALCULATIONS
        # =============================================

        (
            calc_df,
            total_tablet,
            total_bottle
        ) = calculate_costs(

            edited_df,

            bottle_count
        )

        # =============================================
        # TOTAL ROW
        # =============================================

        total_row = pd.DataFrame([{

            "Formulation": "TOTAL",

            "mg per capsule": "",

            "per kg cost": "",

            "cost per tablet":
                total_tablet,

            f"cost per bottle of {bottle_count}'s":
                total_bottle
        }])

        final_df = pd.concat(

            [calc_df, total_row],

            ignore_index=True
        )

        # =============================================
        # DISPLAY OUTPUT
        # =============================================

        st.dataframe(

            final_df,

            use_container_width=True
        )

        # =============================================
        # ACTION BUTTONS
        # =============================================

        b1, b2 = st.columns(2)

        with b1:

            if st.button(
                f"Add Ingredient - {strength_name}"
            ):

                add_ingredient(
                    strength_name
                )

                st.rerun()

        with b2:

            if st.button(
                f"Delete Table - {strength_name}"
            ):

                delete_table(
                    strength_name
                )

                st.rerun()

        st.divider()