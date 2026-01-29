import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()



cur.execute("SELECT * FROM users")
print(cur.fetchall())

cur.execute("SELECT * FROM users WHERE full_name = ?", ("Abdullah Ali",))
print(cur.fetchall())


cur.execute("SELECT * FROM users WHERE full_name LIKE ?", ("%Ah%",))
print(cur.fetchall())

cur.execute("SELECT * FROM users ORDER BY id ASC LIMIT 2")
print(cur.fetchall())

cur.execute("""
SELECT * FROM users
WHERE phone LIKE ?
""", ("0770%",))
print(cur.fetchall())

conn.close()
