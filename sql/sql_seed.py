import sqlite3

conn = sqlite3.connect("practice.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users_safe (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT UNIQUE NOT NULL,
    area TEXT DEFAULT 'Unknown',
    age INTEGER CHECK(age >= 0)
)
""")
conn.commit()

# تنظيف البيانات القديمة حتى تصير النتائج ثابتة
cur.execute("DELETE FROM users_safe")
conn.commit()

users = [
    ("Abdullah Ali",   "u1@mail.com",  "07700000001", "Baghdad", 20),
    ("Omar Hassan",    "u2@mail.com",  "07700000002", "Basra",   22),
    ("Ahmad Kareem",   "u3@mail.com",  "07700000003", "Baghdad", 19),
    ("Sara Naser",     "u4@mail.com",  "07700000004", "Basra",   25),
    ("Huda Aziz",      "u5@mail.com",  "07700000005", "Erbil",   30),
    ("Ali Mahmood",    "u6@mail.com",  "07700000006", "Baghdad", 28),
    ("Zainab Salem",   "u7@mail.com",  "07700000007", "Najaf",   18),
    ("Hussein Jabbar", "u8@mail.com",  "07700000008", "Baghdad", 35),
    ("Maryam Qasim",   "u9@mail.com",  "07700000009", "Erbil",   24),
    ("Noor Yasin",     "u10@mail.com", "07700000010", "Basra",   21),
    ("Mustafa Adnan",  "u11@mail.com", "07700000011", "Najaf",   27),
    ("Rami Fadel",     "u12@mail.com", "07700000012", "Baghdad", 17),
]

cur.executemany("""
INSERT INTO users_safe (full_name, email, phone, area, age)
VALUES (?, ?, ?, ?, ?)
""", users)
conn.commit()

cur.execute("SELECT id, full_name, area, age FROM users_safe ORDER BY id")
print(cur.fetchall())

conn.close()
