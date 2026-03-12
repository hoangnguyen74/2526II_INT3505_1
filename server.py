from flask import Flask, request, jsonify, make_response
import time

app = Flask(__name__)

cameras = [
    {"id": 1, "name": "Camera Gate"},
    {"id": 2, "name": "Camera Lobby"}
]


# =========================
# Layer: Logging Middleware
# =========================
@app.before_request
def log_request():
    print(f"[Layer] Incoming request: {request.method} {request.path}")


@app.after_request
def log_response(response):
    print(f"[Layer] Response status: {response.status}")
    return response


# =========================
# Auth Layer
# =========================
def authenticate():
    token = request.headers.get("Authorization")
    return token == "Bearer secret123"


# =========================
# API Layer
# =========================
@app.route("/cameras", methods=["GET"])
def get_cameras():

    if not authenticate():
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    response = make_response(jsonify({
        "status": "success",
        "data": cameras
    }))

    # Cacheable
    response.headers["Cache-Control"] = "public, max-age=60"

    return response


@app.route("/cameras", methods=["POST"])
def create_camera():

    if not authenticate():
        return jsonify({
            "status": "error",
            "message": "Unauthorized"
        }), 401

    data = request.json

    new_camera = {
        "id": len(cameras) + 1,
        "name": data["name"]
    }

    cameras.append(new_camera)

    return jsonify({
        "status": "success",
        "data": new_camera
    }), 201

@app.route("/script", methods=["GET"])
def get_script():

    script = """
    console.log("Hello from server!");
    """

    response = make_response(script)
    response.headers["Content-Type"] = "application/javascript"

    return response

if __name__ == "__main__":
    app.run(port=5000, debug=True)