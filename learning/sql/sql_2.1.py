import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()

cur.execute("SELECT 99")

print("Result:", cur.fetchone())

conn.commit()

conn.close()
