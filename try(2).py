names = ["abood", "sara", "ali"]

try:
    i = int(input("Enter index: "))
    print(names[i])
except IndexError:
    print("name dont exsist")
except ValueError:
    print("entar num only")

