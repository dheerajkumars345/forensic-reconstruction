import requests
import json
import os

BASE_URL = "http://localhost:8000/api"

def test_backend():
    print("Testing Backend Endpoints...")
    
    # 1. Create Project
    print("\n1. Creating Project...")
    project_data = {
        "case_number": "BSA-TEST-001",
        "case_title": "BSA Compliance Test",
        "examiner_name": "Test Agent"
    }
    r = requests.post(f"{BASE_URL}/projects", json=project_data)
    if r.status_code == 201:
        project = r.json()
        print(f"   Success: Project created with ID {project['id']}")
        project_id = project['id']
    else:
        print(f"   Failed: {r.status_code} - {r.text}")
        return

    # 2. Upload Images (Simulated)
    print("\n2. Uploading Images...")
    # Create dummy image
    with open("test_img.jpg", "wb") as f:
        f.write(b"fake image data")
    
    files = {'files': open("test_img.jpg", 'rb')}
    r = requests.post(f"{BASE_URL}/projects/{project_id}/images", files=files)
    if r.status_code == 201:
        images = r.json()
        print(f"   Success: {len(images)} images uploaded.")
        # Check metadata
        img = images[0]
        if 'gps_latitude' in img:
             print("   Success: GPS metadata present.")
    else:
        print(f"   Failed: {r.status_code} - {r.text}")

    # 3. Generate Report (Check BSA Compliance)
    print("\n3. Generating Report...")
    r = requests.post(f"{BASE_URL}/projects/{project_id}/report/generate", json={})
    if r.status_code == 200:
        data = r.json()
        report_path = data['report_path']
        print(f"   Success: Report generated at {report_path}")
        
        # Verify Report Content
        full_path = f"../backend/{report_path}" # Adjust path relative to script
        # Actually simplest to read the file directly since we are on the same machine
        # The server saves to 'reports/...' relative to CWD.
        # We are running this script in backend/ typically? Or user root?
        # Let's try to read the file from the server's expected location.
        actual_path = os.path.join(os.getcwd(), report_path) 
        
        if os.path.exists(actual_path):
             with open(actual_path, "rb") as f:
                 content = f.read()
                 if b"Section 63 BSA Compliant" in content:
                     print("   VERIFIED: Report contains 'Section 63 BSA Compliant' text.")
                 else:
                     print("   FAILED: Report missing compliance text.")
        else:
            print(f"   Warning: Could not find report file locally at {actual_path}")
            
    else:
        print(f"   Failed: {r.status_code} - {r.text}")

    # 4. Check Audit Log
    print("\n4. Checking Audit Log...")
    r = requests.get(f"{BASE_URL}/projects/{project_id}/audit-log")
    if r.status_code == 200:
        logs = r.json()
        print(f"   Success: {len(logs)} audit logs retrieved.")
        if len(logs) > 0:
            print(f"   Sample Log: {logs[0]['event_type']} - {logs[0]['event_description']}")
    else:
        print(f"   Failed: {r.status_code} - {r.text}")

if __name__ == "__main__":
    test_backend()
