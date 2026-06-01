import json

class Task:
    def __init__(self, task_id, title):
        self.id = task_id
        self.title = title
        self.done = False
    
    def mark_done(self):
        self.done = True

    def __str__(self):
        status = "✅" if self.done else "❌"
        return f"{status} [{self.id}] {self.title}"

class TaskManager:
    def __init__(self):
        self.tasks = []
        self.next_id = 1
        self.lode_from_file()
    
    def add_task(self, title):
        new_task = Task(self.next_id, title)

        self.tasks.append(new_task)

        self.next_id += 1
        print(f"تمت اضافه: {title}")
    
    def show_tasks(self):
        print("\n======================")
        if not self.tasks:
            print("no itime here")
        else:
            for task in self.tasks:
                print(task)
        print("=======================\n")

    def mark_task_done(self, task_id):
        for task in self.tasks:
            if task.id == task_id:
                task.mark_done()
                print(f"تم إنجاز المهمة رقم {task_id} بنجاح! 🎉")
                return
        
        print(f"عذراً، المهمة رقم {task_id} غير موجودة.")

    def save_to_file(self):

        tasks_data = []

        for task in self.tasks:
            task_dict = {
                "id": task.id,
                "title": task.title,
                "done": task.done
            }
            tasks_data.append(task_dict)

        with open("tasks.json", "w", encoding="utf-8") as file:
            
            json.dump(tasks_data, file, ensure_ascii=False, indent=4)

        print("💾 تم حفظ المهام في ملف tasks.json بنجاح!")
    
    def lode_from_file(self):
        try:
            with open("tasks.json", "r", encoding="utf-8") as file:

                task_data = json.load(file)

                self.tasks = []

                for data in task_data:
                    restored_task = Task(data["id"], data["title"])

                    restored_task.done = data["done"]

                    self.tasks.append(restored_task)

                if self.tasks:
                    self.next_id = self.tasks[-1].id + 1

                print("📂 تم استرجاع المهام السابقة من الملف بنجاح!")

        except FileNotFoundError:

            print("⚠️ لم يتم العثور على ملف سابق، سنبدأ بقائمة فارغة.")


manager = TaskManager()

manager.show_tasks()

