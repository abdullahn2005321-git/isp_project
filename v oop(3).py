class Student:
    def __init__(self, name, age, grade):
        self.name = name
        self.age = age
        self.grade = grade
    
    def to_dict(self):
        return {
            "name": self.name,
            "age": self.age,
            "grade": self.grade
        }

class School:
    def __init__(self):
        self.students = []
    
    def add_student(self, student):
        self.students.append(student)

    def list_students(self):
        for s in self.students:
            print(f"{s.name} - Age: {s.age} - Grade: {s.grade}")

    def remove_student(self, name):
        self.students = [s for s in self.students if s.name != name]

school1 = School()
school1.add_student(Student("abood", 20, 95))
school1.add_student(Student("sara", 19, 90))
school1.list_students()