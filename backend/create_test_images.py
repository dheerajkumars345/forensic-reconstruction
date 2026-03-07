"""
Create realistic test forensic images with full EXIF metadata for testing.
Generates multiple crime scene simulation images with GPS, camera info, timestamps.
"""
import os
from PIL import Image, ImageDraw, ImageFont
import piexif
from datetime import datetime, timedelta
import struct
import random
from pathlib import Path

def create_gps_ifd(lat, lon, altitude=0):
    """Create GPS IFD with proper format for EXIF"""
    def to_deg(value, is_positive):
        sec = value * 3600
        deg = int(sec // 3600)
        sec -= deg * 3600
        minutes = int(sec // 60)
        sec -= minutes * 60
        return ((deg, 1), (minutes, 1), (int(sec * 100), 100)), 'N' if is_positive else 'S' if lat else ('E' if is_positive else 'W')
    
    lat_deg, lat_ref = to_deg(abs(lat), lat >= 0)
    lon_deg, lon_ref = to_deg(abs(lon), lon >= 0)
    
    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: lat_ref.encode(),
        piexif.GPSIFD.GPSLatitude: lat_deg,
        piexif.GPSIFD.GPSLongitudeRef: lon_ref.encode(),
        piexif.GPSIFD.GPSLongitude: lon_deg,
        piexif.GPSIFD.GPSAltitudeRef: 0,  # Above sea level
        piexif.GPSIFD.GPSAltitude: (int(altitude * 100), 100),
    }
    return gps_ifd

def create_forensic_image(
    filepath: str,
    image_num: int,
    lat: float,
    lon: float,
    altitude: float,
    timestamp: datetime,
    camera_make: str,
    camera_model: str,
    scene_description: str
):
    """Create a simulated forensic crime scene image with full EXIF data"""
    
    # Create image with forensic-looking content
    width, height = 4032, 3024  # Realistic smartphone resolution
    img = Image.new('RGB', (width, height), color='#2a2a2a')
    draw = ImageDraw.Draw(img)
    
    # Draw grid pattern (like floor tiles)
    grid_size = 150
    for x in range(0, width, grid_size):
        draw.line([(x, 0), (x, height)], fill='#3a3a3a', width=2)
    for y in range(0, height, grid_size):
        draw.line([(0, y), (width, y)], fill='#3a3a3a', width=2)
    
    # Draw evidence markers (yellow numbered cones)
    markers = [
        (800, 1200, "1"),
        (2200, 1800, "2"),
        (1500, 2400, "3"),
        (3200, 1000, "4"),
    ]
    for mx, my, num in markers:
        # Yellow triangle marker
        draw.polygon([(mx, my-80), (mx-50, my+40), (mx+50, my+40)], fill='#ffc107')
        draw.polygon([(mx, my-60), (mx-35, my+25), (mx+35, my+25)], fill='#000')
        # Number
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except:
            font = ImageFont.load_default()
        draw.text((mx-10, my-30), num, fill='#ffc107', font=font)
    
    # Draw scale ruler
    ruler_y = height - 200
    ruler_start = 200
    ruler_length = 1000  # 1 meter scale
    draw.rectangle([ruler_start, ruler_y, ruler_start + ruler_length, ruler_y + 50], fill='white')
    for i in range(11):
        x = ruler_start + (i * ruler_length // 10)
        draw.line([(x, ruler_y), (x, ruler_y + 50)], fill='black', width=3)
        if i % 2 == 0:
            draw.text((x - 20, ruler_y + 55), f"{i*10}cm", fill='white')
    
    # Draw some "evidence" shapes
    # Blood spatter pattern
    for _ in range(50):
        x = random.randint(1000, 2500)
        y = random.randint(800, 1600)
        r = random.randint(5, 25)
        draw.ellipse([x-r, y-r, x+r, y+r], fill='#8b0000')
    
    # Shoe print
    draw.ellipse([2800, 2000, 2950, 2300], fill='#444', outline='#555')
    
    # Case number watermark
    draw.text((50, 50), f"CASE: FSL-2026-{image_num:04d}", fill='#c69749')
    draw.text((50, 100), f"IMAGE: {image_num}/4", fill='#888')
    draw.text((50, 150), scene_description, fill='#666')
    
    # Create EXIF data
    zeroth_ifd = {
        piexif.ImageIFD.Make: camera_make.encode(),
        piexif.ImageIFD.Model: camera_model.encode(),
        piexif.ImageIFD.Software: "Forensic Evidence Capture v2.1".encode(),
        piexif.ImageIFD.DateTime: timestamp.strftime("%Y:%m:%d %H:%M:%S").encode(),
        piexif.ImageIFD.ImageWidth: width,
        piexif.ImageIFD.ImageLength: height,
        piexif.ImageIFD.XResolution: (300, 1),
        piexif.ImageIFD.YResolution: (300, 1),
    }
    
    exif_ifd = {
        piexif.ExifIFD.DateTimeOriginal: timestamp.strftime("%Y:%m:%d %H:%M:%S").encode(),
        piexif.ExifIFD.DateTimeDigitized: timestamp.strftime("%Y:%m:%d %H:%M:%S").encode(),
        piexif.ExifIFD.ExifVersion: b"0232",
        piexif.ExifIFD.ColorSpace: 1,  # sRGB
        piexif.ExifIFD.PixelXDimension: width,
        piexif.ExifIFD.PixelYDimension: height,
        piexif.ExifIFD.FocalLength: (26, 1),  # 26mm
        piexif.ExifIFD.FocalLengthIn35mmFilm: 26,
        piexif.ExifIFD.ISOSpeedRatings: 400,
        piexif.ExifIFD.ExposureTime: (1, 60),  # 1/60s
        piexif.ExifIFD.FNumber: (28, 10),  # f/2.8
        piexif.ExifIFD.ExposureProgram: 2,  # Normal program
        piexif.ExifIFD.MeteringMode: 5,  # Pattern
        piexif.ExifIFD.Flash: 0,  # No flash
        piexif.ExifIFD.WhiteBalance: 0,  # Auto
        piexif.ExifIFD.LensModel: "26mm f/2.8".encode(),
    }
    
    gps_ifd = create_gps_ifd(lat, lon, altitude)
    
    exif_dict = {
        "0th": zeroth_ifd,
        "Exif": exif_ifd,
        "GPS": gps_ifd,
        "1st": {},
    }
    
    exif_bytes = piexif.dump(exif_dict)
    
    # Save image with EXIF
    img.save(filepath, "JPEG", quality=95, exif=exif_bytes)
    print(f"Created: {filepath}")
    print(f"  GPS: {lat:.6f}, {lon:.6f}, Alt: {altitude}m")
    print(f"  Camera: {camera_make} {camera_model}")
    print(f"  Time: {timestamp}")

def main():
    """Create a set of test forensic images"""
    output_dir = Path("test_forensic_images")
    output_dir.mkdir(exist_ok=True)
    
    # Crime scene location: India - Hyderabad area
    base_lat = 17.385044
    base_lon = 78.486671
    base_time = datetime(2026, 3, 7, 14, 30, 0)
    
    # Image configurations - multiple angles/positions of same scene
    images = [
        {
            "num": 1,
            "lat": base_lat,
            "lon": base_lon,
            "alt": 540.5,
            "time_offset": 0,
            "camera": ("Nikon", "D850"),
            "desc": "Overview - Entry point"
        },
        {
            "num": 2,
            "lat": base_lat + 0.00005,  # ~5.5 meters north
            "lon": base_lon + 0.00003,  # ~3.3 meters east
            "alt": 540.8,
            "time_offset": 45,
            "camera": ("Nikon", "D850"),
            "desc": "Detail - Evidence marker 1"
        },
        {
            "num": 3,
            "lat": base_lat - 0.00003,
            "lon": base_lon + 0.00008,
            "alt": 541.2,
            "time_offset": 120,
            "camera": ("Canon", "EOS R5"),
            "desc": "Lateral view - Blood spatter"
        },
        {
            "num": 4,
            "lat": base_lat + 0.00002,
            "lon": base_lon - 0.00004,
            "alt": 540.3,
            "time_offset": 180,
            "camera": ("Canon", "EOS R5"),
            "desc": "Detail - Footprint evidence"
        },
    ]
    
    print("=" * 60)
    print("FORENSIC TEST IMAGE GENERATOR")
    print("=" * 60)
    print(f"Location: Hyderabad, India ({base_lat}, {base_lon})")
    print(f"Base Time: {base_time}")
    print("=" * 60)
    
    created_files = []
    for img_config in images:
        filepath = output_dir / f"forensic_evidence_{img_config['num']:02d}.jpg"
        create_forensic_image(
            str(filepath),
            img_config['num'],
            img_config['lat'],
            img_config['lon'],
            img_config['alt'],
            base_time + timedelta(seconds=img_config['time_offset']),
            img_config['camera'][0],
            img_config['camera'][1],
            img_config['desc']
        )
        created_files.append(str(filepath))
        print()
    
    print("=" * 60)
    print(f"Created {len(created_files)} test images in: {output_dir.absolute()}")
    print("\nTo upload via API:")
    print(f'  curl -X POST "http://localhost:8000/api/projects/1/images?demo_mode=true" \\')
    print(f'       -F "files=@{created_files[0]}" \\')
    print(f'       -F "files=@{created_files[1]}" ...')
    print("=" * 60)
    
    return created_files

if __name__ == "__main__":
    main()
