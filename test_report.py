import requests
import time

# Generate report
print("Generating forensic report...")
r = requests.post(
    'http://localhost:8000/api/projects/4/report/generate',
    json={
        "report_type": "full",
        "included_sections": [
            "executive_summary",
            "reconstruction",
            "measurements",
            "evidence",
            "audit_trail"
        ],
        "examiner_signature": "Dr. Forensic Expert"
    }
)
print(f"Status: {r.status_code}")
if r.status_code in [200, 201]:
    data = r.json()
    print(f"Report ID: {data.get('id', 'N/A')}")
    print(f"Report Path: {data.get('report_path', 'N/A')}")
    print(f"Generated At: {data.get('generated_at', 'N/A')}")
else:
    print(f"Error: {r.text[:500]}")

# Get report info
print("\n--- Report Details ---")
r = requests.get('http://localhost:8000/api/projects/4/report')
print(f"Status: {r.status_code}")
if r.status_code == 200:
    report = r.json()
    print(f"Report ID: {report.get('id')}")
    print(f"Report Type: {report.get('report_type')}")
    print(f"Path: {report.get('report_path')}")
else:
    print(f"Error: {r.text}")
