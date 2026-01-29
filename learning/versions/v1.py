import os

file_path = os.path.join(os.path.dirname(__file__), "subs.txt")

if not os.path.exists(file_path):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("")

name = input("Enter new subscriber name: ").strip()


if name == "":
    print("Name cannot be empty!")

else:
    with open(file_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    clean_names = [line.strip() for line in lines]
    lower_names = [n.lower() for n in clean_names]

    if name.lower() in lower_names:
        print("Name already exists!")
    
    else:
        with open(file_path, "a", encoding="utf-8") as f:
            f.write(name + "\n")

        with open(file_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        count = 1
        for line in lines:
            print(f"{count} ) {line.strip()}")
            count += 1
