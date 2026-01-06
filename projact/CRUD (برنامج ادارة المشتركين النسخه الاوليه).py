import json
import os

file = "subs.json"

if not os.path.exists(file):
    with open(file, "w") as f:
        json.dump([],f)

#اضافه مشتركين
def add_subscriber():
    name = input("enter name: ").strip()
    ip = input("enter ip").strip()

    with open(file, "r") as f:
        subs = json.load(f)
    
    names = [s["name"].lower() for s in subs]

    if name == "":
        print("Name cannot be empty!")
        return
    elif name.lower() in names:
        print("Name already exists!")
        return
    
    subs.append({"name": name, "ip":ip})

    with open(file, "w") as f:
        json.dump(subs, f, indent=4)

    print(f"{name} added successfully!")

#قائمه المشتركين
def list_subscribers():
    with open(file, "r") as f:
        subs = json.load(f)

    if not subs:
        print("No subs yet")
        return

    for i, s in enumerate(subs, start=1):
        print(f"{i}) {s['name']} - {s['ip']}")

#بحث عن مشترك
def search_subscriber():
    query = input("Search by name or IP: ").strip().lower()
    with open(file, "r") as f:
        subs = json.load(f)
    
    results = [s for s in subs if query in s["name"].lower() or query in s["ip"]]

    if not results:
        print("No matches found.")
    else:
        for s in results:
            print(f"{s['name']} - {s['ip']}")

#تعديل مشترك
def update_subscriber():
    targrt = input("Enter name to update: ").strip().lower()
    new_name = input("New name (leave empty to keep same): ").strip()
    new_ip = input("New IP (leave empty to keep same): ").strip()

    with open(file, "r") as f:
        subs = json.load(f)

    found = False
    for s in subs:
        if s["name"].lower() == targrt:
            if new_name:
                s["name"] = new_name
            if new_ip:
                s["ip"] = new_ip
            found = True
            break
    
    if not found:
        print("Subscriber not found.")
        return
    
    with open(file, "w") as f:
        json.dump(subs, f, indent=4)
    print("Subscriber updated successfully!")

#حذف مشترك
def delete_subscriber():
    target = input("Enter name to delete: ").strip().lower()

    with open(file, "r") as f:
        subs = json.load(f)
    
    new_subs = [s for s in subs if s["name"].lower() != target]

    if len(new_subs) == len(subs):
        print("Subscriber not found.")
        return
    
    with open(file, "w") as f:
        json.dump(new_subs, f, indent=4)
    print("Subscriber deleted successfully!")

#menu
def menu():
    while True:
        print("\n--- Subscriber Manager ---")
        print("1) List subscribers")
        print("2) Add subscriber")
        print("3) Search subscriber")
        print("4) Update subscriber")
        print("5) Delete subscriber")
        print("0) Exit")

        choice = input("choice an option: ").strip()

        if choice == "1":
            list_subscribers()
        elif choice == "2":
            add_subscriber()
        elif choice == "3":
            search_subscriber()
        elif choice == "4":
            update_subscriber()
        elif choice == "5":
            delete_subscriber()
        elif choice == "0":
            print("Bye!")
            break
        else:
            print("Invalid choice, try again.")
menu()