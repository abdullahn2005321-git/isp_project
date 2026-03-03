import os
import sqlite3

conn = sqlite3.connect(os.path.join(os.path.dirname(__file__), "db", "practice.db"))
cur = conn.cursor()

cur.execute("""
SELECT u.id, u.full_name
FROM users_safe u
LEFT JOIN tasks t ON u.id = t.user_id
WHERE t.id IS NULL
ORDER BY u.id;
""")
print(cur.fetchall())

conn.close()
