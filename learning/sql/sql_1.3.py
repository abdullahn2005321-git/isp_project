import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "vocab.db"))
cur = conn.cursor()

cur.execute("UPDATE users SET name = ? WHERE id = ?", ("Ahmed", 1))
conn.commit()

cur.execute("DELETE FROM users WHERE id = ?", (2,))
conn.commit()

cur.execute("SELECT * FROM users")
print(cur.fetchall())

conn.close()
