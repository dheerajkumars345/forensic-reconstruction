"""
Forensic Image Validator Service
Implements guardrails to ensure uploaded images meet forensic evidence standards
"""
import cv2
import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Tuple, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(str, Enum):
    """Severity levels for validation warnings"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class ForensicValidator:
    """
    Validates images for forensic suitability and generates warnings/flags
    """
    
    # Expected characteristics for crime scene images
    MIN_RECOMMENDED_RESOLUTION = (1920, 1080)  # HD minimum for forensic work
    MIN_FEATURE_COUNT = 100  # Minimum SIFT features for reconstruction
    EXPECTED_EXIF_FIELDS = ["camera_make", "camera_model", "date_taken"]
    
    # Color distribution thresholds for scene type detection
    OUTDOOR_SKY_THRESHOLD = 0.15  # % of blue pixels suggesting outdoor/sky
    FOOD_COLOR_THRESHOLD = 0.20  # % of warm colors suggesting food imagery
    
    @staticmethod
    def validate_forensic_suitability(
        file_path: Path,
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Comprehensive forensic validation of an image
        
        Args:
            file_path: Path to the image file
            metadata: Extracted EXIF metadata
            
        Returns:
            Dictionary containing:
            - is_suitable: bool - Whether image is suitable for forensic use
            - forensic_score: float - Overall forensic suitability score (0-1)
            - warnings: List of warning messages
            - flags: Dict of specific issue flags
            - recommendations: List of recommendations
        """
        result = {
            "is_suitable": True,
            "forensic_score": 1.0,
            "warnings": [],
            "flags": {
                "missing_metadata": False,
                "low_quality": False,
                "low_resolution": False,
                "insufficient_features": False,
                "potentially_irrelevant": False,
                "missing_gps": False,
                "missing_timestamp": False,
                "missing_camera_info": False,
            },
            "recommendations": [],
            "content_analysis": {}
        }
        
        score_deductions = []
        
        # 1. Check EXIF metadata completeness
        metadata_result = ForensicValidator._check_metadata_completeness(metadata)
        result["warnings"].extend(metadata_result["warnings"])
        result["flags"].update(metadata_result["flags"])
        score_deductions.extend(metadata_result["deductions"])
        result["recommendations"].extend(metadata_result["recommendations"])
        
        # 2. Check image resolution
        resolution_result = ForensicValidator._check_resolution(metadata)
        result["warnings"].extend(resolution_result["warnings"])
        result["flags"].update(resolution_result["flags"])
        score_deductions.extend(resolution_result["deductions"])
        result["recommendations"].extend(resolution_result["recommendations"])
        
        # 3. Analyze image content for relevance
        content_result = ForensicValidator._analyze_content(file_path)
        result["warnings"].extend(content_result["warnings"])
        result["flags"].update(content_result["flags"])
        score_deductions.extend(content_result["deductions"])
        result["content_analysis"] = content_result["analysis"]
        result["recommendations"].extend(content_result["recommendations"])
        
        # 4. Check feature detectability for reconstruction
        feature_result = ForensicValidator._check_feature_count(file_path)
        result["warnings"].extend(feature_result["warnings"])
        result["flags"].update(feature_result["flags"])
        score_deductions.extend(feature_result["deductions"])
        result["recommendations"].extend(feature_result["recommendations"])
        
        # Calculate final score
        total_deduction = sum(score_deductions)
        result["forensic_score"] = max(0.0, round(1.0 - total_deduction, 2))
        
        # Determine overall suitability
        if result["forensic_score"] < 0.3:
            result["is_suitable"] = False
        elif result["flags"]["potentially_irrelevant"]:
            result["is_suitable"] = False
            
        return result
    
    @staticmethod
    def _check_metadata_completeness(metadata: Dict[str, Any]) -> Dict:
        """Check if essential forensic metadata is present"""
        result = {
            "warnings": [],
            "flags": {},
            "deductions": [],
            "recommendations": []
        }
        
        # Check camera information
        if not metadata.get("camera_make") and not metadata.get("camera_model"):
            result["warnings"].append({
                "severity": ValidationSeverity.WARNING,
                "message": "No camera information found in EXIF data",
                "code": "MISSING_CAMERA_INFO"
            })
            result["flags"]["missing_camera_info"] = True
            result["deductions"].append(0.1)
            result["recommendations"].append(
                "Use a camera that embeds EXIF metadata for chain of custody compliance"
            )
        
        # Check timestamp
        if not metadata.get("date_taken"):
            result["warnings"].append({
                "severity": ValidationSeverity.WARNING,
                "message": "No capture timestamp found - cannot verify when image was taken",
                "code": "MISSING_TIMESTAMP"
            })
            result["flags"]["missing_timestamp"] = True
            result["deductions"].append(0.15)
            result["recommendations"].append(
                "Enable date/time on camera settings for temporal evidence tracking"
            )
        
        # Check GPS coordinates
        if not metadata.get("gps_latitude") or not metadata.get("gps_longitude"):
            result["warnings"].append({
                "severity": ValidationSeverity.INFO,
                "message": "No GPS coordinates found - location cannot be auto-detected",
                "code": "MISSING_GPS"
            })
            result["flags"]["missing_gps"] = True
            result["deductions"].append(0.05)
            result["recommendations"].append(
                "Enable GPS tagging on camera or use a GPS-enabled device"
            )
        
        # Overall metadata check
        missing_count = sum([
            not metadata.get("camera_make"),
            not metadata.get("camera_model"),
            not metadata.get("date_taken"),
            not metadata.get("gps_latitude")
        ])
        
        if missing_count >= 3:
            result["flags"]["missing_metadata"] = True
            result["warnings"].append({
                "severity": ValidationSeverity.ERROR,
                "message": "Critical: Image lacks most forensic metadata - may not be admissible as evidence",
                "code": "INSUFFICIENT_METADATA"
            })
        
        return result
    
    @staticmethod
    def _check_resolution(metadata: Dict[str, Any]) -> Dict:
        """Check if resolution is adequate for forensic analysis"""
        result = {
            "warnings": [],
            "flags": {},
            "deductions": [],
            "recommendations": []
        }
        
        width = metadata.get("width", 0)
        height = metadata.get("height", 0)
        
        if width and height:
            min_w, min_h = ForensicValidator.MIN_RECOMMENDED_RESOLUTION
            
            if width < min_w or height < min_h:
                result["warnings"].append({
                    "severity": ValidationSeverity.WARNING,
                    "message": f"Resolution {width}x{height} is below recommended {min_w}x{min_h} for forensic work",
                    "code": "LOW_RESOLUTION"
                })
                result["flags"]["low_resolution"] = True
                # Calculate deduction based on how far below threshold
                ratio = (width * height) / (min_w * min_h)
                deduction = max(0.05, 0.2 * (1 - ratio))
                result["deductions"].append(deduction)
                result["recommendations"].append(
                    "Use higher resolution images (minimum 1920x1080) for detailed analysis"
                )
        
        return result
    
    @staticmethod
    def _analyze_content(file_path: Path) -> Dict:
        """
        Analyze image content to detect potentially irrelevant images
        Uses color histogram analysis and basic scene classification
        """
        result = {
            "warnings": [],
            "flags": {},
            "deductions": [],
            "recommendations": [],
            "analysis": {}
        }
        
        try:
            img = cv2.imread(str(file_path))
            if img is None:
                return result
                
            # Convert to different color spaces for analysis
            hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
            
            # Analyze color distribution
            h, s, v = cv2.split(hsv)
            
            # Calculate color statistics
            result["analysis"]["mean_saturation"] = float(np.mean(s))
            result["analysis"]["mean_brightness"] = float(np.mean(v))
            result["analysis"]["color_variance"] = float(np.std(hsv))
            
            # Detect overly saturated/colorful images (potential food/product photos)
            high_saturation_pixels = np.sum(s > 180) / s.size
            result["analysis"]["high_saturation_ratio"] = float(high_saturation_pixels)
            
            # Detect warm colors (reds, oranges, yellows) - common in food
            warm_mask = ((h < 30) | (h > 160)) & (s > 100)
            warm_ratio = np.sum(warm_mask) / h.size
            result["analysis"]["warm_color_ratio"] = float(warm_ratio)
            
            # Detect blue sky (outdoor non-indoor scenes)
            blue_mask = (h > 90) & (h < 130) & (s > 50) & (v > 100)
            sky_ratio = np.sum(blue_mask) / h.size
            result["analysis"]["sky_ratio"] = float(sky_ratio)
            
            # Detect if image has very uniform colors (synthetic/graphic)
            unique_colors = len(np.unique(img.reshape(-1, 3), axis=0))
            color_diversity = unique_colors / (img.shape[0] * img.shape[1])
            result["analysis"]["color_diversity"] = float(color_diversity)
            
            # Flag potentially irrelevant content
            is_potentially_irrelevant = False
            irrelevance_reasons = []
            
            # Check for food-like color patterns
            if warm_ratio > ForensicValidator.FOOD_COLOR_THRESHOLD and high_saturation_pixels > 0.3:
                irrelevance_reasons.append("High saturation with warm colors (possible food/product image)")
                is_potentially_irrelevant = True
            
            # Check for very low color diversity (graphics/screenshots)
            if color_diversity < 0.001:
                irrelevance_reasons.append("Very low color diversity (possible screenshot/graphic)")
                is_potentially_irrelevant = True
            
            # Check for excessive brightness uniformity (possible blank/test image)
            if np.std(v) < 10:
                irrelevance_reasons.append("Uniform brightness (possible test/blank image)")
                is_potentially_irrelevant = True
            
            if is_potentially_irrelevant:
                result["flags"]["potentially_irrelevant"] = True
                result["warnings"].append({
                    "severity": ValidationSeverity.ERROR,
                    "message": f"Image may not be crime scene related: {'; '.join(irrelevance_reasons)}",
                    "code": "POTENTIALLY_IRRELEVANT"
                })
                result["deductions"].append(0.5)
                result["recommendations"].append(
                    "Please verify this image is relevant to the forensic case"
                )
            
            # Check for low contrast (poor forensic utility)
            contrast = np.std(v)
            if contrast < 30:
                result["warnings"].append({
                    "severity": ValidationSeverity.WARNING,
                    "message": "Low contrast image may have reduced forensic utility",
                    "code": "LOW_CONTRAST"
                })
                result["flags"]["low_quality"] = True
                result["deductions"].append(0.1)
                
        except Exception as e:
            logger.error(f"Error analyzing image content: {e}")
            
        return result
    
    @staticmethod
    def _check_feature_count(file_path: Path) -> Dict:
        """Check if image has sufficient features for 3D reconstruction"""
        result = {
            "warnings": [],
            "flags": {},
            "deductions": [],
            "recommendations": []
        }
        
        try:
            img = cv2.imread(str(file_path))
            if img is None:
                return result
                
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            # Use SIFT to detect features
            sift = cv2.SIFT_create()
            keypoints = sift.detect(gray, None)
            feature_count = len(keypoints)
            
            result["analysis"] = {"feature_count": feature_count}
            
            if feature_count < ForensicValidator.MIN_FEATURE_COUNT:
                result["warnings"].append({
                    "severity": ValidationSeverity.WARNING,
                    "message": f"Only {feature_count} features detected - may be insufficient for 3D reconstruction",
                    "code": "INSUFFICIENT_FEATURES"
                })
                result["flags"]["insufficient_features"] = True
                result["deductions"].append(0.15)
                result["recommendations"].append(
                    "Images with more texture and detail work better for reconstruction"
                )
            elif feature_count < ForensicValidator.MIN_FEATURE_COUNT * 3:
                result["warnings"].append({
                    "severity": ValidationSeverity.INFO,
                    "message": f"{feature_count} features detected - adequate but more would improve reconstruction",
                    "code": "LOW_FEATURES"
                })
                result["deductions"].append(0.05)
                
        except Exception as e:
            logger.error(f"Error checking features: {e}")
            
        return result
    
    @staticmethod
    def get_validation_summary(validation_results: List[Dict]) -> Dict:
        """
        Generate a summary of validation results for multiple images
        
        Args:
            validation_results: List of validation result dicts
            
        Returns:
            Summary statistics and recommendations
        """
        if not validation_results:
            return {"total": 0, "suitable": 0, "warnings": 0, "rejected": 0}
        
        suitable_count = sum(1 for r in validation_results if r["is_suitable"])
        warning_count = sum(1 for r in validation_results if r["warnings"] and r["is_suitable"])
        rejected_count = sum(1 for r in validation_results if not r["is_suitable"])
        
        avg_score = sum(r["forensic_score"] for r in validation_results) / len(validation_results)
        
        # Collect all unique warnings
        all_warnings = []
        for r in validation_results:
            all_warnings.extend(r["warnings"])
        
        # Count warning types
        warning_codes = {}
        for w in all_warnings:
            code = w.get("code", "UNKNOWN")
            warning_codes[code] = warning_codes.get(code, 0) + 1
        
        return {
            "total": len(validation_results),
            "suitable": suitable_count,
            "with_warnings": warning_count,
            "rejected": rejected_count,
            "average_forensic_score": round(avg_score, 2),
            "warning_summary": warning_codes,
            "overall_recommendation": ForensicValidator._get_overall_recommendation(
                suitable_count, rejected_count, avg_score
            )
        }
    
    @staticmethod
    def _get_overall_recommendation(suitable: int, rejected: int, avg_score: float) -> str:
        """Generate overall recommendation based on validation results"""
        if rejected > suitable:
            return "Most images appear unsuitable for forensic analysis. Please review and upload appropriate crime scene photographs."
        elif avg_score < 0.5:
            return "Image set has significant quality issues. Consider re-capturing with proper forensic photography techniques."
        elif avg_score < 0.7:
            return "Image set is usable but has some quality concerns. Review warnings for specific improvements."
        else:
            return "Image set meets forensic standards. Proceed with analysis."
