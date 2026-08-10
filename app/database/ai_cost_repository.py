import sqlite3
import json


class AICostRepository:

    def __init__(self):

        self.conn = sqlite3.connect(
            "data/ai_cache.db"
        )

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

    # -----------------------------------------
    # GET CACHE
    # -----------------------------------------

    def get_cached_result(

        self,

        application_no,

        api_name,

        dosage_form,

        route

    ):

        self.cursor.execute("""

            SELECT analysis_json

            FROM ai_cost_cache

            WHERE

                application_no = ?

                AND api_name = ?

                AND dosage_form = ?

                AND route = ?

            ORDER BY created_at DESC

            LIMIT 1

        """, (

            application_no,

            api_name.upper(),

            dosage_form.upper(),

            route.upper()

        ))

        row = self.cursor.fetchone()

        if row:

            return json.loads(
                row["analysis_json"]
            )

        return None

    # -----------------------------------------
    # SAVE CACHE
    # -----------------------------------------

    def save_result(

        self,

        application_no,

        brand_name,

        generic_name,

        api_name,

        dosage_form,

        route,

        manufacturer,

        result

    ):

        self.cursor.execute("""

            INSERT INTO ai_cost_cache(

                application_no,

                brand_name,

                generic_name,

                api_name,

                dosage_form,

                route,

                manufacturer,

                analysis_json

            )

            VALUES(?,?,?,?,?,?,?,?)

        """,(

            application_no,

            brand_name,

            generic_name,

            api_name.upper(),

            dosage_form.upper(),

            route.upper(),

            manufacturer,

            json.dumps(result)

        ))

        self.conn.commit()

    def close(self):

        self.conn.close()