import os
import sqlite3
conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON")

cur.execute("SELECT COUNT(*) FROM tasks")
print("Tasks before", cur.fetchone()[0])

try:
    cur.execute("BEGIN;")

    cur.execute("INSERT INTO tasks (user_id, title, done) VALUES (?, ?, ?)", (1, "TEMP TASK", 0))

    cur.execute("INSERT INTO tasks (user_id, title, done) VALUES (?, ?, ?)", (9999, "BAD TASK", 0))

    conn.commit()

except Exception as e:
    print("Error happend -> rollback:", e)
    conn.rollback()

cur.execute("SELECT COUNT(*) FROM tasks")
print("Tasks after:", cur.fetchone()[0])
