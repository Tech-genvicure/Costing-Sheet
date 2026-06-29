def build_intelligence_summary(parsed_data):

    formulations = parsed_data.get(
        "formulations",
        []
    )

    strengths = parsed_data.get(
        "strengths",
        []
    )

    dosage_forms = parsed_data.get(
        "dosage_form",
        []
    )

    routes = parsed_data.get(
        "route",
        []
    )

    score = 0

    # ============================================
    # STRENGTH COMPLEXITY
    # ============================================

    strength_count = len(strengths)

    if strength_count >= 8:
        score += 35

    elif strength_count >= 5:
        score += 25

    else:
        score += 10

    # ============================================
    # INJECTION COMPLEXITY
    # ============================================

    if "INJECTION" in dosage_forms:
        score += 30

    # ============================================
    # SUBCUTANEOUS COMPLEXITY
    # ============================================

    if "SUBCUTANEOUS" in routes:
        score += 20

    # ============================================
    # MULTIPLE DOSAGE FORMS
    # ============================================

    if len(dosage_forms) > 1:
        score += 15

    # ============================================
    # FINAL COMPLEXITY
    # ============================================

    if score >= 75:
        complexity = "HIGH"

    elif score >= 45:
        complexity = "MEDIUM"

    else:
        complexity = "LOW"

    # ============================================
    # OPPORTUNITY
    # ============================================

    if score >= 70:
        opportunity = "HIGH"

    elif score >= 40:
        opportunity = "MEDIUM"

    else:
        opportunity = "LOW"

    return {

        "complexity": complexity,

        "portfolio_score": score,

        "opportunity": opportunity,

        "strength_count": strength_count
    }