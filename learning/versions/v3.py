import csv
import os

file_path = os.path.join(os.path.dirname(__file__), "subs.csv")

if not os.path.exists(file_path):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["name", "email", "ip"])

name = input("enter name: ").strip()
email = input("enter email: ").strip()
ip = input("enter ip: ").strip()

with open(file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    ex = [row["name"].lower() for row in reader]

if name =="":
    print("Name cannot be empty!")
elif name.lower() in ex:
    print("Name already exists!")
else:
    with open(file_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([name, email, ip])
    print("Added successfully!")
