"""
Measurements API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import logging

from database import get_db
from models import Measurement, MeasurementCreate, MeasurementResponse, Reconstruction
from services.measurement import MeasurementService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects/{project_id}/measurements", response_model=MeasurementResponse)
async def create_measurement(
    project_id: int,
    measurement_data: MeasurementCreate,
    db: AsyncSession = Depends(get_db)
):
    """Create new measurement"""
    try:
        # Get reconstruction for scale factor - required for measurements
        result = await db.execute(
            select(Reconstruction)
            .where(Reconstruction.project_id == project_id)
            .order_by(Reconstruction.completed_at.desc())
        )
        reconstruction = result.scalar_one_or_none()
        
        # Require a valid reconstruction before allowing measurements
        if not reconstruction:
            raise HTTPException(
                status_code=400, 
                detail="Cannot create measurements: No 3D reconstruction found. Please run reconstruction with valid images first."
            )
        
        if reconstruction.status == "failed":
            raise HTTPException(
                status_code=400,
                detail="Cannot create measurements: Reconstruction failed. Please upload suitable crime scene images and try again."
            )
        
        scale_factor = reconstruction.scale_factor if reconstruction else 1.0
        
        # Calculate measurement value based on type
        value = None
        unit = "meters"
        uncertainty = None
        
        if measurement_data.measurement_type == "distance":
            if len(measurement_data.coordinates) >= 2:
                value = MeasurementService.calculate_distance(
                    measurement_data.coordinates[0],
                    measurement_data.coordinates[1],
                    scale_factor
                )
                uncertainty = MeasurementService.estimate_uncertainty(
                    value, len(measurement_data.coordinates)
                )
        
        elif measurement_data.measurement_type == "area":
            value = MeasurementService.calculate_area(
                measurement_data.coordinates, scale_factor
            )
            unit = "square meters"
            uncertainty = MeasurementService.estimate_uncertainty(value, len(measurement_data.coordinates))
        
        # Create measurement
        measurement = Measurement(
            project_id=project_id,
            measurement_type=measurement_data.measurement_type,
            name=measurement_data.name,
            description=measurement_data.description,
            coordinates=measurement_data.coordinates,
            value=value,
            unit=unit,
            uncertainty=uncertainty,
            created_by=measurement_data.created_by
        )
        
        db.add(measurement)
        await db.commit()
        await db.refresh(measurement)
        
        return MeasurementResponse.model_validate(measurement)
        
    except Exception as e:
        logger.error(f"Error creating measurement: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/measurements", response_model=List[MeasurementResponse])
async def list_measurements(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all measurements for a project"""
    try:
        result = await db.execute(
            select(Measurement)
            .where(Measurement.project_id == project_id)
            .order_by(Measurement.created_at)
        )
        measurements = result.scalars().all()
        return [MeasurementResponse.model_validate(m) for m in measurements]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
