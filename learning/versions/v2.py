import csv
import os

file_path = os.path.join(os.path.dirname(__file__), "subs.csv")

with open(file_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "email", "ip"])
    writer.writerow(["ali", "ali@gmail.com", "192.186.1.1"])
    writer.writerow(["hassan","gassan@gmail.com", "192.186.1.1"])

with open(file_path, "a", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["omar", "omar@gmail.com", "192.168.1.3"])


with open(file_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']} - {row['email']} - {row['ip']}")
