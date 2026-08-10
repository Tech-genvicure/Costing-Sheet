import sqlite3
import pandas as pd

# ==========================================
# CONFIG
# ==========================================

EXCEL_FILE = "List of Drug Master Files (DMFs) 2nd Quarter 2026.xlsx"
DB_FILE = "data/dmf.db"

# ==========================================
# LOAD EXCEL
# ==========================================

df = pd.read_excel(
    EXCEL_FILE,
    sheet_name=0
)

# Remove empty rows
df = df.dropna(how="all")

# Standardize column names
df.columns = (
    df.columns
    .str.strip()
    .str.replace(" ", "_")
)

# ==========================================
# CREATE DATABASE
# ==========================================

conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

cursor.execute("""
DROP TABLE IF EXISTS dmf_holders
""")

cursor.execute("""
CREATE TABLE dmf_holders (

    DMF_No TEXT,

    Status TEXT,

    Type TEXT,

    Holder TEXT,

    Subject TEXT

)
""")

# ==========================================
# KEEP ONLY REQUIRED COLUMNS
# ==========================================

required = [
    "DMF#",
    "STATUS",
    "TYPE",
    "HOLDER",
    "SUBJECT"
]

df = df[required]

df.columns = [
    "DMF_No",
    "Status",
    "Type",
    "Holder",
    "Subject"
]

# ------------------------------------------
# Clean text
# ------------------------------------------

df["Holder"] = (
    df["Holder"]
    .astype(str)
    .str.strip()
)

df["Subject"] = (
    df["Subject"]
    .astype(str)
    .str.replace(r"\s+", " ", regex=True)
    .str.strip()
)

# ==========================================
# INSERT
# ==========================================

df.to_sql(
    "dmf_holders",
    conn,
    if_exists="append",
    index=False
)

conn.commit()
conn.close()

print("DMF database created successfully.")
print(f"Rows imported: {len(df)}")