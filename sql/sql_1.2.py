import sqlite3

conn = sqlite3.connect("vocab.db")
cur = conn.cursor()

cur.execute("SELECT * FROM users WHERE id = ?", (2,))
print(cur.fetchall())

conn.close()