from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello Abdullah", 200

# ====== In-memory "DB" ======
USERS = []
NEXT_ID = 1

def _find_user(user_id: int):
    return next((u for u in USERS if u["id"] == user_id), None)

def _validate_name(data):
    name = None if data is None else data.get("name")
    if not name or not isinstance(name, str) or name.strip() == "":
        return None
    return name.strip()

# ====== Users CRUD ======
@app.get("/users")
def list_users():
    return jsonify(users=USERS, total=len(USERS)), 200

@app.post("/users")
def create_user():
    global NEXT_ID
    data = request.get_json(silent=True)

    name = _validate_name(data)
    if name is None:
        return jsonify(error="name is required and must be a non-empty string"), 400

    user = {"id": NEXT_ID, "name": name}
    NEXT_ID += 1
    USERS.append(user)
    return jsonify(user=user), 201

@app.get("/users/<int:user_id>")
def get_user(user_id):
    user = _find_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404
    return jsonify(user=user), 200

@app.put("/users/<int:user_id>")
def update_user(user_id):
    user = _find_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404

    data = request.get_json(silent=True)
    name = _validate_name(data)
    if name is None:
        return jsonify(error="name is required and must be a non-empty string"), 400

    user["name"] = name
    return jsonify(user=user), 200

@app.delete("/users/<int:user_id>")
def delete_user(user_id):
    user = _find_user(user_id)
    if user is None:
        return jsonify(error="User not found"), 404

    USERS.remove(user)
    return jsonify(message="Deleted"), 200





if __name__ == "__main__":
    app.run(debug=True)