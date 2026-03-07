import requests
import time

# Start reconstruction
print("Starting 3D reconstruction...")
r = requests.post(
    'http://localhost:8000/api/projects/4/reconstruct',
    json={"reconstruction_type": "dense", "quality": "high"}
)
print(f"Status: {r.status_code}")
if r.status_code in [200, 201]:
    data = r.json()
    print(f"Task ID: {data.get('task_id', 'N/A')}")
    print(f"Status: {data.get('status', 'N/A')}")
    print(f"Message: {data.get('message', 'N/A')}")
else:
    print(f"Error: {r.text[:300]}")

# Check reconstruction status
print("\n--- Checking Status ---")
r = requests.get('http://localhost:8000/api/projects/4/reconstruction/status')
print(f"Status Code: {r.status_code}")
if r.status_code == 200:
    status = r.json()
    print(f"Reconstruction Status: {status.get('status')}")
    print(f"Progress: {status.get('progress', 'N/A')}%")
    if status.get('point_cloud_path'):
        print(f"Point Cloud: {status.get('point_cloud_path')}")
    if status.get('mesh_path'):
        print(f"Mesh: {status.get('mesh_path')}")
else:
    print(f"Error: {r.text}")
