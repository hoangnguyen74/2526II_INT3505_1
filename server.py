from flask import Flask, request, jsonify

app = Flask(__name__)

# fake database
cameras = [
    {"id": 1, "name": "Camera Gate"},
    {"id": 2, "name": "Camera Lobby"}
]


# middleware kiểm tra token
def authenticate():
    token = request.headers.get("Authorization")

    if token != "Bearer secret123":
        return False
    return True


# ========================
# GET cameras
# ========================
@app.route("/cameras", methods=["GET"])
def get_cameras():

    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "data": cameras
    })


# ========================
# POST camera
# ========================
@app.route("/cameras", methods=["POST"])
def create_camera():

    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json

    new_camera = {
        "id": len(cameras) + 1,
        "name": data["name"]
    }

    cameras.append(new_camera)

    return jsonify(new_camera), 201


if __name__ == "__main__":
    app.run(port=5000, debug=True)
