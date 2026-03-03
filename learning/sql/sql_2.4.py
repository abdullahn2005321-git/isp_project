import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()

cur.execute("SELECT * FROM users")
print(cur.fetchall())

cur.execute("""
UPDATE users
SET phone = ?
WHERE phone LIKE ?
""", ("", "0770%"))
conn.commit()
print("\nUpdate done, affected rows:", cur.rowcount)

cur.execute("DELETE FROM users WHERE id = ?", (45,))
conn.commit()
print("\nDelete done, affected rows:", cur.rowcount)

cur.execute("SELECT * FROM users")
print(cur.fetchall())

conn.close()
