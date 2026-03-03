import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "vocab.db"))
cur = conn.cursor()

cur.execute("SELECT * FROM users WHERE id = ?", (2,))
print(cur.fetchall())

conn.close()
