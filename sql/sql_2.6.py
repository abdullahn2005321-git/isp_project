#المستوى 6 — التجميع والتقارير (COUNT / GROUP BY / HAVING)
import sqlite3

conn = sqlite3.connect("practice.db")
cur = conn.cursor()


print("\nAll")
cur.execute("SELECT COUNT(*) FROM users_safe")
print(cur.fetchone())


print("\n area")
cur.execute("""
SELECT area, COUNT(*) AS total
FROM users_safe
GROUP BY area
ORDER BY total DESC
""")
print(cur.fetchone())


print("\n area_2")
cur.execute("""
SELECT area, COUNT(*) AS total
FROM users_safe
GROUP BY area
HAVING COUNT(*) >= 3
""")
print(cur.fetchone())

print("\n(A/M2)")
cur.execute("""
SELECT
  area,
  COUNT(*) AS total,
  AVG(age) AS avg_age,
  MIN(age) AS min_age
FROM users_safe
GROUP BY area
""")
print(cur.fetchall())

cur.execute("""
SELECT area, full_name, COUNT(*) AS total
FROM users_safe
GROUP BY area, full_name;
""")
print(cur.fetchall())


conn.close()