from flask import Flask, request, jsonify, make_response
import time
from response import *

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
def get_all_cameras():

    if not authenticate():
        return error_response(HTTP_UNAUTHORIZED)

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
        return error_response(HTTP_UNAUTHORIZED)

    data = request.json

    new_camera = {
        "id": len(cameras) + 1,
        "name": data["name"]
    }

    cameras.append(new_camera)

    return success_response_with_data(HTTP_CREATED, new_camera)

@app.route("/script", methods=["GET"])
def get_script():

    script = """
    console.log("Hello from server!");
    """

    response = make_response(script)
    response.headers["Content-Type"] = "application/javascript"

    return response

@app.route("/cameras/<int:camera_id>", methods=["GET"])
def get_camera(camera_id):

    for cam in cameras:
        if cam["id"] == camera_id:
            return success_response_with_data(HTTP_OK, cam)

    return error_response(HTTP_NOT_FOUND)

@app.route("/cameras/<int:camera_id>", methods=["DELETE"])
def delete_camera(camera_id):

    global cameras
    cameras = [c for c in cameras if c["id"] != camera_id]

    return success_response(HTTP_OK)

if __name__ == "__main__":
    app.run(port=5000, debug=True)