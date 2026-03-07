import requests

# Add more measurements
measurements = [
    {
        "measurement_type": "area",
        "name": "Blood spatter area",
        "description": "Area of blood distribution at scene",
        "coordinates": [{"x": 200, "y": 100, "z": 0}, {"x": 600, "y": 100, "z": 0}, 
                        {"x": 600, "y": 500, "z": 0}, {"x": 200, "y": 500, "z": 0}],
        "created_by": "Dr. Forensic Expert"
    },
    {
        "measurement_type": "angle",
        "name": "Impact angle",
        "description": "Estimated angle of attack",
        "coordinates": [{"x": 300, "y": 300, "z": 0}, {"x": 500, "y": 100, "z": 0}, 
                        {"x": 400, "y": 300, "z": 0}],
        "created_by": "Dr. Forensic Expert"
    }
]

for m in measurements:
    try:
        r = requests.post('http://localhost:8000/api/projects/4/measurements', json=m)
        if r.status_code == 201:
            data = r.json()
            print(f"Created: {data['measurement_type']} - {data['name']} = {data.get('value', 'N/A')}")
        else:
            print(f"Error: {r.status_code} - {r.text[:100]}")
    except Exception as e:
        print(f"Exception: {e}")

# List all measurements
print("\n--- All Measurements ---")
r = requests.get('http://localhost:8000/api/projects/4/measurements')
data = r.json()
print(f"Total: {len(data)}")
for m in data:
    print(f"  {m['id']}: {m['measurement_type']} - {m['name']} = {m.get('value', 'N/A')}")
