from app.database.db import get_connection
from app.utils.normalizer import normalize_text


def save_parsed_formulations(
    setid,
    formulations
):

    conn = get_connection()

    cursor = conn.cursor()

    saved_count = 0

    for formulation in formulations:

        api_name = normalize_text(
            formulation.get("api_name")
        )

        strength = normalize_text(
            formulation.get("strength")
        )

        dosage_form = normalize_text(
            formulation.get("dosage_form")
        )

        route = normalize_text(
            formulation.get("route")
        )

        # ============================================
        # SKIP INCOMPLETE ROWS
        # ============================================

        if not api_name or not strength:

            print("SKIPPED — Missing data")
            continue

        # ============================================
        # DEBUG PRINT
        # ============================================

        print("\nCHECKING FORMULATION:")

        print({
            "setid": setid,
            "api_name": api_name,
            "strength": strength,
            "dosage_form": dosage_form,
            "route": route
        })

        # ============================================
        # CHECK DUPLICATES
        # ============================================

        cursor.execute("""
            SELECT id
            FROM parsed_formulations
            WHERE
                setid = ?
                AND api_name = ?
                AND strength = ?
                AND dosage_form = ?
                AND route = ?
        """, (
            setid,
            api_name,
            strength,
            dosage_form,
            route
        ))

        exists = cursor.fetchone()

        if exists:

            print("SKIPPED — Already exists")
            continue

        # ============================================
        # INSERT FORMULATION
        # ============================================

        try:

            cursor.execute("""
                INSERT INTO parsed_formulations (
                    setid,
                    api_name,
                    strength,
                    dosage_form,
                    route,
                    source
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                setid,
                api_name,
                strength,
                dosage_form,
                route,
                "DAILYMED"
            ))

            saved_count += 1

            print("INSERTED")

        except Exception as e:

            print("INSERT FAILED")
            print(e)

    conn.commit()

    conn.close()

    print(
        f"\n{saved_count} formulations saved successfully."
    )