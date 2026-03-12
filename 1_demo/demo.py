from flask import Flask, request, jsonify

app = Flask(__name__)

# fake database
cameras = [
    {"id": 1, "name": "Camera Gate A", "location": "Gate"},
    {"id": 2, "name": "Camera Lobby", "location": "Lobby"}
]

alerts = []


# ======================
# GET cameras
# ======================
@app.route("/cameras", methods=["GET"])
def get_cameras():
    return jsonify({
        "status": "success",
        "data": cameras
    })


# ======================
# GET camera by id
# ======================
@app.route("/cameras/<int:camera_id>", methods=["GET"])
def get_camera(camera_id):

    for cam in cameras:
        if cam["id"] == camera_id:
            return jsonify(cam)

    return jsonify({"error": "Camera not found"}), 404


# ======================
# POST create camera
# ======================
@app.route("/cameras", methods=["POST"])
def create_camera():

    data = request.json

    new_camera = {
        "id": len(cameras) + 1,
        "name": data["name"],
        "location": data["location"]
    }

    cameras.append(new_camera)

    return jsonify(new_camera), 201


# ======================
# DELETE camera
# ======================
@app.route("/cameras/<int:camera_id>", methods=["DELETE"])
def delete_camera(camera_id):

    global cameras
    cameras = [c for c in cameras if c["id"] != camera_id]

    return jsonify({"message": "Camera deleted"})


# ======================
# POST alert
# ======================
@app.route("/alerts", methods=["POST"])
def create_alert():

    data = request.json

    alert = {
        "camera_id": data["camera_id"],
        "alert_type": data["alert_type"],
        "timestamp": data["timestamp"]
    }

    alerts.append(alert)

    return jsonify(alert), 201


# ======================
# GET alerts
# ======================
@app.route("/alerts", methods=["GET"])
def get_alerts():

    alert_type = request.args.get("type")

    if alert_type:
        filtered = [a for a in alerts if a["alert_type"] == alert_type]
        return jsonify(filtered)

    return jsonify(alerts)


if __name__ == "__main__":
    app.run(debug=True)
