import requests
import os

project_id = 4
test_dir = 'e:/forensic-antigravity/test_images'

for i in range(1, 4):
    file_path = f'{test_dir}/crime_scene_{i}.jpg'
    with open(file_path, 'rb') as f:
        files = {'files': (f'crime_scene_{i}.jpg', f, 'image/jpeg')}
        response = requests.post(
            f'http://localhost:8000/api/projects/{project_id}/images',
            files=files
        )
        print(f'Image {i}: Status {response.status_code}')
        if response.status_code == 200:
            result = response.json()
            img_id = result.get('id')
            file_hash = result.get('file_hash', 'N/A')
            print(f'  ID: {img_id}, Hash: {file_hash[:16]}...')
        else:
            print(f'  Error: {response.text[:200]}')
