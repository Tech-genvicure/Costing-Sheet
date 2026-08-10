import sqlite3

conn = sqlite3.connect("data/ai_cache.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS ai_cost_cache")

conn.commit()
conn.close()

print("AI Cache reset successfully.")
