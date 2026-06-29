def build_opportunity_summary(

    commercial_data,
    orange_book_data

):

    score = commercial_data.get(
        "portfolio_score",
        0
    )

    patent_count = orange_book_data.get(
        "patent_count",
        0
    )

    exclusivity_count = orange_book_data.get(
        "exclusivity_count",
        0
    )

    patent_risk = orange_book_data.get(
        "patent_risk",
        "LOW"
    )

    # ============================================
    # PATENT COMPLEXITY
    # ============================================

    if patent_count >= 20:
        score += 25

    elif patent_count >= 10:
        score += 15

    # ============================================
    # EXCLUSIVITY COMPLEXITY
    # ============================================

    if exclusivity_count >= 5:
        score += 15

    elif exclusivity_count >= 2:
        score += 10

    # ============================================
    # PATENT RISK
    # ============================================

    if patent_risk == "HIGH":
        score += 20

    elif patent_risk == "MEDIUM":
        score += 10

    # ============================================
    # FINAL OPPORTUNITY
    # ============================================

    if score >= 90:

        opportunity = "MEGA BLOCKBUSTER"

    elif score >= 70:

        opportunity = "HIGH"

    elif score >= 40:

        opportunity = "MEDIUM"

    else:

        opportunity = "LOW"

    return {

        "final_score": score,

        "opportunity": opportunity,

        "patent_count": patent_count,

        "exclusivity_count": exclusivity_count,

        "patent_risk": patent_risk
    }