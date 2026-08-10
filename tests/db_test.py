import sqlite3

conn = sqlite3.connect("data/ai_cache.db")

for row in conn.execute(
    "SELECT name FROM sqlite_master WHERE type='table';"
):
    print(row)

conn.close()