import sqlite3

conn = sqlite3.connect("app/database/pharma.db")
conn.close()

print("Database created successfully!")

print("Database and tables created successfully.")