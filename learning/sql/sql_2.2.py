import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    area TEXT NOT NULL,
    mother_name TEXT NOT NULL
)
""")

cur.execute("""
INSERT INTO users (full_name, email, phone, area, mother_name)
VALUES (?, ?, ?, ?, ?)
""", ("Abdullah Ali", "Abod@gmali.com", "07709514900", "Baghdad", "Fatima"))

cur.execute("""
INSERT INTO users (full_name, email, phone, area, mother_name)
VALUES (?, ?, ?, ?, ?)
""", ("Omar Hassan", "omar@gmali.com", "07701223308", "Basra", "Sara"))

cur.execute("""
INSERT INTO users (full_name, email, phone, area, mother_name)
VALUES (?, ?, ?, ?, ?)
""", ("Ahmad", "ahmad@gmali.com", "07708109109", "Arbel", "Zinab"))

# cur.execute("DELETE FROM users")

conn.commit()

cur.execute("SELECT * FROM users")
print(cur.fetchall())

cur.close()
