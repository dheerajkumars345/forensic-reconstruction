"""
Generate overlapping images of a 3D scene for real photogrammetry testing.
Creates multiple views of the same scene from different camera angles.
"""
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import os
import math
from datetime import datetime, timedelta
import piexif
import struct


def create_gps_ifd(lat: float, lon: float, altitude: float = 0):
    """Create GPS IFD for EXIF data"""
    def to_deg(value, loc):
        if value < 0:
            loc_value = loc[1]
            value = abs(value)
        else:
            loc_value = loc[0]
        deg = int(value)
        min_float = (value - deg) * 60
        min_int = int(min_float)
        sec = (min_float - min_int) * 60 * 100
        return ((deg, 1), (min_int, 1), (int(sec), 100)), loc_value

    lat_deg, lat_ref = to_deg(lat, ["N", "S"])
    lon_deg, lon_ref = to_deg(lon, ["E", "W"])

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref.encode(),
        piexif.GPSIFD.GPSLatitude: lat_deg,
        piexif.GPSIFD.GPSLongitudeRef: lon_ref.encode(),
        piexif.GPSIFD.GPSLongitude: lon_deg,
        piexif.GPSIFD.GPSAltitudeRef: 0,
        piexif.GPSIFD.GPSAltitude: (int(altitude * 100), 100),
    }
    return gps_ifd


