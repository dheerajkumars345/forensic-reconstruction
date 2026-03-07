"""
Full-featured demo backend with simulated 3D reconstruction, measurements, and reports
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import cgi
import random
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from io import BytesIO

# In-memory storage
projects = []
images = []
reconstructions = []
measurements = []
audit_logs_db = []
project_id_counter = 1
image_id_counter = 1
reconstruction_id_counter = 1
measurement_id_counter = 1
audit_log_id_counter = 1

# Create directories
UPLOAD_DIR = "uploads"
MODELS_DIR = "models"
REPORTS_DIR = "reports"
for dir_path in [UPLOAD_DIR, MODELS_DIR, REPORTS_DIR]:
    os.makedirs(dir_path, exist_ok=True)

class FullFeatureHandler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_OPTIONS(self):
        self._set_headers()
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Projects list
        if parsed_path.path == '/api/projects':
            self._set_headers()
            self.wfile.write(json.dumps(projects).encode())
        
        # Single project
        elif parsed_path.path.startswith('/api/projects/') and len(parsed_path.path.split('/')) == 4:
            project_id = int(parsed_path.path.split('/')[-1])
            project = next((p for p in projects if p['id'] == project_id), None)
            if project:
                self._set_headers()
                self.wfile.write(json.dumps(project).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'detail': 'Project not found'}).encode())
        
        # Images for project
        elif parsed_path.path.startswith('/api/projects/') and parsed_path.path.endswith('/images'):
            project_id = int(parsed_path.path.split('/')[-2])
            project_images = [img for img in images if img['project_id'] == project_id]
            self._set_headers()
            self.wfile.write(json.dumps(project_images).encode())
            
        # Audit logs for project
        elif parsed_path.path.startswith('/api/projects/') and parsed_path.path.endswith('/audit-log'):
            self._set_headers()
            self.wfile.write(json.dumps(audit_logs_db).encode())
        
        # Reconstruction status
        elif parsed_path.path.startswith('/api/projects/') and 'reconstruction/status' in parsed_path.path:
            project_id = int(parsed_path.path.split('/')[-3])
            recon = next((r for r in reconstructions if r['project_id'] == project_id), None)
            if recon:
                self._set_headers()
                self.wfile.write(json.dumps(recon).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'detail': 'No reconstruction found'}).encode())
        
        # Measurements
        elif parsed_path.path.startswith('/api/projects/') and parsed_path.path.endswith('/measurements'):
            project_id = int(parsed_path.path.split('/')[-2])
            project_measurements = [m for m in measurements if m['project_id'] == project_id]
            self._set_headers()
            self.wfile.write(json.dumps(project_measurements).encode())
        
        # Audit log
        elif parsed_path.path.startswith('/api/projects/') and 'audit-log' in parsed_path.path:
            project_id = int(parsed_path.path.split('/')[-2])
            project_logs = [log for log in audit_logs if log['project_id'] == project_id]
            self._set_headers()
            self.wfile.write(json.dumps(project_logs).encode())
        
        # Static file serving
        elif parsed_path.path.startswith('/uploads/') or parsed_path.path.startswith('/models/') or parsed_path.path.startswith('/reports/'):
            file_path = parsed_path.path.lstrip('/')
            if os.path.exists(file_path) and os.path.isfile(file_path):
                self.send_response(200)
                if file_path.lower().endswith(('.jpg', '.jpeg')):
                    self.send_header('Content-Type', 'image/jpeg')
                elif file_path.lower().endswith('.png'):
                    self.send_header('Content-Type', 'image/png')
                elif file_path.lower().endswith('.pdf'):
                    self.send_header('Content-Type', 'application/pdf')
                else:
                    self.send_header('Content-Type', 'application/octet-stream')
                self.send_header('Access-Control-Allow-Origin', '*')
                self.end_headers()
                with open(file_path, 'rb') as f:
                    self.wfile.write(f.read())
                return
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'detail': 'File not found'}).encode())
                return
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'detail': 'Not found'}).encode())
    
    def do_POST(self):
        global project_id_counter, image_id_counter, reconstruction_id_counter, measurement_id_counter
        
        # Create project
        if self.path == '/api/projects':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            new_project = {
                'id': project_id_counter,
                'case_number': data.get('case_number'),
                'case_title': data.get('case_title'),
                'description': data.get('description', ''),
                'location': data.get('location', ''),
                'incident_date': data.get('incident_date'),
                'examiner_name': data.get('examiner_name'),
                'examiner_id': data.get('examiner_id', ''),
                'laboratory': data.get('laboratory', ''),
                'status': 'created',
                'created_at': datetime.now().isoformat(),
                'updated_at': datetime.now().isoformat(),
                'image_count': 0
            }
            projects.append(new_project)
            project_id_counter += 1
            
            self._set_headers(201)
            self.wfile.write(json.dumps(new_project).encode())
        
        # Upload images
        elif self.path.startswith('/api/projects/') and self.path.endswith('/images'):
            project_id = int(self.path.split('/')[-2])
            
            content_type = self.headers['Content-Type']
            if not content_type.startswith('multipart/form-data'):
                self._set_headers(400)
                self.wfile.write(json.dumps({'detail': 'Must be multipart/form-data'}).encode())
                return
            
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )
            
            uploaded_images = []
            
            if 'files' in form:
                files = form['files']
                if not isinstance(files, list):
                    files = [files]
                
                for file_item in files:
                    if file_item.filename:
                        filename = os.path.basename(file_item.filename)
                        project_dir = os.path.join(UPLOAD_DIR, str(project_id))
                        os.makedirs(project_dir, exist_ok=True)
                        filepath = os.path.join(project_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(file_item.file.read())
                        
                        # Simulate GPS coordinates
                        gps_lat = 28.6139 + random.uniform(-0.01, 0.01)  # Delhi area
                        gps_lon = 77.2090 + random.uniform(-0.01, 0.01)
                        
                        new_image = {
                            'id': image_id_counter,
                            'project_id': project_id,
                            'filename': filename,
                            'filepath': filepath,
                            'file_hash': f'sha256-{image_id_counter:08x}',
                            'width': 1920,
                            'height': 1080,
                            'gps_latitude': gps_lat,
                            'gps_longitude': gps_lon,
                            'gps_altitude': 220.5,
                            'camera_make': 'Canon',
                            'camera_model': 'EOS 5D Mark IV',
                            'date_taken': datetime.now().isoformat(),
                            'uploaded_at': datetime.now().isoformat(),
                            'is_processed': False,
                            'quality_score': random.uniform(0.75, 0.95)
                        }
                        images.append(new_image)
                        uploaded_images.append(new_image)
                        image_id_counter += 1
                        
                        # Update project
                        project = next((p for p in projects if p['id'] == project_id), None)
                        if project:
                            project['image_count'] = len([img for img in images if img['project_id'] == project_id])
                            project['status'] = 'images_uploaded'
            
            self._set_headers(201)
            self.wfile.write(json.dumps(uploaded_images).encode())
        
        # Start reconstruction
        elif self.path.startswith('/api/projects/') and self.path.endswith('/reconstruct'):
            project_id = int(self.path.split('/')[-2])
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            project_images = [img for img in images if img['project_id'] == project_id]
            
            # Create reconstruction with granular steps
            new_reconstruction = {
                'id': reconstruction_id_counter,
                'project_id': project_id,
                'status': 'completed',
                'num_images_used': len(project_images),
                'num_points': random.randint(50000, 150000),
                'num_faces': random.randint(100000, 300000),
                'scale_factor': 1.0,
                'estimated_accuracy_cm': round(random.uniform(2.5, 5.5), 2),
                'quality': data.get('quality', 'medium'),
                'started_at': datetime.now().isoformat(),
                'completed_at': datetime.now().isoformat(),
                'orthomosaic_path': f"models/orthomosaic_{project_id}.tif",
                'pipeline': [
                    {"step": "Feature Extraction", "status": "completed", "details": f"Extracted {len(project_images)*1200} SIFT features"},
                    {"step": "Structure from Motion", "status": "completed", "details": f"Aligned {len(project_images)}/4 cameras"},
                    {"step": "Multi-View Stereo", "status": "completed", "details": "Generated dense reconstructed mesh"},
                    {"step": "Orthomosaic Generation", "status": "completed", "details": "Generated 0.5cm/px orthophoto"}
                ]
            }
            
            # Create a fake orthomosaic file
            os.makedirs(MODELS_DIR, exist_ok=True)
            with open(os.path.join(MODELS_DIR, f"orthomosaic_{project_id}.tif"), 'wb') as f:
                f.write(b"fake tiff data")

            reconstructions.append(new_reconstruction)
            reconstruction_id_counter += 1
            
            # Update project status
            project = next((p for p in projects if p['id'] == project_id), None)
            if project:
                project['status'] = 'reconstructed'
            
            self._set_headers(201)
            self.wfile.write(json.dumps(new_reconstruction).encode())
        
        # Create measurement
        elif self.path.startswith('/api/projects/') and self.path.endswith('/measurements'):
            project_id = int(self.path.split('/')[-2])
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            # Calculate measurement value based on type
            measurement_type = data.get('measurement_type', 'distance')
            if measurement_type == 'distance':
                value = round(random.uniform(0.5, 5.0), 3)
                unit = 'meters'
            elif measurement_type == 'area':
                value = round(random.uniform(1.0, 10.0), 3)
                unit = 'square meters'
            elif measurement_type == 'volume':
                value = round(random.uniform(0.5, 8.0), 3)
                unit = 'cubic meters'
            else:
                value = round(random.uniform(30, 150), 2)
                unit = 'degrees'
            
            new_measurement = {
                'id': measurement_id_counter,
                'project_id': project_id,
                'measurement_type': measurement_type,
                'name': data.get('name', f'Measurement {measurement_id_counter}'),
                'description': data.get('description', ''),
                'coordinates': data.get('coordinates', []),
                'value': value,
                'unit': unit,
                'uncertainty': round(value * 0.05, 3),
                'created_by': data.get('created_by', 'System'),
                'created_at': datetime.now().isoformat()
            }
            measurements.append(new_measurement)
            measurement_id_counter += 1
            
            self._set_headers(201)
            self.wfile.write(json.dumps(new_measurement).encode())
        
        # Generate report
        elif self.path.startswith('/api/projects/') and 'report/generate' in self.path:
            project_id = int(self.path.split('/')[-3])
            
            project = next((p for p in projects if p['id'] == project_id), None)
            if not project:
                self._set_headers(404)
                self.wfile.write(json.dumps({'detail': 'Project not found'}).encode())
                return
            
            report_filename = f"report_{project['case_number']}.pdf"
            report_path = f"{REPORTS_DIR}/{report_filename}"
            report_full_path = os.path.join(REPORTS_DIR, report_filename)
            report_hash = f"sha256-report-{project_id:08x}"
            
            # Simulate PDF creation
            with open(report_full_path, 'wb') as f:
                f.write(b'%PDF-1.4\nSimulated Forensic Report (Section 63 BSA Compliant)\n')
            
            response = {
                'message': 'Report generated successfully',
                'report_path': report_path,
                'report_hash': report_hash
            }
            
            self._set_headers(200)
            self.wfile.write(json.dumps(response).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'detail': 'Not found'}).encode())

def run(port=8000):
    # Add demo data
    global project_id_counter
    projects.append({
        'id': 1,
        'case_number': 'DEMO-2024-001',
        'case_title': 'Sample Crime Scene Reconstruction',
        'description': 'Demonstration case showing the system capabilities with full workflow',
        'location': 'New Delhi, India',
        'incident_date': '2024-01-15T10:30:00',
        'examiner_name': 'Dr. Forensic Expert',
        'examiner_id': 'FSL-12345',
        'laboratory': 'Central Forensic Science Laboratory',
        'status': 'reconstructed',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'image_count': 4
    })
    # Add mock images for demo project
    global image_id_counter
    for i in range(1, 5):
        filename = f"scene_evidence_{i}.jpg"
        project_dir = os.path.join(UPLOAD_DIR, "1")
        os.makedirs(project_dir, exist_ok=True)
        filepath = os.path.join(project_dir, filename)
        
        # Create empty placeholder files if they don't exist
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                f.write(b'fake image data')

        images.append({
            'id': image_id_counter,
            'project_id': 1,
            'filename': filename,
            'filepath': filepath,
            'file_hash': f'sha256-{image_id_counter:08x}',
            'width': 2048,
            'height': 1536,
            'gps_latitude': 28.6139 + random.uniform(-0.01, 0.01),
            'gps_longitude': 77.2090 + random.uniform(-0.01, 0.01),
            'gps_altitude': 214.5 + i,
            'camera_make': 'Nikon',
            'camera_model': 'D850',
            'iso': random.choice([100, 200, 400]),
            'exposure_time': '1/250',
            'f_number': 4.0,
            'focal_length': 35.0,
            'date_taken': datetime.now().isoformat(),
            'uploaded_at': datetime.now().isoformat(),
            'is_processed': True,
            'quality_score': random.uniform(0.92, 0.98)
        })
        image_id_counter += 1

    # Add forensic audit trail
    global audit_log_id_counter
    audit_logs_db.extend([
        {'timestamp': datetime.now().isoformat(), 'event_type': 'image_upload', 'user_name': 'Dr. Forensic', 'event_description': 'Uploaded 4 raw evidence images (SHA-256 verified)'},
        {'timestamp': datetime.now().isoformat(), 'event_type': 'modification', 'user_name': 'Dr. Forensic', 'event_description': 'Adjusted exposure (+0.5 EV) for scene_evidence_1.jpg'},
        {'timestamp': datetime.now().isoformat(), 'event_type': 'modification', 'user_name': 'Dr. Forensic', 'event_description': 'Applied forensic cropping to scene_evidence_4.jpg to isolate projectile path'},
        {'timestamp': datetime.now().isoformat(), 'event_type': 'measurement', 'user_name': 'Dr. Forensic', 'event_description': 'Validated photogrammetric scale using 1.0m reference bar'},
    ])

    # Add mock reconstruction for project 1
    global reconstruction_id_counter
    reconstructions.append({
        'id': reconstruction_id_counter,
        'project_id': 1,
        'status': 'completed',
        'num_images_used': 4,
        'num_points': 82145,
        'num_faces': 214560,
        'scale_factor': 1.0,
        'estimated_accuracy_cm': 3.12,
        'quality': 'medium',
        'started_at': datetime.now().isoformat(),
        'completed_at': datetime.now().isoformat(),
        'orthomosaic_path': "models/orthomosaic_1.tif",
        'pipeline': [
            {"step": "Feature Extraction", "status": "completed", "details": "Detected 4,800 SIFT keypoints across 4 images"},
            {"step": "Structure from Motion", "status": "completed", "details": "Sparse cloud generated with 15k points"},
            {"step": "Multi-View Stereo", "status": "completed", "details": "Dense depth map fusion successful"},
            {"step": "Orthomosaic Generation", "status": "completed", "details": "Top-down orthophoto generated at 0.5cm/px"}
        ]
    })
    reconstruction_id_counter += 1

    # Add mock measurements for project 1
    global measurement_id_counter
    measurements.extend([
        {
            'id': measurement_id_counter,
            'project_id': 1,
            'measurement_type': 'distance',
            'name': 'Distance: Body to Weapon',
            'description': 'Direct linear distance from the center of mass to the recovered handgun.',
            'value': 2.45,
            'unit': 'meters',
            'uncertainty': 0.02,
            'created_by': 'Dr. Forensic Expert',
            'created_at': datetime.now().isoformat()
        },
        {
            'id': measurement_id_counter + 1,
            'project_id': 1,
            'measurement_type': 'area',
            'name': 'Primary Impact Zone',
            'description': 'Calculated area of the blood distribution on the north-east floor section.',
            'value': 1.12,
            'unit': 'sq meters',
            'uncertainty': 0.05,
            'created_by': 'Dr. Forensic Expert',
            'created_at': datetime.now().isoformat()
        }
    ])
    measurement_id_counter += 2

    project_id_counter = 2
    
    server_address = ('', port)
    httpd = HTTPServer(server_address, FullFeatureHandler)
    print(f'🚀 Full-Featured Demo Server Running!')
    print(f'📍 API: http://localhost:{port}/api')
    print(f'✨ Features: Projects, Images, 3D Reconstruction, Measurements, Reports')
    print(f'🔧 Press Ctrl+C to stop\n')
    httpd.serve_forever()

if __name__ == '__main__':
    run(8000)
