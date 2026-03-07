"""
Image Processing Service
Handles image validation, EXIF extraction, and preprocessing
"""
import cv2
import numpy as np
from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
import piexif
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from config import settings
from services.chain_of_custody import ChainOfCustodyService

logger = logging.getLogger(__name__)


class ImageProcessor:
    """Image processing and metadata extraction"""
    
    @staticmethod
    def validate_image(file_path: Path) -> Tuple[bool, str]:
        """
        Validate if file is a valid image
        
        Args:
            file_path: Path to image file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            # Check file extension
            if file_path.suffix.lower() not in settings.ALLOWED_IMAGE_EXTENSIONS:
                return False, f"Unsupported file extension: {file_path.suffix}"
            
            # Try to open with PIL
            with Image.open(file_path) as img:
                # Check minimum resolution
                width, height = img.size
                min_width, min_height = settings.MIN_IMAGE_RESOLUTION
                
                if width < min_width or height < min_height:
                    return False, f"Image resolution too low: {width}x{height} (minimum: {min_width}x{min_height})"
                
                # Verify image integrity
                img.verify()
            
            # Re-open for additional checks (verify closes the file)
            with Image.open(file_path) as img:
                # Check if image can be converted to RGB
                img.convert('RGB')
            
            return True, "Image is valid"
            
        except Exception as e:
            return False, f"Invalid image file: {str(e)}"
    
    @staticmethod
    def extract_exif_data(file_path: Path) -> Dict[str, Any]:
        """
        Extract EXIF metadata from image
        
        Args:
            file_path: Path to image file
            
        Returns:
            Dictionary containing EXIF data
        """
        metadata = {
            "filename": file_path.name,
            "file_size": file_path.stat().st_size,
            "width": None,
            "height": None,
            "format": None,
            "camera_make": None,
            "camera_model": None,
            "date_taken": None,
            "exposure_time": None,
            "f_number": None,
            "iso": None,
            "focal_length": None,
            "gps_latitude": None,
            "gps_longitude": None,
            "gps_altitude": None,
            "gps_timestamp": None,
        }
        
        try:
            with Image.open(file_path) as img:
                # Basic image info
                metadata["width"], metadata["height"] = img.size
                metadata["format"] = img.format
                
                # Extract EXIF data
                exif_data = img._getexif()
                
                if exif_data:
                    for tag_id, value in exif_data.items():
                        tag_name = TAGS.get(tag_id, tag_id)
                        
                        # Camera information
                        if tag_name == "Make":
                            metadata["camera_make"] = str(value).strip()
                        elif tag_name == "Model":
                            metadata["camera_model"] = str(value).strip()
                        
                        # Date and time
                        elif tag_name == "DateTimeOriginal" or tag_name == "DateTime":
                            try:
                                metadata["date_taken"] = datetime.strptime(
                                    str(value), "%Y:%m:%d %H:%M:%S"
                                )
                            except:
                                pass
                        
                        # Exposure settings
                        elif tag_name == "ExposureTime":
                            # Standardize shutter speed representation
                            if isinstance(value, tuple):
                                if value[1] != 0:
                                    metadata["exposure_time"] = f"{value[0]}/{value[1]}"
                            else:
                                metadata["exposure_time"] = str(value)
                        elif tag_name == "FNumber":
                            if isinstance(value, tuple):
                                metadata["f_number"] = float(value[0]) / float(value[1])
                            else:
                                metadata["f_number"] = float(value)
                        elif tag_name == "ISOSpeedRatings" or tag_name == "ISO":
                            metadata["iso"] = int(value)
                        elif tag_name == "FocalLength":
                            if isinstance(value, tuple):
                                metadata["focal_length"] = float(value[0]) / float(value[1])
                            else:
                                metadata["focal_length"] = float(value)
                        
                        # GPS data
                        elif tag_name == "GPSInfo":
                            gps_data = ImageProcessor._parse_gps_info(value)
                            metadata.update(gps_data)
                
        except Exception as e:
            logger.warning(f"Error extracting EXIF from {file_path}: {e}")
        
        return metadata
    
    @staticmethod
    def _parse_gps_info(gps_info: Dict) -> Dict[str, Any]:
        """
        Parse GPS information from EXIF
        
        Args:
            gps_info: GPS info dictionary from EXIF
            
        Returns:
            Dictionary with parsed GPS coordinates
        """
        gps_data = {
            "gps_latitude": None,
            "gps_longitude": None,
            "gps_altitude": None,
            "gps_timestamp": None
        }
        
        try:
            # Helper function to convert GPS coordinates
            def convert_to_degrees(value):
                d = float(value[0])
                m = float(value[1])
                s = float(value[2])
                return d + (m / 60.0) + (s / 3600.0)
            
            # Latitude
            if 2 in gps_info and 1 in gps_info:  # GPSLatitude and GPSLatitudeRef
                lat = convert_to_degrees(gps_info[2])
                if gps_info[1] == 'S':
                    lat = -lat
                gps_data["gps_latitude"] = lat
            
            # Longitude
            if 4 in gps_info and 3 in gps_info:  # GPSLongitude and GPSLongitudeRef
                lon = convert_to_degrees(gps_info[4])
                if gps_info[3] == 'W':
                    lon = -lon
                gps_data["gps_longitude"] = lon
            
            # Altitude
            if 6 in gps_info:  # GPSAltitude
                alt = float(gps_info[6])
                if 5 in gps_info and gps_info[5] == 1:  # Below sea level
                    alt = -alt
                gps_data["gps_altitude"] = alt
            
        except Exception as e:
            logger.warning(f"Error parsing GPS data: {e}")
        
        return gps_data
    
    @staticmethod
    def assess_image_quality(file_path: Path) -> float:
        """
        Assess image quality using various metrics
        
        Args:
            file_path: Path to image file
            
        Returns:
            Quality score between 0 and 1
        """
        try:
            # Read image with OpenCV
            img = cv2.imread(str(file_path))
            if img is None:
                return 0.0
            
            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Calculate sharpness using Laplacian variance
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 500.0, 1.0)  # Normalize
            
            # Calculate brightness
            mean_brightness = np.mean(gray)
            # Optimal brightness is around 127 (middle gray)
            brightness_score = 1.0 - abs(mean_brightness - 127) / 127.0
            
            # Calculate contrast
            contrast = gray.std()
            contrast_score = min(contrast / 64.0, 1.0)  # Normalize
            
            # Combined quality score (weighted average)
            quality_score = (
                0.5 * sharpness_score +
                0.25 * brightness_score +
                0.25 * contrast_score
            )
            
            return round(quality_score, 3)
            
        except Exception as e:
            logger.error(f"Error assessing image quality: {e}")
            return 0.0
    
    @staticmethod
    def extract_features(file_path: Path, detector_type: str = None) -> Tuple[Any, Any]:
        """
        Extract features from image for photogrammetry
        
        Args:
            file_path: Path to image file
            detector_type: Feature detector type (SIFT, ORB, etc.)
            
        Returns:
            Tuple of (keypoints, descriptors)
        """
        if detector_type is None:
            detector_type = settings.FEATURE_DETECTOR
        
        try:
            # Read image
            img = cv2.imread(str(file_path))
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Create feature detector
            if detector_type == "SIFT":
                detector = cv2.SIFT_create()
            elif detector_type == "ORB":
                detector = cv2.ORB_create(nfeatures=2000)
            elif detector_type == "AKAZE":
                detector = cv2.AKAZE_create()
            else:
                raise ValueError(f"Unsupported detector: {detector_type}")
            
            # Detect keypoints and compute descriptors
            keypoints, descriptors = detector.detectAndCompute(gray, None)
            
            logger.info(f"Detected {len(keypoints)} features in {file_path.name}")
            return keypoints, descriptors
            
        except Exception as e:
            logger.error(f"Error extracting features: {e}")
            return None, None
    
    @staticmethod
    def preprocess_image(
        file_path: Path,
        output_path: Path,
        max_size: Tuple[int, int] = (4096, 4096),
        enhance: bool = True
    ) -> bool:
        """
        Preprocess image for photogrammetry
        
        Args:
            file_path: Input image path
            output_path: Output image path
            max_size: Maximum dimensions (width, height)
            enhance: Whether to enhance image
            
        Returns:
            True if successful
        """
        try:
            with Image.open(file_path) as img:
                # Convert to RGB
                img = img.convert('RGB')
                
                # Resize if necessary
                if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                    img.thumbnail(max_size, Image.Resampling.LANCZOS)
                
                # Enhance if requested
                if enhance:
                    # Auto-adjust levels using OpenCV
                    cv_img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
                    
                    # CLAHE (Contrast Limited Adaptive Histogram Equalization)
                    lab = cv2.cvtColor(cv_img, cv2.COLOR_BGR2LAB)
                    l, a, b = cv2.split(lab)
                    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
                    l = clahe.apply(l)
                    enhanced = cv2.merge([l, a, b])
                    cv_img = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)
                    
                    img = Image.fromarray(cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB))
                
                # Save
                img.save(output_path, quality=95, optimize=True)
                logger.info(f"Preprocessed image saved to {output_path}")
                return True
                
        except Exception as e:
            logger.error(f"Error preprocessing image: {e}")
            return False
