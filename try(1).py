while True:
    try:
        x = int(input("entar num: "))

    except ValueError:
        print("error!!")

    else:
        print(x + 9)
        break