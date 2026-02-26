from flask import Blueprint, jsonify, request
from db import get_conn

users_bp = Blueprint("users", __name__)

def validate_name(data):
    name = None if data is None else data.get("name")
    if not name or not isinstance(name, str) or name.strip() == "":
        return None
    return name.strip()

@users_bp.get("/users")
def list_users():
    name_filter = request.args.get("name")
    sort = request.args.get("sort", "asc").lower()
    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 5, type=int)

    if sort not in ("asc", "desc"):
        return jsonify(error="sort must be 'asc' or 'desc'"), 400
    
    if page is None or page < 1:
        return jsonify(error="page must be an integer >= 1"), 400

    if limit is None or limit < 1 or limit > 50:
        return jsonify(error="limit must be an integer between 1 and 50"), 400
    
    offset = (page - 1) * limit

    conn = get_conn()
    cur = conn.cursor()

    if name_filter:
        cur.execute(
            f"SELECT COUNT(*) AS total FROM users WHERE name LIKE ?",
            (f"%{name_filter}%",)
        )
    else:
        cur.execute(f"SELECT COUNT(*) AS total FROM users")

    total = cur.fetchone()["total"]

    if name_filter:
        cur.execute(
            f"SELECT id, name FROM users WHERE name LIKE ? ORDER BY id {sort.upper()} LIMIT ? OFFSET ?",
            (f"%{name_filter}%", limit, offset)
        )
    else:
        cur.execute(
            f"SELECT id, name FROM users ORDER BY id {sort.upper()} LIMIT ? OFFSET ?",
            (limit, offset)
        )

    rows = cur.fetchall()
    conn.close()

    users = [dict(r) for r in rows]

    if total == 0:
        pages = 0

    else:
        pages = (total + limit - 1) // limit

    return jsonify(
        users=users,
        total=total,
        page=page,
        limit=limit,
        pages=pages,
        has_next=(page < pages),
        has_prev=(page > 1)
        ), 200

@users_bp.post("/users")
def create_users():
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

@users_bp.get("/users/<int:user_id>")
def get_user(user_id):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, name FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()

    if row is None:
        return jsonify(error="user not found"), 404
    return jsonify(user=dict(row)), 200

@users_bp.put("/users/<int:user_id>")
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


@users_bp.delete("/users/<int:user_id>")
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
