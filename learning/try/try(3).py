while True:
    try:
        age = int(input("Enter the age: "))

        if age < 18:
            raise ValueError("age must be 18 or older")
    except ValueError as e:
        print("Error", e)
    else:
        print("welcome!")
        break