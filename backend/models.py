"""
Data models for Crime Scene Reconstruction System
"""
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


Base = declarative_base()


# ============= Database Models (SQLAlchemy) =============

class Project(Base):
    """Forensic case project"""
    __tablename__ = "projects"
    
    id = Column(Integer, primary_key=True, index=True)
    case_number = Column(String, unique=True, index=True, nullable=False)
    case_title = Column(String, nullable=False)
    description = Column(Text)
    location = Column(String)
    incident_date = Column(DateTime)
    
    # Examiner Information
    examiner_name = Column(String, nullable=False)
    examiner_id = Column(String)
    laboratory = Column(String)
    
    # Status
    status = Column(String, default="created")  # created, processing, completed, archived
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    images = relationship("Image", back_populates="project", cascade="all, delete-orphan")
    reconstructions = relationship("Reconstruction", back_populates="project", cascade="all, delete-orphan")
    measurements = relationship("Measurement", back_populates="project", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="project", cascade="all, delete-orphan")


class Image(Base):
    """Crime scene image"""
    __tablename__ = "images"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # File Information
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    file_size = Column(Integer)
    file_hash = Column(String, nullable=False)  # SHA256
    
    # Image Metadata
    width = Column(Integer)
    height = Column(Integer)
    format = Column(String)
    camera_make = Column(String)
    camera_model = Column(String)
    
    # EXIF Data
    date_taken = Column(DateTime)
    exposure_time = Column(String)
    f_number = Column(Float)
    iso = Column(Integer)
    focal_length = Column(Float)
    
    # GPS Data
    gps_latitude = Column(Float)
    gps_longitude = Column(Float)
    gps_altitude = Column(Float)
    gps_timestamp = Column(DateTime)
    
    # Processing
    is_processed = Column(Boolean, default=False)
    quality_score = Column(Float)
    
    # Forensic Validation
    forensic_score = Column(Float)  # 0-1 score for forensic suitability
    is_verified = Column(Boolean, default=False)  # Manually verified by examiner
    validation_warnings = Column(JSON)  # List of validation warnings
    validation_flags = Column(JSON)  # Dict of validation flags
    is_suitable = Column(Boolean, default=True)  # Auto-determined suitability
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="images")


class Reconstruction(Base):
    """3D reconstruction of crime scene"""
    __tablename__ = "reconstructions"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Model Files
    point_cloud_path = Column(String)
    mesh_path = Column(String)
    texture_path = Column(String)
    
    # Reconstruction Parameters
    num_images_used = Column(Integer)
    num_points = Column(Integer)
    num_faces = Column(Integer)
    quality = Column(String)
    
    # Calibration
    scale_factor = Column(Float, default=1.0)  # meters per unit
    reference_object = Column(String)
    reference_size_meters = Column(Float)
    
    # Accuracy Metrics
    reprojection_error = Column(Float)
    point_cloud_density = Column(Float)
    estimated_accuracy_cm = Column(Float)
    
    # Processing Status
    status = Column(String, default="pending")  # pending, processing, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    started_at = Column(DateTime)
    completed_at = Column(DateTime)
    
    # Relationships
    project = relationship("Project", back_populates="reconstructions")


class Measurement(Base):
    """Measurements taken on 3D model"""
    __tablename__ = "measurements"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Measurement Type
    measurement_type = Column(String, nullable=False)  # distance, area, volume, angle, trajectory
    name = Column(String)
    description = Column(Text)
    
    # Coordinates (stored as JSON)
    coordinates = Column(JSON)  # List of 3D points
    
    # Measurement Results
    value = Column(Float)
    unit = Column(String)
    uncertainty = Column(Float)
    
    # Metadata
    created_by = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    project = relationship("Project", back_populates="measurements")


