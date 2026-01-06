import csv

query = input("search name or ip: ").strip().lower()
with open("subs.csv", "r") as f:
    reader = csv.DictReader(f)
    results = [row for row in reader if query in row["name"].lower() or query in row["ip"].lower()]

for r in results:
    print(r)
if not results:
    print("No matches")

