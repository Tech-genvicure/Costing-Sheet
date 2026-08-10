import sqlite3

conn = sqlite3.connect("data/ai_cache.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS ai_cost_cache (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    application_no TEXT,

    brand_name TEXT,

    generic_name TEXT,

    api_name TEXT,

    dosage_form TEXT,

    route TEXT,

    manufacturer TEXT,

    analysis_json TEXT NOT NULL,

    created_at DATETIME DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()
conn.close()

print("AI Cache database created successfully.")