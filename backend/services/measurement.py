"""
Measurement Service
Calculates distances, areas, volumes, and angles on 3D models
"""
import numpy as np
from typing import Any, List, Dict, Tuple, Optional
import logging

from config import settings

logger = logging.getLogger(__name__)


class MeasurementService:
    """3D measurement calculations"""
    
    @staticmethod
    def calculate_distance(
        point1: Dict[str, float],
        point2: Dict[str, float],
        scale_factor: float = 1.0
    ) -> float:
        """
        Calculate Euclidean distance between two 3D points
        
        Args:
            point1: Dictionary with x, y, z coordinates
            point2: Dictionary with x, y, z coordinates
            scale_factor: Scale factor (meters per unit)
            
        Returns:
            Distance in meters
        """
        try:
            p1 = np.array([point1['x'], point1['y'], point1['z']])
            p2 = np.array([point2['x'], point2['y'], point2['z']])
            
            distance = np.linalg.norm(p2 - p1) * scale_factor
            return round(distance, settings.MEASUREMENT_PRECISION)
            
        except Exception as e:
            logger.error(f"Error calculating distance: {e}")
            return 0.0
    
    @staticmethod
    def calculate_path_length(
        points: List[Dict[str, float]],
        scale_factor: float = 1.0
    ) -> float:
        """
        Calculate total length of a path through multiple points
        
        Args:
            points: List of point dictionaries with x, y, z
            scale_factor: Scale factor (meters per unit)
            
        Returns:
            Total path length in meters
        """
        if len(points) < 2:
            return 0.0
        
        total_length = 0.0
        for i in range(len(points) - 1):
            total_length += MeasurementService.calculate_distance(
                points[i], points[i + 1], scale_factor
            )
        
        return round(total_length, settings.MEASUREMENT_PRECISION)
    
    @staticmethod
    def calculate_area(
        points: List[Dict[str, float]],
        scale_factor: float = 1.0
    ) -> float:
        """
        Calculate area of a polygon defined by points
        Uses cross product method for 3D polygons
        
        Args:
            points: List of point dictionaries (minimum 3 points)
            scale_factor: Scale factor (meters per unit)
            
        Returns:
            Area in square meters
        """
        if len(points) < 3:
            return 0.0
        
        try:
            # Convert to numpy array
            pts = np.array([[p['x'], p['y'], p['z']] for p in points])
            
            # Calculate area using Shoelace formula in 3D
            n = len(pts)
            area = 0.0
            
            # Project onto best-fit plane
            # Calculate normal vector using cross product
            v1 = pts[1] - pts[0]
            v2 = pts[2] - pts[0]
            normal = np.cross(v1, v2)
            normal = normal / np.linalg.norm(normal)
            
            # Calculate area
            for i in range(n):
                j = (i + 1) % n
                area += 0.5 * np.linalg.norm(np.cross(pts[i], pts[j]))
            
            area *= (scale_factor ** 2)
            return round(area, settings.MEASUREMENT_PRECISION)
            
        except Exception as e:
            logger.error(f"Error calculating area: {e}")
            return 0.0
    
    @staticmethod
    def calculate_volume(
        points: List[Dict[str, float]],
        scale_factor: float = 1.0
    ) -> float:
        """
        Calculate volume of a convex hull defined by points
        
        Args:
            points: List of point dictionaries
            scale_factor: Scale factor (meters per unit)
            
        Returns:
            Volume in cubic meters
        """
        if len(points) < 4:
            return 0.0
        
        try:
            from scipy.spatial import ConvexHull
            
            # Convert to numpy array
            pts = np.array([[p['x'], p['y'], p['z']] for p in points])
            
            # Calculate convex hull
            hull = ConvexHull(pts)
            volume = hull.volume * (scale_factor ** 3)
            
            return round(volume, settings.MEASUREMENT_PRECISION)
            
        except Exception as e:
            logger.error(f"Error calculating volume: {e}")
            return 0.0
    
    @staticmethod
    def calculate_angle(
        point1: Dict[str, float],
        vertex: Dict[str, float],
        point2: Dict[str, float]
    ) -> float:
        """
        Calculate angle between three points (in degrees)
        
        Args:
            point1: First point
            vertex: Vertex point (angle measured at this point)
            point2: Second point
            
        Returns:
            Angle in degrees
        """
        try:
            p1 = np.array([point1['x'], point1['y'], point1['z']])
            v = np.array([vertex['x'], vertex['y'], vertex['z']])
            p2 = np.array([point2['x'], point2['y'], point2['z']])
            
            # Create vectors from vertex
            vec1 = p1 - v
            vec2 = p2 - v
            
            # Calculate angle using dot product
            cos_angle = np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))
            # Clamp to avoid numerical errors
            cos_angle = np.clip(cos_angle, -1.0, 1.0)
            angle_rad = np.arccos(cos_angle)
            angle_deg = np.degrees(angle_rad)
            
            return round(angle_deg, settings.MEASUREMENT_PRECISION)
            
        except Exception as e:
            logger.error(f"Error calculating angle: {e}")
            return 0.0
    
    @staticmethod
    def calculate_trajectory_angle(
        start_point: Dict[str, float],
        end_point: Dict[str, float]
    ) -> Dict[str, float]:
        """
        Calculate trajectory angles (useful for ballistics)
        
        Args:
            start_point: Starting point of trajectory
            end_point: Ending point of trajectory
            
        Returns:
            Dictionary with horizontal and vertical angles
        """
        try:
            p1 = np.array([start_point['x'], start_point['y'], start_point['z']])
            p2 = np.array([end_point['x'], end_point['y'], end_point['z']])
            
            delta = p2 - p1
            
            # Horizontal angle (azimuth) in the XY plane
            horizontal_angle = np.degrees(np.arctan2(delta[1], delta[0]))
            
            # Vertical angle (elevation)
            horizontal_distance = np.sqrt(delta[0]**2 + delta[1]**2)
            vertical_angle = np.degrees(np.arctan2(delta[2], horizontal_distance))
            
            return {
                "horizontal_angle": round(horizontal_angle, settings.MEASUREMENT_PRECISION),
                "vertical_angle": round(vertical_angle, settings.MEASUREMENT_PRECISION),
                "azimuth": round((horizontal_angle + 360) % 360, settings.MEASUREMENT_PRECISION)
            }
            
        except Exception as e:
            logger.error(f"Error calculating trajectory angle: {e}")
            return {"horizontal_angle": 0.0, "vertical_angle": 0.0, "azimuth": 0.0}
    
    @staticmethod
    def estimate_uncertainty(
        measurement_value: float,
        num_points: int,
        estimated_accuracy_cm: float = None
    ) -> float:
        """
        Estimate measurement uncertainty
        
        Args:
            measurement_value: The measured value
            num_points: Number of points used in measurement
            estimated_accuracy_cm: Estimated model accuracy in cm
            
        Returns:
            Uncertainty value in same units as measurement
        """
        if estimated_accuracy_cm is None:
            estimated_accuracy_cm = settings.ACCURACY_THRESHOLD_CM
        
        # Convert to meters
        base_uncertainty = estimated_accuracy_cm / 100.0
        
        # Uncertainty increases with more points (error propagation)
        point_factor = np.sqrt(num_points)
        
        # For distances, uncertainty is proportional to length
        relative_uncertainty = base_uncertainty * point_factor
        
        return round(relative_uncertainty, settings.MEASUREMENT_PRECISION)
    
    @staticmethod
    def validate_metric_consistency(
        measurements: List[Dict[str, Any]],
        reconstruction_accuracy: float
    ) -> Dict[str, Any]:
        """
        Validate measurements against reconstruction accuracy
        
        Args:
            measurements: List of measurement dictionaries
            reconstruction_accuracy: Expected model accuracy in cm
            
        Returns:
            Dictionary with validation results
        """
        issues = []
        for m in measurements:
            if m.get('uncertainty', 0) > (reconstruction_accuracy / 50.0): # Threshold check
                issues.append(f"Measurement '{m.get('name')}' exceeds accuracy bounds.")
        
        return {
            "is_valid": len(issues) == 0,
            "issues": issues,
            "confidence_score": max(0, 1.0 - (len(issues) * 0.1))
        }

    @staticmethod
    def run_statistical_analysis(measurements: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Perform statistical analysis on a set of measurements
        
        Args:
            measurements: List of measurement dictionaries
            
        Returns:
            Dictionary with mean, std dev, etc.
        """
        values = [m.get('value', 0) for m in measurements if m.get('measurement_type') == 'distance']
        if not values:
            return {"status": "insufficient_data"}
            
        return {
            "count": len(values),
            "mean": round(float(np.mean(values)), 4),
            "std_dev": round(float(np.std(values)), 4),
            "variance": round(float(np.var(values)), 4),
            "min": round(float(np.min(values)), 4),
            "max": round(float(np.max(values)), 4)
        }
