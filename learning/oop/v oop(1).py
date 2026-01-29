class Person:
    def __init__(self, name , age):
        self.name = name
        self.age = age
    
    def helo(self):
        print(f"My name is {self.name} and I am {self.age} years old")

    def birtday(self):
        self.age += 1
        
        
p1 = Person("Ali", 20)
p2 = Person("Abood", 23)
p3 = Person("Ahmad", 30)

p1.helo()
p2.helo()
p3.helo()
p3.birtday()
p3.helo()