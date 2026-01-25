#المستوى 4 — تحديث وحذف (تكملة CRUD)
import sqlite3

conn = sqlite3.connect("practice.db")
cur = conn.cursor()

cur.execute("SELECT * FROM users")
print(cur.fetchall())

cur.execute("""
UPDATE users
SET phone = ?
WHERE phone LIKE ?
""", ("","0770%"))
conn.commit()
print("\n update done, affected rows:", cur.rowcount)

cur.execute("DELETE FROM users WHERE id = ?", (45,))
conn.commit()
print("\n delete done, affected rows:", cur.rowcount)

cur.execute("SELECT * FROM users")
print(cur.fetchall())

conn.close()