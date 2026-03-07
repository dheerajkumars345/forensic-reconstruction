import requests

# Check GPS data in images
print("=== Checking Image GPS Data ===")
r = requests.get('http://localhost:8000/api/projects/4/images')
images = r.json()
print(f"Total images: {len(images)}")
for img in images:
    gps_lat = img.get('gps_latitude')
    gps_lng = img.get('gps_longitude')
    print(f"  {img['filename']}: GPS=({gps_lat}, {gps_lng})")

# Check audit logs
print("\n=== Audit Trail ===")
r = requests.get('http://localhost:8000/api/projects/4/audit-log')
logs = r.json()
print(f"Total events: {len(logs)}")
for log in logs[:10]:  # Show last 10
    print(f"  {log.get('timestamp', 'N/A')[:19]} - {log.get('event_type', 'N/A')}: {log.get('event_description', 'N/A')[:50]}")

# Overall project status
print("\n=== Project Summary ===")
r = requests.get('http://localhost:8000/api/projects/4')
project = r.json()
print(f"Case: {project.get('case_number')} - {project.get('case_title')}")
print(f"Status: {project.get('status')}")
print(f"Images: {project.get('image_count', 0)}")
print(f"Examiner: {project.get('examiner_name')}")
