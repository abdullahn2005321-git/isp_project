import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON")

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

required_ids = [1, 2, 3, 5, 8]
placeholders = ",".join(["?"] * len(required_ids))
cur.execute(f"SELECT id FROM users_safe WHERE id IN ({placeholders})", required_ids)
existing = {row[0] for row in cur.fetchall()}

seed = [
    (1, "User 1", "u1@mail.com", "07700000001", "Baghdad", 20),
    (2, "User 2", "u2@mail.com", "07700000002", "Basra", 22),
    (3, "User 3", "u3@mail.com", "07700000003", "Erbil", 21),
    (5, "User 5", "u5@mail.com", "07700000005", "Najaf", 25),
    (8, "User 8", "u8@mail.com", "07700000008", "Baghdad", 30),
]
for row in seed:
    if row[0] not in existing:
        cur.execute("""
        INSERT INTO users_safe (id, full_name, email, phone, area, age)
        VALUES (?, ?, ?, ?, ?, ?)
        """, row)
conn.commit()

cur.execute("DROP TABLE IF EXISTS tasks")
conn.commit()

cur.execute("""
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    done INTEGER DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users_safe(id)
)
""")
conn.commit()

tasks = [
    (1, "Add 3 users to DB",           1),
    (1, "Write SELECT with WHERE",     0),
    (2, "Practice ORDER BY and LIMIT", 1),
    (3, "Create tasks table",          1),
    (5, "Test UNIQUE and NOT NULL",    0),
    (5, "Make GROUP BY report",        0),
    (8, "Review SQLite vocab",         1),
]

cur.executemany("INSERT INTO tasks (user_id, title, done) VALUES (?, ?, ?)", tasks)
conn.commit()


cur.execute("SELECT * FROM tasks ORDER BY id")
print(cur.fetchall())

conn.close()
