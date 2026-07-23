import sqlite3

DB_PATH = "app/database/pharma.db"


def create_tables():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # ============================================================
    # DRUGS@FDA TABLES
    # ============================================================

    # Applications
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        ApplNo TEXT PRIMARY KEY,
        ApplType TEXT,
        ApplPublicNotes TEXT,
        SponsorName TEXT
    )
    """)

    # Products
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        ApplNo TEXT,
        ProductNo TEXT,
        Form TEXT,
        Strength TEXT,
        ReferenceDrug TEXT,
        DrugName TEXT,
        ActiveIngredient TEXT,
        ReferenceStandard TEXT
    )
    """)

    # Submissions
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS submissions (
        ApplNo TEXT,
        SubmissionClassCodeID TEXT,
        SubmissionType TEXT,
        SubmissionNo TEXT,
        SubmissionStatus TEXT,
        SubmissionStatusDate TEXT,
        SubmissionsPublicNotes TEXT,
        ReviewPriority TEXT
    )
    """)

    # Marketing Status
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS marketing_status (
        MarketingStatusID INTEGER,
        ApplNo TEXT,
        ProductNo TEXT
    )
    """)

    # ============================================================
    # ORANGE BOOK TABLES
    # ============================================================

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orange_products (

        Ingredient TEXT,
        DF_Route TEXT,
        Trade_Name TEXT,

        Applicant TEXT,
        Applicant_Full_Name TEXT,

        Strength TEXT,

        Appl_Type TEXT,
        Appl_No TEXT,
        Product_No TEXT,

        TE_Code TEXT,

        Approval_Date TEXT,

        RLD TEXT,
        RS TEXT,

        Type TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orange_patents (

        Appl_Type TEXT,
        Appl_No TEXT,
        Product_No TEXT,

        Patent_No TEXT,
        Patent_Expire_Date_Text TEXT,

        Drug_Substance_Flag TEXT,
        Drug_Product_Flag TEXT,

        Patent_Use_Code TEXT,

        Delist_Flag TEXT,

        Submission_Date TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orange_exclusivity (

        Appl_Type TEXT,
        Appl_No TEXT,
        Product_No TEXT,

        Exclusivity_Code TEXT,
        Exclusivity_Date TEXT
    )
    """)

    # ============================================================
    # INDEXES - DRUGS@FDA
    # ============================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_drugname
        ON products(DrugName)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_activeingredient
        ON products(ActiveIngredient)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_products_applno
        ON products(ApplNo)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_submissions_applno
        ON submissions(ApplNo)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_marketing_appl_product
        ON marketing_status(ApplNo, ProductNo)
    """)

    # ============================================================
    # INDEXES - ORANGE BOOK
    # ============================================================

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ob_appl
        ON orange_products(Appl_No)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ob_trade
        ON orange_products(Trade_Name)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ob_ingredient
        ON orange_products(Ingredient)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_ob_lookup
        ON orange_products(Appl_No, Product_No)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_pat_lookup
        ON orange_patents(Appl_No, Product_No)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_exc_lookup
        ON orange_exclusivity(Appl_No, Product_No)
    """)

    conn.commit()
    conn.close()

    print("✅ Database schema created successfully!")


if __name__ == "__main__":
    create_tables()