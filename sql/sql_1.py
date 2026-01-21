import sqlite3

conn = sqlite3.connect("vocab.db")
cur = conn.cursor()

cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT)")
conn.commit()

print("Table users reade")
conn.close()