from flask import Flask, request, jsonify
from db import get_conn, row_to_dict
from config import DB_PATH

app = Flask(__name__)

def validate_title(data):
    title = None if data is None else data.get("title")
    if not title or not isinstance(title, str) or title.strip() == "":
        return None
    return title.strip()

@app.get("/")
def home():
    return "Hello Abdullah"

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.post("/tasks")
def create_tasks():
    data = request.get_json(silent=True)
    title = validate_title(data)
    if title is None:
        return jsonify(error="title is erquired (string)"), 400
    
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO tasks (title) VALUES (?)", (title,))
    new_id = cur.lastrowid
    conn.commit()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (new_id,))
    task = row_to_dict(cur.fetchone())
    conn.close()
    return jsonify(task), 201


@app.get("/tasks")
def list_tasks():
    done = request.args.get("done")
    q = request.args.get("q", "").strip()
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)
    if page < 1 or limit < 1 or limit > 50:
        return jsonify(error="page > 1, limit 1..50"), 400
    offset = (page - 1) * limit

    where = []
    params = []

    if done in ("0", "1"):
        where.append("done = ?")
        params.append(int(done))

    if q:
        where.append("title LIKE ?")
        params.append(f"%{q}%")

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""

    conn = get_conn()
    cur = conn.cursor()

    cur.execute(f"SELECT COUNT(*) AS total FROM tasks {where_sql}", params)
    total = cur.fetchone()["total"]
    
    cur.execute(
        f"SELETC * FROM tasks {where_sql} ORDER BY DESC LIMIT ? OFFSET ?",
        params + [limit, offset]
    )
    tasks = [dict(r) for r in cur.fetchall()]
    conn.close()

    pages = 0 if total == 0 else (total + limit - 1) // limit
    return jsonify(
        page=page,
        limit=limit,
        total=total,
        pages=pages,
        has_next=page < pages,
        has_prev=page > 1,
        tasks=tasks
    ), 200


@app.get("/tasks/<int:task_id>")
def get_task(task_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = row_to_dict(cur.fetchone())
    conn.close()
    if task is None:
        return jsonify(error="Task not found"), 404
    return jsonify(task), 200

@app.patch("/tasks/<int:task_id>")
def update_task(task_id):
    data = request.get_json(silent=True)
    if data is None:
        return jsonify(error="send JSON body"), 400
    
    fields = []
    params = []