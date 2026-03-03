import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users_safe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    area TEXT DEFAULT 'Unknown',
    age INTEGER CHECK(age >= 18)
)
""")
conn.commit()


try:
    cur.execute("""
    INSERT INTO users_safe (full_name, email, phone, area, age)
    VALUES (?, ?, ?, ?, ?)
    """, ("Hasan", "", "07705555555", "pop", 19))
    conn.commit()
    print("Insert OK")
except sqlite3.IntegrityError as e:
    print("Blocked by constraint:", e)

cur.execute("SELECT * FROM users_safe")
print(cur.fetchall())

conn.close()
