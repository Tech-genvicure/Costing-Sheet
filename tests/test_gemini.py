import os

from dotenv import load_dotenv
from google import genai


# =====================================================
# LOAD ENVIRONMENT
# =====================================================

load_dotenv()


# =====================================================
# GEMINI CONFIG
# =====================================================

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY not found in .env"
    )


client = genai.Client(
    api_key=api_key
)


# =====================================================
# TEST
# =====================================================

response = client.models.generate_content(

    model="gemini-3.6-flash",

    contents="Say hello to Genvicure."

)


print("\n========== GEMINI TEST ==========")
print(response.text)
print("=================================\n")