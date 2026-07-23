import sqlite3
from pathlib import Path


class DrugRepository:

    def __init__(self):

        db_path = Path(__file__).parent / "pharma.db"

        self.conn = sqlite3.connect(db_path)

        self.conn.row_factory = sqlite3.Row

        self.cursor = self.conn.cursor()

    # ----------------------------------------------------
    # SEARCH DRUG
    # ----------------------------------------------------

    def search_drug(self, query, limit=25):

        sql = """
        SELECT

            p.ApplNo,
            p.ProductNo,
            p.DrugName,
            p.ActiveIngredient,
            p.Form,
            p.Strength,
            p.ReferenceDrug,
            p.ReferenceStandard,

            a.ApplType,
            a.SponsorName

        FROM products p

        JOIN applications a

            ON p.ApplNo = a.ApplNo

        WHERE

            p.DrugName LIKE ?

            OR

            p.ActiveIngredient LIKE ?

        ORDER BY

            p.DrugName

        LIMIT ?
        """

        self.cursor.execute(
            sql,
            (f"%{query}%", f"%{query}%", limit),
        )

        rows = self.cursor.fetchall()

        return [dict(row) for row in rows]

    # ----------------------------------------------------
    # APPLICATION
    # ----------------------------------------------------

    def get_application(self, appl_no):

        self.cursor.execute(
            """
            SELECT *
            FROM applications
            WHERE ApplNo = ?
            """,
            (appl_no,),
        )

        row = self.cursor.fetchone()

        return dict(row) if row else None

    # ----------------------------------------------------
    # PRODUCTS
    # ----------------------------------------------------

    def get_products(self, appl_no):

        self.cursor.execute(
            """
            SELECT *
            FROM products
            WHERE ApplNo = ?
            ORDER BY ProductNo
            """,
            (appl_no,),
        )

        return [dict(r) for r in self.cursor.fetchall()]

    # ----------------------------------------------------
    # LATEST SUBMISSION
    # ----------------------------------------------------

    def get_latest_submission(self, appl_no):

        self.cursor.execute(
            """
            SELECT *
            FROM submissions

            WHERE ApplNo = ?

            ORDER BY SubmissionStatusDate DESC

            LIMIT 1
            """,
            (appl_no,),
        )

        row = self.cursor.fetchone()

        return dict(row) if row else None

    # ----------------------------------------------------
    # MARKETING STATUS
    # ----------------------------------------------------

    def get_marketing_status(self, appl_no, product_no):

        self.cursor.execute(
            """
            SELECT *

            FROM marketing_status

            WHERE

                ApplNo = ?

                AND

                ProductNo = ?
            """,
            (appl_no, product_no),
        )

        row = self.cursor.fetchone()

        return dict(row) if row else None
    
    # ----------------------------------------------------
    # ORANGE BOOK PRODUCT
    # ----------------------------------------------------

    def get_orange_product(self, appl_no):

        self.cursor.execute(
            """
            SELECT *

            FROM orange_products

            WHERE Appl_No = ?

            ORDER BY Product_No

            LIMIT 1
            """,
            (appl_no,),
        )

        row = self.cursor.fetchone()

        return dict(row) if row else None
    
    # ----------------------------------------------------
    # ORANGE BOOK PATENTS
    # ----------------------------------------------------

    def get_patents(self, appl_no):

        self.cursor.execute(
            """
            SELECT *

            FROM orange_patents

            WHERE Appl_No = ?

            ORDER BY Patent_Expire_Date_Text
            """,
            (appl_no,),
        )

        return [dict(row) for row in self.cursor.fetchall()]

    # ----------------------------------------------------
    # ORANGE BOOK EXCLUSIVITIES
    # ----------------------------------------------------

    def get_exclusivities(self, appl_no):

        self.cursor.execute(
            """
            SELECT *

            FROM orange_exclusivity

            WHERE Appl_No = ?

            ORDER BY Exclusivity_Date
            """,
            (appl_no,),
        )

        return [dict(row) for row in self.cursor.fetchall()]


    # ----------------------------------------------------
    # CLOSE
    # ----------------------------------------------------

    def close(self):

        self.conn.close()