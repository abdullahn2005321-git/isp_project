#المستوى 1 — أساس الاتصال من بايثون (الأدوات الثلاثة)
import sqlite3

conn = sqlite3.connect("practice.db")
cur = conn.cursor()

cur.execute("SELECT 99")

print("Result:", cur.fetchone())

conn.commit()

conn.close()