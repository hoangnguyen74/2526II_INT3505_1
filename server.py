from flask import Flask, jsonify, request

app = Flask(__name__)

cameras = [
    {"id": 1, "name": "Camera Gate"},
    {"id": 2, "name": "Camera Lobby"}
]

@app.route("/cameras", methods=["GET"])
def get_cameras():
    return jsonify(cameras)

@app.route("/cameras", methods=["POST"])
def create_camera():

    data = request.json

    new_camera = {
        "id": len(cameras) + 1,
        "name": data["name"]
    }

    cameras.append(new_camera)

    return jsonify(new_camera), 201


if __name__ == "__main__":
    app.run(port=5000, debug=True)
