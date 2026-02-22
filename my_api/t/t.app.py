from flask import Flask, jsonify, request

app = Flask(__name__)

@app.get("/")
def home():
    return "Hello Abdullah ✅", 200

@app.get("/health")
def health():
    return jsonify(status="ok"), 200

@app.errorhandler(404)
def not_found(e):
    return jsonify(error="Route not found", path=request.path), 404

@app.route("/echo", methods=["GET", "POST"])
def echo():
    if request.method == "GET":
        return "Use POST with JSON body", 200


    data = request.get_json(silent=True)
    if data is None:
        return jsonify(error="Send JSON body"), 400
    return jsonify(you_sent=data), 200


@app.post("/sum")
def sum_numbers():
    data = request.get_json(silent=True)

    if data is None:
        return jsonify(error="send JSON body"), 400

    a = data.get("a")
    b = data.get("b")
    if not isinstance(a, int)or not isinstance(b, int):
        return jsonify(error="a and b must be integers"), 400
        
    return jsonify(result=a + b), 200




if __name__ == "__main__":
    app.run(debug=True)