from flask import Flask, jsonify, request
from db import init_db
from users_routes import users_bp


app = Flask(__name__)

@app.get("/")
def home():
    return "Hello Abdullah", 200

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Route not found", path=request.path), 404

app.register_blueprint(users_bp)


DEMO_USER = {
    "username": "abdullah",
    "password": "1234"
}

DEMO_TOKEN = "abc123-demo-token"

@app.post("/login")
def login():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify(error="send JSON body"), 400

    username = data.get("username")
    password = data.get("password")

    if username ==DEMO_USER["username"] and password == DEMO_USER["password"]:
        return jsonify(token=DEMO_TOKEN, token_type="Bearer"), 200
    
    return jsonify(error="Invalid username or password"), 401


@app.get("/me")
def me():
    auth_header = request.headers.get("Authorization", "")

    if not auth_header.startswith("Bearer "):
        return jsonify(error="Missing or invalid Authorization header"), 401
    
    token = auth_header.split(" ", 1)[1]

    if token != DEMO_TOKEN:
        return jsonify(error="Invalid token"), 401
    
    return jsonify(user={"username": DEMO_USER["username"]}), 200




if __name__ == "__main__":
    init_db()
    app.run(debug=True)
