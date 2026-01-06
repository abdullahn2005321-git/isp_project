import csv

name = input("enter name: ").strip()
emali = input("enter email: ").strip()
ip = input("enter ip: ").strip()

with open("subs.csv", "r") as f:
    reader = csv.DictReader(f)
    ex = [row["name"].lower() for row in reader]

if name =="":
    print("Name cannot be empty!")
elif name.lower() in ex:
    print("Name already exists!")
else:
    with open("subs.csv", "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([name, emali, ip])
    print("Added successfully!")