def render_3d_scene(camera_angle: float, camera_elevation: float, width: int = 1920, height: int = 1080) -> Image.Image:
    """
    Render a 3D crime scene from a given camera angle.
    Uses simple 3D projection to create realistic overlapping views.
    """
    img = Image.new('RGB', (width, height), color=(40, 45, 50))
    draw = ImageDraw.Draw(img)
    
    # Camera setup
    cam_distance = 10
    cam_x = cam_distance * math.cos(math.radians(camera_angle)) * math.cos(math.radians(camera_elevation))
    cam_y = cam_distance * math.sin(math.radians(camera_angle)) * math.cos(math.radians(camera_elevation))
    cam_z = cam_distance * math.sin(math.radians(camera_elevation)) + 2
    
    focal_length = 800
    
    def project_3d_to_2d(x3d, y3d, z3d):
        """Project 3D point to 2D screen coordinates"""
        # Translate to camera space
        dx = x3d - cam_x
        dy = y3d - cam_y
        dz = z3d - cam_z
        
        # Rotate based on camera angle
        angle_rad = math.radians(-camera_angle)
        rx = dx * math.cos(angle_rad) - dy * math.sin(angle_rad)
        ry = dx * math.sin(angle_rad) + dy * math.cos(angle_rad)
        rz = dz
        
        # Rotate based on elevation
        elev_rad = math.radians(-camera_elevation)
        ry2 = ry * math.cos(elev_rad) - rz * math.sin(elev_rad)
        rz2 = ry * math.sin(elev_rad) + rz * math.cos(elev_rad)
        
        # Project
        if ry2 > 0.1:
            screen_x = int(width/2 + focal_length * rx / ry2)
            screen_y = int(height/2 - focal_length * rz2 / ry2)
            depth = ry2
            return screen_x, screen_y, depth
        return None
    
    def draw_3d_polygon(points_3d, color, outline=None):
        """Draw a filled polygon in 3D space"""
        projected = [project_3d_to_2d(*p) for p in points_3d]
        if all(p is not None for p in projected):
            avg_depth = sum(p[2] for p in projected) / len(projected)
            points_2d = [(p[0], p[1]) for p in projected]
            return (avg_depth, points_2d, color, outline)
        return None
    
    polygons = []
    
    # Floor (concrete texture simulation)
    floor_size = 8
    tile_size = 1
    for i in range(-4, 4):
        for j in range(-4, 4):
            is_dark = (i + j) % 2 == 0
            color = (60, 65, 70) if is_dark else (70, 75, 80)
            floor_tile = [
                (i * tile_size, j * tile_size, 0),
                ((i+1) * tile_size, j * tile_size, 0),
                ((i+1) * tile_size, (j+1) * tile_size, 0),
                (i * tile_size, (j+1) * tile_size, 0),
            ]
            poly = draw_3d_polygon(floor_tile, color)
            if poly:
                polygons.append(poly)
    
    # Evidence markers (yellow cones)
    evidence_positions = [
        (1.5, 0.5, "1"),
        (-1.0, 1.5, "2"),
        (0.5, -1.0, "3"),
        (-0.5, 2.0, "4"),
        (2.0, -0.5, "5"),
    ]
    
    for ex, ey, label in evidence_positions:
        # Cone base
        cone_radius = 0.15
        cone_height = 0.4
        segments = 8
        for s in range(segments):
            angle1 = s * 360 / segments
            angle2 = (s + 1) * 360 / segments
            x1 = ex + cone_radius * math.cos(math.radians(angle1))
            y1 = ey + cone_radius * math.sin(math.radians(angle1))
            x2 = ex + cone_radius * math.cos(math.radians(angle2))
            y2 = ey + cone_radius * math.sin(math.radians(angle2))
            
            # Cone side
            cone_face = [
                (x1, y1, 0),
                (x2, y2, 0),
                (ex, ey, cone_height),
            ]
            shade = 200 + int(50 * math.sin(math.radians(angle1)))
            poly = draw_3d_polygon(cone_face, (shade, shade, 0), (100, 100, 0))
            if poly:
                polygons.append(poly)
    
    # Blood spatter patterns (dark red spots)
    blood_positions = [
        (0.3, 0.8, 0.2),
        (0.5, 0.9, 0.15),
        (0.1, 1.0, 0.25),
        (0.4, 1.2, 0.1),
        (-0.2, 0.7, 0.18),
    ]
    
    for bx, by, br in blood_positions:
        segments = 12
        blood_points = []
        for s in range(segments):
            angle = s * 360 / segments
            px = bx + br * math.cos(math.radians(angle))
            py = by + br * math.sin(math.radians(angle))
            blood_points.append((px, py, 0.001))
        
        poly = draw_3d_polygon(blood_points, (80, 20, 20))
        if poly:
            polygons.append(poly)
    
    # Scale ruler (L-shaped)
    ruler_color = (200, 200, 50)
    ruler_marks = (50, 50, 50)
    
    # Horizontal part
    ruler_h = [
        (-0.5, -0.5, 0.01),
        (1.0, -0.5, 0.01),
        (1.0, -0.4, 0.01),
        (-0.5, -0.4, 0.01),
    ]
    poly = draw_3d_polygon(ruler_h, ruler_color)
    if poly:
        polygons.append(poly)
    
    # Vertical part
    ruler_v = [
        (-0.5, -0.5, 0.01),
        (-0.4, -0.5, 0.01),
        (-0.4, 1.0, 0.01),
        (-0.5, 1.0, 0.01),
    ]
    poly = draw_3d_polygon(ruler_v, ruler_color)
    if poly:
        polygons.append(poly)
    
    # Weapon (knife shape)
    knife_blade = [
        (1.8, 1.5, 0.02),
        (2.5, 1.6, 0.02),
        (2.6, 1.65, 0.02),
        (2.5, 1.7, 0.02),
        (1.8, 1.6, 0.02),
    ]
    poly = draw_3d_polygon(knife_blade, (150, 150, 160))
    if poly:
        polygons.append(poly)
    
    knife_handle = [
        (1.3, 1.45, 0.02),
        (1.8, 1.5, 0.02),
        (1.8, 1.6, 0.02),
        (1.3, 1.65, 0.02),
    ]
    poly = draw_3d_polygon(knife_handle, (60, 40, 30))
    if poly:
        polygons.append(poly)
    
    # Box (evidence container)
    box_size = 0.4
    bx, by = -2, -1
    
    # Box faces
    box_faces = [
        # Top
        [(bx, by, box_size), (bx+box_size, by, box_size), 
         (bx+box_size, by+box_size, box_size), (bx, by+box_size, box_size)],
        # Front
        [(bx, by, 0), (bx+box_size, by, 0), 
         (bx+box_size, by, box_size), (bx, by, box_size)],
        # Right
        [(bx+box_size, by, 0), (bx+box_size, by+box_size, 0), 
         (bx+box_size, by+box_size, box_size), (bx+box_size, by, box_size)],
        # Back
        [(bx, by+box_size, 0), (bx+box_size, by+box_size, 0), 
         (bx+box_size, by+box_size, box_size), (bx, by+box_size, box_size)],
        # Left
        [(bx, by, 0), (bx, by+box_size, 0), 
         (bx, by+box_size, box_size), (bx, by, box_size)],
    ]
    
    box_colors = [(139, 90, 43), (120, 80, 40), (130, 85, 42), (115, 75, 38), (125, 82, 41)]
    for face, color in zip(box_faces, box_colors):
        poly = draw_3d_polygon(face, color, (80, 50, 25))
        if poly:
            polygons.append(poly)
    
    # Sort by depth (painter's algorithm)
    polygons.sort(key=lambda x: -x[0])
    
    # Draw all polygons
    for _, points_2d, color, outline in polygons:
        if len(points_2d) >= 3:
            draw.polygon(points_2d, fill=color, outline=outline)
    
    # Add some noise/texture
    pixels = np.array(img)
    noise = np.random.normal(0, 3, pixels.shape).astype(np.int16)
    pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(pixels)
    
    return img


