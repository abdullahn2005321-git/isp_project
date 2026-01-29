class Person:
    def __init__(self, name, age):
        self.name = name
        self.age = age
    
    def role(self):
        print(f"hello, my name is {self.name} and my age {self.age}")


class Student(Person):
    def __init__(self, name, age, grade):
        super().__init__(name, age)
        self.grade = grade
    
    def role(self):
        super().role()
        print(f"and my grade {self.grade}")

class Employee(Person):
    def __init__(self, name, age, salary):
        super().__init__(name, age)
        self.salary = salary
    
    def role(self):
        super().role()
        print(f"and my salary {self.salary}")
    
s1 = Student("sara", 19, 100)
s2 = Student("Ali", 22, 90)
e1 = Employee("Abdullah", 21, 10000)
e2 = Employee("Ahmad", 23, 5000)

s2.role()
e1.role()
