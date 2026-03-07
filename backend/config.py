"""
Configuration module for Crime Scene Reconstruction System
"""
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # Application Info
    APP_NAME: str = "Crime Scene Reconstruction System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # API Configuration
    API_PREFIX: str = "/api"
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:3001", 
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:5173",
        # Add your Vercel deployment URLs
        os.getenv("FRONTEND_URL", "http://localhost:3000"),
    ]
    
    # Allow all Vercel preview deployments
    CORS_ALLOW_ALL_ORIGINS: bool = os.getenv("CORS_ALLOW_ALL", "false").lower() == "true"
    
    # File Storage
    BASE_DIR: Path = Path(__file__).parent
    DATA_DIR: Path = BASE_DIR / "data"
    UPLOAD_DIR: Path = DATA_DIR / "uploads"
    PROJECTS_DIR: Path = DATA_DIR / "projects"
    MODELS_DIR: Path = DATA_DIR / "models"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    TEMP_DIR: Path = DATA_DIR / "temp"
    
    # Database
    DATABASE_URL: str = f"sqlite+aiosqlite:///{Path(__file__).parent / 'data' / 'forensic.db'}"
    
    # File Upload Limits
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB per file
    MAX_FILES_PER_PROJECT: int = 200
    ALLOWED_IMAGE_EXTENSIONS: set = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".dng", ".cr2", ".nef", ".arw"}
    
    # Image Processing
    IMAGE_QUALITY_THRESHOLD: float = 0.5  # Minimum quality score (0-1)
    MIN_IMAGE_RESOLUTION: tuple = (100, 100)  # Minimum width x height (lowered for flexibility)
    FEATURE_DETECTOR: str = "SIFT"  # SIFT, SURF, ORB
    
    # Photogrammetry Settings
    MIN_OVERLAP_PERCENTAGE: float = 60.0
    MAX_OVERLAP_PERCENTAGE: float = 80.0
    MIN_MATCHES_THRESHOLD: int = 10  # Minimum feature matches between image pairs (lowered for better compatibility)
    RECONSTRUCTION_QUALITY: str = "high"  # low, medium, high, ultra
    
    # 3D Reconstruction
    POINT_CLOUD_DENSITY: str = "high"  # low, medium, high
    MESH_DECIMATION_RATIO: float = 0.2  # Reduce mesh complexity (0-1)
    TEXTURE_RESOLUTION: int = 4096  # Texture map resolution
    
    # Measurement Accuracy
    DEFAULT_MEASUREMENT_UNIT: str = "meters"
    MEASUREMENT_PRECISION: int = 4  # Decimal places
    ACCURACY_THRESHOLD_CM: float = 5.0  # Target accuracy in centimeters
    
    # Geospatial
    DEFAULT_CRS: str = "EPSG:4326"  # WGS84
    INDIAN_GRID_CRS: str = "EPSG:7755"  # Indian National Grid
    SATELLITE_PROVIDER: str = "OpenStreetMap"  # OpenStreetMap, Mapbox, Google
    
    # Report Generation
    REPORT_TEMPLATE: str = "forensic_standard"
    INCLUDE_AUDIT_TRAIL: bool = True
    DIGITAL_SIGNATURE: bool = True
    REPORT_LANGUAGE: str = "en-IN"
    
    # Forensic Compliance (Indian Evidence Act)
    CHAIN_OF_CUSTODY_ENABLED: bool = True
    HASH_ALGORITHM: str = "SHA256"
    TIMESTAMP_VERIFICATION: bool = True
    EXAMINER_CERTIFICATION_REQUIRED: bool = True
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Processing
    MAX_WORKER_THREADS: int = 4
    ENABLE_GPU: bool = True
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = BASE_DIR / "logs" / "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        directories = [
            self.DATA_DIR,
            self.UPLOAD_DIR,
            self.PROJECTS_DIR,
            self.MODELS_DIR,
            self.REPORTS_DIR,
            self.TEMP_DIR,
            self.LOG_FILE.parent
        ]
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)


# Global settings instance
settings = Settings()
settings.ensure_directories()
