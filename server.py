from flask import Flask, request, jsonify, make_response

app = Flask(__name__)

cameras = [
    {"id": 1, "name": "Camera Gate"},
    {"id": 2, "name": "Camera Lobby"}
]


def authenticate():
    token = request.headers.get("Authorization")

    if token != "Bearer secret123":
        return False
    return True


@app.route("/cameras", methods=["GET"])
def get_cameras():

    if not authenticate():
        return jsonify({"error": "Unauthorized"}), 401

    response = make_response(jsonify({
        "data": cameras
    }))

    # cache 60 seconds
    response.headers["Cache-Control"] = "public, max-age=60"

    return response


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
