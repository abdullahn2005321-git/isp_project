from manager import SubscriberManager
from subscriber import Subscriber

def menu():
    manager = SubscriberManager("subs.json")

    while True:
        print("\n--- Subscriber Manager ---")
        print("1) List subscribers")
        print("2) Add subscriber")
        print("3) Search subscriber")
        print("4) Update subscriber (by number)")
        print("5) Delete subscriber (by name)")
        print("0) Exit")

        choice = input("choose an optine: ").strip()

        if choice == "1":
            manager.list_all()
        
        elif choice == "2":
            name = input("Enter name: ").strip()
            ip = input("Enter IP: ").strip()
            manager.add(Subscriber(name, ip))
            
        elif choice == "3":
            q = input("Search by name or IP: ").strip()
            results = manager.search(q)
            if not results:
                print("No matches found.")
            else:
                for s in results:
                    print(f"{s.name} - {s.ip}")

        elif choice == "4":
            manager.list_all()
            try:
                number = int(input("Enter subscriber number to update: ").strip())
            except ValueError:
                print("Invalid number.")
                continue

            new_name = input("New name (leave empty to keep same): ").strip()
            new_ip = input("New IP (leave empty to keep same): ").strip()
            manager.update_by_index(number, new_name=new_name, new_ip=new_ip)

        elif choice == "5":
            name = input("Enter name to delete: ").strip()
            manager.delete(name)

        elif choice == "0":
            print("Bye!")
            break

        else:
            print("Invalid choice, try again.")


if __name__ == "__main__":
    menu()