def create_photogrammetry_dataset(output_dir: str, num_views: int = 8):
    """
    Create a dataset of overlapping images suitable for photogrammetry.
    
    Args:
        output_dir: Directory to save images
        num_views: Number of camera positions around the scene
    """
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Creating photogrammetry dataset with {num_views} views...")
    
    # Camera positions in a circle around the scene
    base_time = datetime(2026, 3, 7, 14, 30, 0)
    
    # Hyderabad coordinates (forensic lab)
    base_lat = 17.4474
    base_lon = 78.3762
    
    images_info = []
    
    for i in range(num_views):
        # Calculate camera angle (full 360 degree coverage)
        angle = i * (360 / num_views)
        
        # Vary elevation slightly for better coverage
        elevation = 15 + 10 * math.sin(math.radians(angle * 2))
        
        print(f"  Rendering view {i+1}/{num_views}: angle={angle:.1f}°, elevation={elevation:.1f}°")
        
        # Render the scene
        img = render_3d_scene(angle, elevation)
        
        # Add EXIF metadata
        capture_time = base_time + timedelta(seconds=i * 15)
        
        # Slight GPS variation to simulate walking around
        lat = base_lat + 0.00001 * math.cos(math.radians(angle))
        lon = base_lon + 0.00001 * math.sin(math.radians(angle))
        
        exif_dict = {
            "0th": {
                piexif.ImageIFD.Make: "Canon".encode(),
                piexif.ImageIFD.Model: "EOS 5D Mark IV".encode(),
                piexif.ImageIFD.Software: "Forensic Capture v2.0".encode(),
                piexif.ImageIFD.ImageDescription: f"Crime Scene View {i+1} - Angle {angle:.0f}deg".encode(),
            },
            "Exif": {
                piexif.ExifIFD.DateTimeOriginal: capture_time.strftime("%Y:%m:%d %H:%M:%S").encode(),
                piexif.ExifIFD.DateTimeDigitized: capture_time.strftime("%Y:%m:%d %H:%M:%S").encode(),
                piexif.ExifIFD.FocalLength: (50, 1),
                piexif.ExifIFD.FocalLengthIn35mmFilm: 50,
                piexif.ExifIFD.ISOSpeedRatings: 400,
                piexif.ExifIFD.ExposureTime: (1, 125),
                piexif.ExifIFD.FNumber: (56, 10),
                piexif.ExifIFD.ExposureProgram: 2,
                piexif.ExifIFD.MeteringMode: 5,
                piexif.ExifIFD.Flash: 0,
                piexif.ExifIFD.WhiteBalance: 0,
                piexif.ExifIFD.PixelXDimension: img.width,
                piexif.ExifIFD.PixelYDimension: img.height,
            },
            "GPS": create_gps_ifd(lat, lon, 540 + i * 0.5),
            "1st": {},
            "thumbnail": None,
        }
        
        exif_bytes = piexif.dump(exif_dict)
        
        # Save image
        filename = f"scene_view_{i+1:02d}.jpg"
        filepath = os.path.join(output_dir, filename)
        img.save(filepath, "JPEG", quality=95, exif=exif_bytes)
        
        images_info.append({
            "filename": filename,
            "angle": angle,
            "elevation": elevation,
            "lat": lat,
            "lon": lon,
            "timestamp": capture_time.isoformat(),
        })
        
        print(f"    Saved: {filepath}")
    
    # Create info file
    import json
    info_path = os.path.join(output_dir, "dataset_info.json")
    with open(info_path, 'w') as f:
        json.dump({
            "name": "Photogrammetry Test Dataset",
            "description": "Overlapping views of a crime scene for 3D reconstruction testing",
            "num_images": num_views,
            "images": images_info,
        }, f, indent=2)
    
    print(f"\nDataset created successfully!")
    print(f"  Location: {output_dir}")
    print(f"  Images: {num_views}")
    print(f"  Info file: {info_path}")
    print(f"\nUpload these images to test real 3D reconstruction.")
    
    return output_dir


if __name__ == "__main__":
    output_path = os.path.join(os.path.dirname(__file__), "photogrammetry_test_images")
    create_photogrammetry_dataset(output_path, num_views=8)
