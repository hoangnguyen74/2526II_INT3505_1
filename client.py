import requests

SERVER_URL = "http://127.0.0.1:5000"


# GET cameras
response = requests.get(f"{SERVER_URL}/cameras")

print("GET cameras:")
print(response.json())


# POST camera
data = {
    "name": "Camera Parking"
}

response = requests.post(f"{SERVER_URL}/cameras", json=data)

print("\nPOST camera:")
print(response.json())
