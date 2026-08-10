import sqlite3

conn = sqlite3.connect("data/dmf.db")

for row in conn.execute("PRAGMA table_info(dmf_holders)"):
    print(row)