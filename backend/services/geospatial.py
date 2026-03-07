"""
Geospatial Service
Handles GPS coordinates, geolocation, and mapping
"""
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import pyproj
from typing import Optional, Dict, Tuple, Any
import logging

from config import settings

logger = logging.getLogger(__name__)


class GeospatialService:
    """Geospatial operations and coordinate transformations"""
    
    def __init__(self):
        self.geocoder = Nominatim(user_agent=settings.APP_NAME)
        self.wgs84 = pyproj.CRS(settings.DEFAULT_CRS)
        self.indian_grid = pyproj.CRS(settings.INDIAN_GRID_CRS)
    
    def reverse_geocode(self, latitude: float, longitude: float) -> Optional[Dict[str, Any]]:
        """
        Get address from coordinates
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            
        Returns:
            Dictionary with address information
        """
        try:
            location = self.geocoder.reverse(
                f"{latitude}, {longitude}",
                language="en"
            )
            
            if location:
                return {
                    "address": location.address,
                    "raw": location.raw,
                    "latitude": location.latitude,
                    "longitude": location.longitude
                }
            return None
            
        except Exception as e:
            logger.error(f"Reverse geocoding error: {e}")
            return None
    
    def geocode(self, address: str) -> Optional[Dict[str, Any]]:
        """
        Get coordinates from address
        
        Args:
            address: Address string
            
        Returns:
            Dictionary with location information
        """
        try:
            location = self.geocoder.geocode(address)
            
            if location:
                return {
                    "address": location.address,
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "raw": location.raw
                }
            return None
            
        except Exception as e:
            logger.error(f"Geocoding error: {e}")
            return None
    
    def calculate_distance(
        self,
        coord1: Tuple[float, float],
        coord2: Tuple[float, float]
    ) -> float:
        """
        Calculate distance between two GPS coordinates
        
        Args:
            coord1: Tuple of (latitude, longitude)
            coord2: Tuple of (latitude, longitude)
            
        Returns:
            Distance in meters
        """
        try:
            distance = geodesic(coord1, coord2).meters
            return distance
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            return 0.0
    
    def transform_coordinates(
        self,
        latitude: float,
        longitude: float,
        from_crs: str = None,
        to_crs: str = None
    ) -> Tuple[float, float]:
        """
        Transform coordinates between coordinate systems
        
        Args:
            latitude: Latitude
            longitude: Longitude
            from_crs: Source CRS (default: WGS84)
            to_crs: Target CRS (default: Indian Grid)
            
        Returns:
            Tuple of transformed coordinates
        """
        try:
            if from_crs is None:
                from_crs = settings.DEFAULT_CRS
            if to_crs is None:
                to_crs = settings.INDIAN_GRID_CRS
            
            transformer = pyproj.Transformer.from_crs(
                from_crs, to_crs, always_xy=True
            )
            
            x, y = transformer.transform(longitude, latitude)
            return (x, y)
            
        except Exception as e:
            logger.error(f"Coordinate transformation error: {e}")
            return (longitude, latitude)
    
    def format_coordinates(
        self,
        latitude: float,
        longitude: float,
        format_type: str = "decimal"
    ) -> str:
        """
        Format coordinates in different notation systems
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            format_type: Format type (decimal, dms, utm)
            
        Returns:
            Formatted coordinate string
        """
        if format_type == "decimal":
            return f"{latitude:.6f}, {longitude:.6f}"
        
        elif format_type == "dms":
            # Convert to degrees, minutes, seconds
            def to_dms(coord, is_latitude):
                abs_coord = abs(coord)
                degrees = int(abs_coord)
                minutes_float = (abs_coord - degrees) * 60
                minutes = int(minutes_float)
                seconds = (minutes_float - minutes) * 60
                
                if is_latitude:
                    direction = "N" if coord >= 0 else "S"
                else:
                    direction = "E" if coord >= 0 else "W"
                
                return f"{degrees}°{minutes}'{seconds:.2f}\"{direction}"
            
            lat_dms = to_dms(latitude, True)
            lon_dms = to_dms(longitude, False)
            return f"{lat_dms}, {lon_dms}"
        
        elif format_type == "utm":
            # Convert to UTM
            utm = pyproj.CRS("EPSG:32643")  # UTM Zone 43N (India)
            transformer = pyproj.Transformer.from_crs(
                "EPSG:4326", utm, always_xy=True
            )
            easting, northing = transformer.transform(longitude, latitude)
            return f"UTM: {easting:.2f}E, {northing:.2f}N"
        
        return f"{latitude}, {longitude}"
    
    def get_bounding_box(
        self,
        coordinates: list[Tuple[float, float]],
        buffer_meters: float = 100
    ) -> Dict[str, float]:
        """
        Calculate bounding box for a set of coordinates with buffer
        
        Args:
            coordinates: List of (latitude, longitude) tuples
            buffer_meters: Buffer distance in meters
            
        Returns:
            Dictionary with min/max lat/lon
        """
        if not coordinates:
            return None
        
        lats = [coord[0] for coord in coordinates]
        lons = [coord[1] for coord in coordinates]
        
        # Calculate buffer in degrees (approximate)
        buffer_degrees = buffer_meters / 111000  # Rough conversion
        
        return {
            "min_lat": min(lats) - buffer_degrees,
            "max_lat": max(lats) + buffer_degrees,
            "min_lon": min(lons) - buffer_degrees,
            "max_lon": max(lons) + buffer_degrees
        }
    
    def generate_map_url(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 16,
        provider: str = None
    ) -> str:
        """
        Generate URL for satellite/map view
        
        Args:
            latitude: Latitude
            longitude: Longitude
            zoom: Zoom level
            provider: Map provider (osm, google, mapbox)
            
        Returns:
            URL string
        """
        if provider is None:
            provider = settings.SATELLITE_PROVIDER.lower()
        
        if provider == "openstreetmap" or provider == "osm":
            return f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map={zoom}/{latitude}/{longitude}"
        elif provider == "google":
            return f"https://www.google.com/maps/@{latitude},{longitude},{zoom}z"
        else:
            return f"https://www.openstreetmap.org/?mlat={latitude}&mlon={longitude}#map={zoom}/{latitude}/{longitude}"
