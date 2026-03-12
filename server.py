from flask import Flask, request, jsonify, make_response
import time
from response import *

app = Flask(__name__)

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

@app.route("/script", methods=["GET"])
def get_script():

    script = """
    console.log("Hello from server!");
    """

    response = make_response(script)
    response.headers["Content-Type"] = "application/javascript"

    return response

# -------------------------------------- Camera -------------------------------

cameras = [
    {"id": 1, "name": "Camera Gate"},
    {"id": 2, "name": "Camera Lobby"}
]

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

# -------------------------------------- Robot -------------------------------

robots = [
    {"id": 1, "type": "Boston Dynamic", "name": "Dog for customer A"},
    {"id": 2, "type": "Boston Dynamic", "name": "Dog for customer B"},
    {"id": 3, "type": "UGO", "name": "Small device control A area"},
    {"id": 4, "type": "UGO", "name": "Small device control B area"}
]

@app.route("/robots", methods=["GET"])
def get_all_robots():

    if not authenticate():
        return error_response(HTTP_UNAUTHORIZED)

    response = make_response(jsonify({
        "status": "success",
        "data": robots
    }))

    # Cacheable
    response.headers["Cache-Control"] = "public, max-age=30"

    return response

@app.route("/robots", methods=["POST"])
def create_robot():

    if not authenticate():
        return error_response(HTTP_UNAUTHORIZED)

    data = request.json

    new_robot = {
        "id": len(cameras) + 1,
        "type": data["type"]
        "name": data["name"]
    }

    cameras.append(new_robot)

    return success_response_with_data(HTTP_CREATED, new_robot)

@app.route("/cameras/<int:camera_id>", methods=["GET"])
def get_robot(robot_id):

    for cam in robots:
        if cam["id"] == robot_id:
            return success_response_with_data(HTTP_OK, cam)

    return error_response(HTTP_NOT_FOUND)

@app.route("/robots/<int:robot_id>", methods=["DELETE"])
def delete_robot(robot_id):

    global robots
    robots = [r for r in robots if r["id"] != robot_id]

    return success_response(HTTP_OK)

if __name__ == "__main__":
    app.run(port=5000, debug=True)