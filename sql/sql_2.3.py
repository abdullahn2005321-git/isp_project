#المستوى 3 — الفلترة والترتيب (WHERE مثل if)
import sqlite3

conn = sqlite3.connect("practice.db")
cur = conn.cursor()

print("\n1) كل البيانات:")
cur.execute("SELECT * FROM users")
print(cur.fetchall())

print("\n2) فقط عندما يكون اسم عبدالله:")
cur.execute("SELECT * FROM users WHERE full_name = ?", ("Abdullah Ali",))
print(cur.fetchall())

print("\n3) يحتوي على AH:")
cur.execute("SELECT * FROM users WHERE full_name LIKE ?", ("%Ah%",))
print(cur.fetchall())

print("\n4) اخر صف :")
cur.execute("SELECT * FROM users ORDER BY id ASC LIMIT 2")
print(cur.fetchall())

print("\n5) احمد و رقم 0770:")
cur.execute("""
SELECT * FROM users
WHERE phone LIKE ?
""", ("0770%",))
print(cur.fetchall())

conn.close()