class AuditLog(Base):
    """Chain of custody and audit trail"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    
    # Event Information
    event_type = Column(String, nullable=False)  # upload, process, measure, export, etc.
    event_description = Column(Text)
    
    # User Information
    user_name = Column(String)
    user_id = Column(String)
    
    # Data Integrity
    affected_resource = Column(String)  # File path or resource ID
    resource_hash_before = Column(String)
    resource_hash_after = Column(String)
    
    # Timestamp
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Additional Data
    extra_metadata = Column("metadata", JSON)
    
    # Relationships
    project = relationship("Project", back_populates="audit_logs")


# ============= API Models (Pydantic) =============

class ProjectStatus(str, Enum):
    CREATED = "created"
    PROCESSING = "processing"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class ProjectCreate(BaseModel):
    case_number: str = Field(..., description="Unique case identification number")
    case_title: str = Field(..., description="Title of the case")
    description: Optional[str] = None
    location: Optional[str] = None
    incident_date: Optional[datetime] = None
    examiner_name: str = Field(..., description="Name of forensic examiner")
    examiner_id: Optional[str] = None
    laboratory: Optional[str] = None


class ProjectResponse(BaseModel):
    id: int
    case_number: str
    case_title: str
    description: Optional[str]
    location: Optional[str]
    incident_date: Optional[datetime]
    examiner_name: str
    examiner_id: Optional[str]
    laboratory: Optional[str]
    status: str
    created_at: datetime
    updated_at: datetime
    image_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class ImageMetadata(BaseModel):
    filename: str
    file_size: int
    file_hash: str
    width: Optional[int]
    height: Optional[int]
    format: Optional[str]
    camera_make: Optional[str]
    camera_model: Optional[str]
    date_taken: Optional[datetime]
    exposure_time: Optional[str]
    f_number: Optional[float]
    iso: Optional[int]
    focal_length: Optional[float]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    gps_altitude: Optional[float]
    quality_score: Optional[float]


class ValidationWarning(BaseModel):
    severity: str
    message: str
    code: str


class ImageResponse(BaseModel):
    id: int
    project_id: int
    filename: str
    filepath: str
    file_hash: str
    width: Optional[int]
    height: Optional[int]
    gps_latitude: Optional[float]
    gps_longitude: Optional[float]
    date_taken: Optional[datetime]
    uploaded_at: datetime
    is_processed: bool
    quality_score: Optional[float]
    # Forensic validation fields
    forensic_score: Optional[float] = None
    is_verified: bool = False
    is_suitable: bool = True
    validation_warnings: Optional[List[Dict[str, Any]]] = None
    validation_flags: Optional[Dict[str, bool]] = None
    
    class Config:
        from_attributes = True


class ReconstructionRequest(BaseModel):
    quality: str = Field(default="high", description="Reconstruction quality: low, medium, high, ultra")
    scale_reference_object: Optional[str] = None
    scale_reference_size_meters: Optional[float] = None


class ReconstructionResponse(BaseModel):
    id: int
    project_id: int
    status: str
    num_images_used: Optional[int]
    num_points: Optional[int]
    num_faces: Optional[int]
    scale_factor: float
    estimated_accuracy_cm: Optional[float]
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class MeasurementCreate(BaseModel):
    measurement_type: str = Field(..., description="Type: distance, area, volume, angle, trajectory")
    name: str
    description: Optional[str] = None
    coordinates: List[Dict[str, float]]  # List of {x, y, z} points
    created_by: str


class MeasurementResponse(BaseModel):
    id: int
    project_id: int
    measurement_type: str
    name: str
    description: Optional[str]
    coordinates: List[Dict[str, float]]
    value: Optional[float]
    unit: Optional[str]
    uncertainty: Optional[float]
    created_by: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class ReportRequest(BaseModel):
    include_images: bool = True
    include_3d_views: bool = True
    include_measurements: bool = True
    include_satellite_view: bool = True
    include_audit_trail: bool = True
    examiner_signature: Optional[str] = None
    additional_notes: Optional[str] = None


class AuditLogResponse(BaseModel):
    id: int
    event_type: str
    event_description: Optional[str]
    user_name: Optional[str]
    affected_resource: Optional[str]
    timestamp: datetime
    
    class Config:
        from_attributes = True
