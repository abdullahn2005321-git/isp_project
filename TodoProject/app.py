from flask import Flask, jsonify, request
from main import TaskManager

app = Flask(__name__)

app.json.ensure_ascii = False

manager = TaskManager()

@app.route("/")
def home():

    return "🚀 مرحباً بك في واجهة برمجة المهام (API) الخاصة بعبد الله!"

@app.route("/tasks", methods=["GET"])
def list_tasks():

    tasks = manager.get_all_tasks()

    return jsonify(tasks), 200

@app.route("/tasks", methods=["POST"])
def create_task():

    data = request.get_json()

    if not data or "title" not in data:

        return jsonify({"error": "الرجاء ارسال عنوان المهمه(title)"}), 400
    
    manager.add_task(data["title"])

    return jsonify({"message": "تمت إضافة المهمة بنجاح!"}), 201

@app.route("/tasks/<int:task_id>", methods=["DELETE"])
def remove_task(task_id):

    manager.delete_task(task_id)

    return jsonify ({"message": f"تم إرسال طلب الحذف للمهمة رقم {task_id}!"}), 200

@app.route("/tasks/<int:task_id>", methods=["PUT"])
def update_tasks(task_id):

    data = request.get_json()

    if not data or "title" not in data:

        return jsonify({"error": "الرجاء إرسال العنوان الجديد (title)"}), 400
    
    new_title = data["title"]

    manager.update_task(task_id, new_title)

    return jsonify ({"massage": f"تم بنجاح تحديث عنوان المهمه الى {new_title}"}), 200

@app.route("/tasks/<int:task_id>/complete", methods=["PUT"])
def complete_task(task_id):

    manager.mark_task_done(task_id)

    return jsonify({"massage":f"تم إرسال طلب التحديث للمهمة رقم {task_id}!"}), 200


if __name__ == "__main__":
    app.run(debug=True)