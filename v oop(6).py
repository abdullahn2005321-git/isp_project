class Person:
    def __init__(self,name, age):
        self.name = name
        self.age = age
    
    def say_hello(self):
        print(f"Hello my name {self.name} and my age {self.age}")


class Employee(Person):
    def __init__(self, name, age, salary):
        super().__init__(name, age)
        self.salary = salary
    
    def info(self):
        self.say_hello()
        print(f"my salary is {self.salary}")

e1 = Employee("Ali", 22, 86)
e2 = Employee("Sara",19, 95)
e2.info()