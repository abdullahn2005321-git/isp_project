class BankAccount:

    def __init__(self, balance):
        if balance < 0:
            raise ValueError("Balance cannot be negative")
        self.__balance = balance

    def deposit(self, amount):
        if amount > 0:
            self.__balance += amount
        else:
            print("Invalid deposit amount")

    def withdraw(self, amount):
        if amount <= self.__balance:
            self.__balance -= amount
        else:
            print("Balance is insufficient")

    def get_balance(self):
        return self.__balance


b1 = BankAccount(200)

b1.deposit(100)
b1.withdraw(200)

print(b1.get_balance())
