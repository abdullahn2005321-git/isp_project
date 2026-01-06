name = input("Enter new subscriber name:").strip()


if name == "":
    print("Name cannot be empty!")

else:
    with open("subs.txt", "r") as f:
        lines = f.readlines()

    clean_names = [line.strip() for line in lines]
    lower_names = [n.lower() for n in clean_names]

    if name.lower() in lower_names:
        print("Name already exists!")
    
    else:
        with open("subs.txt", "a") as f:
            f.write(name + "\n")

        with open("subs.txt", "r") as f:
            lines = f.readlines()

        count = 1
        for line in lines:
            print(f"{count} ) {line.strip()}")
            count += 1
