from app.services.scoring_service import build_intelligence_summary

drug_data = {
    "dosage_form": "INJECTION",
    "route": "SUBCUTANEOUS",
    "strengths": [
        "0.25 mg",
        "0.5 mg",
        "1 mg",
        "1.7 mg",
        "2.4 mg"
    ],
    "manufacturer": "Novo Nordisk"
}

result = build_intelligence_summary(drug_data)

print(result)