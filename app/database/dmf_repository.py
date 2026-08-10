import sqlite3


class DMFRepository:

    def __init__(self):

        self.conn = sqlite3.connect(
            "data/dmf.db"
        )

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

    # -------------------------------------------------
    # Get DMF records
    # -------------------------------------------------
    def get_holders(
        self,
        api_name,
        active_only=True
    ):

        sql = """

            SELECT

                DMF_No,
                Holder,
                Status,
                Type,
                Subject

            FROM dmf_holders

            WHERE

                UPPER(Subject) LIKE ?

        """

        params = [
            f"%{api_name.upper()}%"
        ]

        if active_only:

            sql += """

                AND TRIM(UPPER(Status)) = 'A'

            """

        sql += """

            ORDER BY Holder

        """

        self.cursor.execute(
            sql,
            params
        )

        return [

            dict(row)

            for row in self.cursor.fetchall()

        ]

    # -------------------------------------------------
    # Get UNIQUE Active Holders
    # (Best for AI prompts)
    # -------------------------------------------------
    def get_active_holders(
        self,
        api_name
    ):

        self.cursor.execute("""

            SELECT DISTINCT

                Holder

            FROM dmf_holders

            WHERE

                UPPER(Subject) LIKE ?

            AND

                TRIM(UPPER(Status)) = 'A'

            ORDER BY Holder

        """, (

            f"%{api_name.upper()}%",

        ))

        return [

            row["Holder"]

            for row in self.cursor.fetchall()

        ]

    # -----------------------------------------
    # Supplier Summary
    # -----------------------------------------
    def get_supplier_summary(self, api_name):

        self.cursor.execute("""

            SELECT

                Holder AS holder,

                COUNT(*) AS dmf_count

            FROM dmf_holders

            WHERE
                UPPER(Subject) LIKE ?
            AND
                UPPER(Status) = 'ACTIVE'

            GROUP BY Holder

            ORDER BY dmf_count DESC, Holder

        """, (

            f"%{api_name.upper()}%",

        ))

        return [

            dict(row)

            for row in self.cursor.fetchall()

        ]

    def get_ai_supplier_context(
        self,
        api_name,
        limit=15
    ):

        self.cursor.execute("""

            SELECT

                Holder,

                COUNT(*) AS dmf_count

            FROM dmf_holders

            WHERE

                UPPER(Subject) LIKE ?

            AND

                Status = 'A'

            GROUP BY Holder

            ORDER BY dmf_count DESC,
                    Holder

            LIMIT ?

        """, (

            f"%{api_name.upper()}%",
            limit

        ))

        rows = self.cursor.fetchall()

        suppliers = []

        for row in rows:

            suppliers.append({

                "holder": row["Holder"],

                "country": "Unknown",

                "dmf_count": row["dmf_count"]

            })

        return suppliers

    def get_ai_prompt_context(
        self,
        api_name,
        limit=15
    ):

        suppliers = self.get_ai_supplier_context(
            api_name,
            limit
        )

        lines = []

        for supplier in suppliers:

            lines.append(
                f"- {supplier['holder']} "
                f"({supplier['dmf_count']} Active DMFs)"
            )

        return "\n".join(lines)

    # -------------------------------------------------
    # Close connection
    # -------------------------------------------------
    def close(self):

        self.conn.close()