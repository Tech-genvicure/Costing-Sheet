import sqlite3

DB_PATH = "data/pharma.db"

conn = sqlite3.connect(DB_PATH)

with open("app/database/schema.sql", "r") as file:
    schema = file.read()

conn.executescript(schema)

conn.commit()
conn.close()

print("Database and tables created successfully.")