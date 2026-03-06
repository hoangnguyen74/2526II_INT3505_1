from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

cameras = [
    {"id": 1, "name": "Camera Gate"},
    {"id": 2, "name": "Camera Lobby"}
]


def authenticate():
    token = request.headers.get("Authorization")
    return token == "Bearer secret123"


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


if __name__ == "__main__":
    app.run(port=5000, debug=True)
