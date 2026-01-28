import sqlite3

conn = sqlite3.connect("practice.db")
cur = conn.cursor()

cur.execute("PRAGMA foreign_keys = ON")

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
