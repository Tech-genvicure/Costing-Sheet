"""
FDA Drugs@FDA Importer
Imports FDA TXT files into SQLite.

Author: Genvicure
"""

import csv
import sqlite3
from pathlib import Path

# ============================================================
# CONFIG
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = BASE_DIR / "pharma.db"
RAW_DATA = BASE_DIR / "raw"

FILES = {
    # ============================
    # Drugs@FDA
    # ============================
    "applications": "Applications.txt",
    "products": "Products.txt",
    "submissions": "Submissions.txt",
    "marketing_status": "MarketingStatus.txt",

    # ============================
    # Orange Book
    # ============================
    "orange_products": "orangebook/products.txt",
    "orange_patents": "orangebook/patent.txt",
    "orange_exclusivity": "orangebook/exclusivity.txt",
}

BATCH_SIZE = 5000


# ============================================================
# DATABASE
# ============================================================

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()


# ============================================================
# OPEN FILE WITH ENCODING DETECTION
# ============================================================

def open_file(file_path):
    """
    Open FDA file with automatic encoding detection.
    """

    encodings = [
        "utf-8-sig",
        "utf-8",
        "cp1252",
        "latin-1",
    ]

    for encoding in encodings:

        try:
            # Read the whole file once to verify encoding
            with open(file_path, "r", encoding=encoding) as test_file:
                test_file.read()

            print(f"   Using encoding: {encoding}")

            return open(file_path, "r", encoding=encoding)

        except UnicodeDecodeError:
            continue

    raise Exception(f"Cannot decode {file_path}")

# ============================================================
# IMPORT TABLE
# ============================================================

def import_table(table_name, filename):

    file_path = RAW_DATA / filename

    if not file_path.exists():
        print(f"❌ Missing file: {filename}")
        return

    print(f"\n📥 Importing {filename}")

    cursor.execute(f"DELETE FROM {table_name}")

    f = open_file(file_path)

    def get_delimiter(filename):

        if "orangebook" in filename.lower():
            return "~"

        return "\t"

    reader = csv.DictReader(
        f,
        delimiter=get_delimiter(filename)
    )

    COLUMN_RENAMES = {
        "orange_products": {
            "DF;Route": "DF_Route"
        }
    }

    # Read original headers from file
    original_columns = reader.fieldnames

    # Rename headers to match SQLite schema
    mapping = COLUMN_RENAMES.get(table_name, {})

    columns = [
        mapping.get(col, col)
        for col in original_columns
    ]

    placeholders = ",".join(["?"] * len(columns))

    sql = f"""
        INSERT INTO {table_name}
        ({",".join(columns)})
        VALUES ({placeholders})
    """

    batch = []

    total = 0

    for row in reader:

        # Use ORIGINAL headers to read the file values
        batch.append(
            tuple(row[col] for col in original_columns)
        )

        if len(batch) >= BATCH_SIZE:

            cursor.executemany(sql, batch)

            conn.commit()

            total += len(batch)

            print(f"   Imported {total:,} rows...")

            batch.clear()

    if batch:

        cursor.executemany(sql, batch)

        conn.commit()

        total += len(batch)

    f.close()

    print(f"✅ Finished {table_name}: {total:,} rows")


# ============================================================
# VERIFY
# ============================================================

def verify():

    print("\n" + "=" * 60)
    print("DATABASE SUMMARY")
    print("=" * 60)

    for table in FILES.keys():

        cursor.execute(f"SELECT COUNT(*) FROM {table}")

        count = cursor.fetchone()[0]

        print(f"{table:<20} {count:,} rows")


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("FDA DATABASE IMPORT")
    print("=" * 60)

    for table, filename in FILES.items():

        try:

            import_table(table, filename)

        except Exception as e:

            print(f"\n❌ Failed importing {filename}")

            print(e)

    verify()

    print("\n🧹 Optimizing database...")
    conn.execute("VACUUM")

    conn.close()

    print("\n🎉 Import Complete!")


if __name__ == "__main__":
    main()