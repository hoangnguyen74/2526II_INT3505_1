import requests

SERVER_URL = "http://127.0.0.1:5000"

headers = {
    "Authorization": "Bearer secret123"
}


# GET cameras
response = requests.get(
    f"{SERVER_URL}/cameras",
    headers=headers
)

print("GET cameras:")
print(response.json())


# POST camera
data = {
    "name": "Camera Parking"
}

response = requests.post(
    f"{SERVER_URL}/cameras",
    json=data,
    headers=headers
)

print("\nPOST camera:")
print(response.json())

# Request code from server
response = requests.get(f"{SERVER_URL}/script")

print("\nCode received from server:")
print(response.text)
