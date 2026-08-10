import json
import os

from dotenv import load_dotenv
from google import genai
from google.genai import types
from app.database.ai_cost_repository import AICostRepository

load_dotenv()


class AICostService:

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

    # =====================================================
    # BUILD PROMPT
    # =====================================================

    def build_prompt(
        self,
        profile,
        parsed_data,
        dmf_holders
    ):

        strengths = profile.get("strengths", [])

        dosage_forms = profile.get("dosage_forms", [])

        generic = profile.get(
            "generic_name",
            "Unknown"
        )

        brand = profile.get(
            "brand_name",
            "Unknown"
        )

        application = profile.get(
            "application_no",
            "Unknown"
        )

        manufacturer = profile.get(
            "manufacturer",
            "Unknown"
        )

        api_name = ", ".join(
            parsed_data.get(
                "active_ingredients",
                []
            )
        )

        route = ", ".join(
            parsed_data.get(
                "route",
                []
            )
        )

        inactive = parsed_data.get(
            "inactive_ingredients",
            []
        )

        # ------------------------------------------
        # DMF Holder Names
        # ------------------------------------------

        holder_names = []

        for holder in dmf_holders:

            if isinstance(holder, dict):

                holder_names.append(
                    holder.get(
                        "holder",
                        holder.get(
                            "Holder",
                            ""
                        )
                    )
                )

            else:

                holder_names.append(
                    str(holder)
                )

        holder_text = "\n".join(

            f"- {holder['holder']} (DMFs: {holder['dmf_count']})"

            for holder in dmf_holders

        )

        prompt = f"""
You are a Senior Pharmaceutical Commercial Intelligence Analyst.

You specialize in:

• API procurement
• Generic drug commercialization
• CDMO costing
• Pharmaceutical manufacturing economics
• Global API supplier pricing
• DMF landscape analysis

====================================================

FDA PROFILE

Brand Name:
{brand}

Generic Name:
{generic}

Application Number:
{application}

Manufacturer:
{manufacturer}

Dosage Form:
{", ".join(dosage_forms)}

Route:
{route}

Strengths:
{", ".join(strengths)}

API:
{api_name}

Inactive Ingredients:
{", ".join(inactive)}

====================================================

KNOWN ACTIVE DMF HOLDERS

{holder_text}

====================================================

Estimate:

1. Typical API procurement cost (USD/kg)

2. Estimated commercial manufacturing cost (USD/kg)

Consider:

• API complexity

• Peptide vs small molecule

• Manufacturing scale

• Dosage form complexity

• Number of DMF suppliers

• Global supplier competition

• Public pharmaceutical sourcing knowledge

Return ONLY VALID JSON.

{{
    "api_cost": {{
        "low": number,
        "typical": number,
        "high": number
    }},

    "commercial_cost": {{
        "low": number,
        "typical": number,
        "high": number
    }},

    "confidence":"High|Medium|Low",

    "market_summary":"...",

    "reasoning":"...",

    "major_suppliers":[
        "...",
        "...",
        "..."
    ],

    "cost_drivers":[
        "...",
        "...",
        "..."
    ]
}}

Do NOT return markdown.

Do NOT use ```.

Return JSON only.
"""

        return prompt

    # =====================================================
    # ESTIMATE
    # =====================================================

    def estimate(

        self,

        profile,

        parsed_data,

        dmf_holders

    ):

        from app.database.ai_cost_repository import AICostRepository

        repo = AICostRepository()

        application_no = str(
            profile.get(
                "application_no",
                ""
            )
        )

        brand_name = profile.get(
            "brand_name",
            ""
        )

        generic_name = profile.get(
            "generic_name",
            ""
        )

        api_name = ", ".join(

            parsed_data.get(

                "active_ingredients",

                []

            )

        )

        dosage_form = ", ".join(

            profile.get(

                "dosage_forms",

                []

            )

        )

        route = ", ".join(

            parsed_data.get(

                "route",

                []

            )

        )

        manufacturer = profile.get(

            "manufacturer",

            ""

        )

        # -----------------------------------------
        # CACHE
        # -----------------------------------------

        cached = repo.get_cached_result(

            application_no,

            api_name,

            dosage_form,

            route

        )

        if cached:

            print("\n========== AI CACHE HIT ==========\n")

            repo.close()

            return cached

        print("\n========== GEMINI REQUEST ==========\n")

        # -----------------------------------------
        # BUILD PROMPT
        # -----------------------------------------

        prompt = self.build_prompt(

            profile,

            parsed_data,

            dmf_holders

        )

        # -----------------------------------------
        # GEMINI
        # -----------------------------------------

        response = self.client.models.generate_content(

            model="gemini-3.6-flash",

            contents=prompt,

            config=types.GenerateContentConfig(

                temperature=0.2,

                response_mime_type="application/json"

            )

        )

        text = response.text.strip()

        try:

            result = json.loads(text)

        except Exception:

            result = {

                "api_cost": {

                    "low": None,

                    "typical": None,

                    "high": None

                },

                "rld_cost": {

                    "low": None,

                    "typical": None,

                    "high": None

                },

                "confidence": "Unknown",

                "market_summary": "",

                "reasoning": text,

                "major_suppliers": [],

                "cost_drivers": []

            }

        # -----------------------------------------
        # SAVE CACHE
        # -----------------------------------------

        repo.save_result(

            application_no,

            brand_name,

            generic_name,

            api_name,

            dosage_form,

            route,

            manufacturer,

            result

        )

        repo.close()

        return result