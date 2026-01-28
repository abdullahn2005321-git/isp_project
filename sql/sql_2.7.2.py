import sqlite3

conn = sqlite3.connect("practice.db")
cur = conn.cursor()
cur.execute("PRAGMA foreign_keys = ON;")

cur.execute("""
SELECT users_safe.full_name, tasks.title, tasks.done
FROM tasks
JOIN users_safe ON users_safe.id = tasks.user_id
ORDER BY users_safe.id, tasks.id;
""")

print(cur.fetchall())
conn.close()