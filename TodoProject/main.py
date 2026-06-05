import sqlite3

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
        self.conn = sqlite3.connect("todo.db", check_same_thread=False)
        self.cur = self.conn.cursor()

        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TAXT NOT NULL,
                done INTEGER DEFAULT 0
            )
        """)

        self.conn.commit()
        print("🗄️ تم الاتصال بقاعدة البيانات وتجهيز الجدول بنجاح!")


    def get_all_tasks(self):

        self.cur.execute("SELECT id, title, done FROM tasks")
        rows = self.cur.fetchall()

        tasks_list = []
        for row in rows:

            task_dict = {
                "id" : row[0],
                "title": row[1],
                "done": bool(row[2])
            }
            tasks_list.append(task_dict)
        
        return tasks_list


    def add_task(self, title):

        self.cur.execute("INSERT INTO tasks (title) VALUES (?)", (title,))

        self.conn.commit()

        print(f"تمت الإضافة لقاعدة البيانات: {title}")
    
    def show_tasks(self):
        
        print("\n=== قائمة المهام من قاعدة البيانات ===")

        self.cur.execute("SELECT id, title, done FROM tasks")

        rows = self.cur.fetchall()

        if len(rows) == 0:

            print("قاعدة البيانات فارغة، لا يوجد مهام حالياً.")

        else:
            for row in rows:
                task_id = row[0]
                task_title = row[1]
                task_done = row[2]
                
                task = Task(task_id, task_title)
                task.done = bool(task_done)
                print(task)

        print("==============================================\n")


    def mark_task_done(self, task_id):
        self.cur.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))

        if self.cur.rowcount > 0:
            self.conn.commit()
            print(f"✅ تم إنجاز المهمة رقم {task_id} بنجاح!")
        
        else:
            print(f"⚠️ عذراً، المهمة رقم {task_id} غير موجودة.")
    

    def update_task(self, task_id, new_title):
        self.cur.execute("UPDATE tasks SET title = ? WHERE id = ?", (new_title, task_id))

        if self.cur.rowcount > 0:
            self.conn.commit()
            print(f"✅ تم بنجاح تحديث عنوان المهمه الى {new_title}")

        else:
            print(f"⚠️ عذراً، المهمة رقم {task_id} غير موجودة.")


    def delete_task(self, task_id):
        self.cur.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        if self.cur.rowcount > 0:
            self.conn.commit()
            print(f"🗑️ تم حذف المهمة رقم {task_id} نهائياً.")
        else:
            print(f"⚠️ عذراً، لا يمكن الحذف. المهمة رقم {task_id} غير موجودة.")


