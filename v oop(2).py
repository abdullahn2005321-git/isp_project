class Car:
    def __init__(self, brand, model):
        self.brand = brand
        self.model = model
        self.speed = 0

    def accelerate(self):
        self.speed += 10
        
    
    
    def brake(self):
        self.speed -= 10
        if self.speed < 0:
            self.speed = 0
    

    def info(self):

        print(f"The car is {self.brand} and {self.model} and the speed {self.speed}")


c1 = Car("tesla", "sabr")
c2 = Car("Toyota", "Corolla")

c1.info()
c1.brake()
c1.info()
c1.brake()
c2.info()
