import sqlite3

conn = sqlite3.connect("app/database/pharma.db")
conn.row_factory = sqlite3.Row

cursor = conn.cursor()

cursor.execute("""
SELECT
    ApplNo,
    DrugName,
    Strength,
    COUNT(*) AS occurrences
FROM products
GROUP BY
    ApplNo,
    DrugName,
    Strength
HAVING COUNT(*) > 1
ORDER BY occurrences DESC, ApplNo;
""")

rows = cursor.fetchall()

print(f"\nFound {len(rows)} duplicate product presentations\n")

for row in rows[:50]:
    print(dict(row))

conn.close()