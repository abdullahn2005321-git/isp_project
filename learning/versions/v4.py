import csv
import os

file_path = os.path.join(os.path.dirname(__file__), "subs.csv")

if not os.path.exists(file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "ip"])

query = input("search name or ip: ").strip().lower()
with open(file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    results = [row for row in reader if query in row["name"].lower() or query in row["ip"].lower()]

for r in results:
    print(r)
if not results:
    print("No matches")

