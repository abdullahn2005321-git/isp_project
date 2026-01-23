import sqlite3

conn = sqlite3.connect("vocab.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
conn.commit()

cur.execute("INSERT INTO users (name) VALUES (?)", ("Ali",))
conn.commit()

cur.execute("SELECT * FROM users")
print(cur.fetchall())

conn.close()