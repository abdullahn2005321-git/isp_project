from flask import Flask, jsonify, request
import sqlite3

app = Flask(__name__)

DB_PATH = "app.db"


# ====== DB Helpers ======
def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def validate_name(data):
    name = None if data is None else data.get("name")
    if not name or not isinstance(name, str) or name.strip() == "":
        return None
    return name.strip()


# ====== Basic Routes ======
@app.get("/")
def home():
    return "Hello Abdullah ✅", 200


@app.get("/health")
def health():
    return jsonify(status="ok"), 200


@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Route not found", path=request.path), 404


# ====== Users CRUD (SQLite) ======
@app.get("/users")
def list_users():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users ORDER BY id")
    rows = cur.fetchall()
    conn.close()

    users = [dict(r) for r in rows]
    return jsonify(users=users, total=len(users)), 200


@app.post("/users")
def create_user():
    data = request.get_json(silent=True)
    name = validate_name(data)
    if name is None:
        return jsonify(error="name is required and must be a non-empty string"), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (name) VALUES (?)", (name,))
    conn.commit()
    new_id = cur.lastrowid
    conn.close()

    return jsonify(user={"id": new_id, "name": name}), 201


@app.get("/users/<int:user_id>")
def get_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify(error="User not found"), 404
    return jsonify(user=dict(row)), 200


@app.put("/users/<int:user_id>")
def update_user(user_id):
    data = request.get_json(silent=True)
    name = validate_name(data)
    if name is None:
        return jsonify(error="name is required and must be a non-empty string"), 400

    conn = get_conn()
    cur = conn.cursor()
    cur.execute("UPDATE users SET name = ? WHERE id = ?", (name, user_id))
    conn.commit()
    changed = cur.rowcount
    conn.close()

    if changed == 0:
        return jsonify(error="User not found"), 404

    return jsonify(user={"id": user_id, "name": name}), 200


@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    deleted = cur.rowcount
    conn.close()

    if deleted == 0:
        return jsonify(error="User not found"), 404

    return jsonify(message="Deleted"), 200


if __name__ == "__main__":
    init_db()
    app.run(debug=True)

