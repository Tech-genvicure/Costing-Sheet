import pandas as pd


def build_commercial_model(formulations):

    strengths = []

    for item in formulations:

        strength = item.get(
            "strength",
            ""
        )

        if strength and strength not in strengths:

            strengths.append(
                strength
            )

    # =====================================
    # TABLE 1
    # GLOBAL MASTER
    # =====================================

    master_df = pd.DataFrame(

        index=[

            "Genv Volume",

            "EB Volume",

            "Batch Cost",

            "Batch Size",

            "Mfg Cost / Tablet"

        ],

        columns=strengths

    )

    master_df = master_df.fillna(0)

    # =====================================
    # TABLE 2
    # PER TABLET ECONOMICS
    # =====================================

    economics_df = pd.DataFrame(

        {

            "Strength": strengths,

            "API Cost": 0,

            "RM Cost": 0,

            "PM Cost": 0,

            "Mfg Cost": 0,

            "COGS": 0,

            "Markup %": 70,

            "Selling Price": 0

        }

    )

    return {

        "master_df": master_df,

        "economics_df": economics_df

    }