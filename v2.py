import csv

with open("subs.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "email", "ip"])
    writer.writerow(["ali", "ali@gmail.com", "192.186.1.1"])
    writer.writerow(["hassan","gassan@gmail.com", "192.186.1.1"])

with open("subs.csv", "a", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["omar", "omar@gmail.com", "192.168.1.3"])


with open("subs.csv", "r") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"{row['name']} - {row['email']} - {row['ip']}")