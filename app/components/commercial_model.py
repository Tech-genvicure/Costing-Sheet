import pandas as pd


def build_commercial_model(
    formulations
):

    strengths = []

    for item in formulations:

        strength = item.get(
            "strength",
            ""
        )

        if (
            strength
            and
            strength not in strengths
        ):

            strengths.append(
                strength
            )

    rows = [

        "Total Market Value",

        "Per Tablet Volume",

        "Genvicure Volume",

        "Batch Cost",

        "Batch Size",

        "Manufacturing Cost per Unit",

        "API Cost",

        "RM Cost",

        "PM Cost",

        "COGS",

        "Selling Price"

    ]

    data = {}

    for strength in strengths:

        data[strength] = [

            0,      # Market value
            0,      # Volume
            0,      # Genvicure volume
            0,      # Batch cost
            0,      # Batch size
            0,      # Mfg cost/unit
            0,      # API cost
            0,      # RM cost
            0,      # PM cost
            0,      # COGS
            0       # Selling price
        ]

    df = pd.DataFrame(
        data,
        index=rows
    )

    return df