"""
Minimal backend for demonstration - runs without heavy dependencies
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import os
import cgi
from datetime import datetime
from urllib.parse import urlparse, parse_qs
from io import BytesIO

# In-memory storage
projects = []
images = []
project_id_counter = 1
image_id_counter = 1

# Create uploads directory
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

class CORSRequestHandler(BaseHTTPRequestHandler):
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
        
        if parsed_path.path == '/api/projects':
            self._set_headers()
            self.wfile.write(json.dumps(projects).encode())
        
        elif parsed_path.path.startswith('/api/projects/') and parsed_path.path.endswith('/images'):
            # Get images for a project
            project_id = int(parsed_path.path.split('/')[-2])
            project_images = [img for img in images if img['project_id'] == project_id]
            self._set_headers()
            self.wfile.write(json.dumps(project_images).encode())
        
        elif parsed_path.path.startswith('/api/projects/') and len(parsed_path.path.split('/')) == 4:
            project_id = int(parsed_path.path.split('/')[-1])
            project = next((p for p in projects if p['id'] == project_id), None)
            if project:
                self._set_headers()
                self.wfile.write(json.dumps(project).encode())
            else:
                self._set_headers(404)
                self.wfile.write(json.dumps({'detail': 'Project not found'}).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'detail': 'Not found'}).encode())
    
    def do_POST(self):
        global project_id_counter, image_id_counter
        
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
        
        elif self.path.startswith('/api/projects/') and self.path.endswith('/images'):
            # Handle file upload
            project_id = int(self.path.split('/')[-2])
            
            # Parse multipart form data
            content_type = self.headers['Content-Type']
            if not content_type.startswith('multipart/form-data'):
                self._set_headers(400)
                self.wfile.write(json.dumps({'detail': 'Must be multipart/form-data'}).encode())
                return
            
            # Create form parser
            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    'REQUEST_METHOD': 'POST',
                    'CONTENT_TYPE': content_type,
                }
            )
            
            uploaded_images = []
            
            # Process uploaded files
            if 'files' in form:
                files = form['files']
                if not isinstance(files, list):
                    files = [files]
                
                for file_item in files:
                    if file_item.filename:
                        # Save file
                        filename = os.path.basename(file_item.filename)
                        project_dir = os.path.join(UPLOAD_DIR, str(project_id))
                        os.makedirs(project_dir, exist_ok=True)
                        filepath = os.path.join(project_dir, filename)
                        
                        with open(filepath, 'wb') as f:
                            f.write(file_item.file.read())
                        
                        # Create image record
                        new_image = {
                            'id': image_id_counter,
                            'project_id': project_id,
                            'filename': filename,
                            'filepath': filepath,
                            'file_hash': 'demo-hash-' + str(image_id_counter),
                            'width': 1920,
                            'height': 1080,
                            'uploaded_at': datetime.now().isoformat(),
                            'is_processed': False,
                            'quality_score': 0.85
                        }
                        images.append(new_image)
                        uploaded_images.append(new_image)
                        image_id_counter += 1
                        
                        # Update project image count
                        project = next((p for p in projects if p['id'] == project_id), None)
                        if project:
                            project['image_count'] = len([img for img in images if img['project_id'] == project_id])
            
            self._set_headers(201)
            self.wfile.write(json.dumps(uploaded_images).encode())
        
        else:
            self._set_headers(404)
            self.wfile.write(json.dumps({'detail': 'Not found'}).encode())

def run(port=8000):
    server_address = ('', port)
    httpd = HTTPServer(server_address, CORSRequestHandler)
    print(f'Starting minimal backend server on port {port}...')
    print(f'API available at: http://localhost:{port}/api')
    print(f'Press Ctrl+C to stop')
    httpd.serve_forever()

if __name__ == '__main__':
    # Add some test data
    projects.append({
        'id': 1,
        'case_number': 'DEMO-2024-001',
        'case_title': 'Sample Crime Scene Reconstruction',
        'description': 'Demonstration case showing the system capabilities',
        'location': 'Test Location, India',
        'incident_date': '2024-01-15T10:30:00',
        'examiner_name': 'Dr. Forensic Expert',
        'examiner_id': 'FSL-12345',
        'laboratory': 'Central Forensic Science Laboratory',
        'status': 'processing',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'image_count': 12
    })
    project_id_counter = 2
    
    run(8000)
