"""
Images API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pathlib import Path
import shutil
import logging

from database import get_db
from models import Image, ImageResponse, Project
from config import settings
from services.image_processor import ImageProcessor
from services.chain_of_custody import ChainOfCustodyService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects/{project_id}/images", response_model=List[ImageResponse], status_code=status.HTTP_201_CREATED)
async def upload_images(
    project_id: int,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db)
):
    """Upload images to a project"""
    try:
        # Verify project exists
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Create project upload directory
        project_upload_dir = settings.UPLOAD_DIR / str(project_id)
        project_upload_dir.mkdir(parents=True, exist_ok=True)
        
        uploaded_images = []
        
        for file in files:
            # Save file
            file_path = project_upload_dir / file.filename
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Validate image
            is_valid, message = ImageProcessor.validate_image(file_path)
            if not is_valid:
                file_path.unlink()
                logger.warning(f"Invalid image {file.filename}: {message}")
                continue
            
            # Extract metadata
            metadata = ImageProcessor.extract_exif_data(file_path)
            file_hash = ChainOfCustodyService.calculate_file_hash(file_path)
            quality_score = ImageProcessor.assess_image_quality(file_path)
            
            # Create database record with URL-relative filepath
            relative_filepath = f"static/uploads/{project_id}/{file.filename}"
            image = Image(
                project_id=project_id,
                filename=file.filename,
                filepath=relative_filepath,
                file_size=metadata["file_size"],
                file_hash=file_hash,
                width=metadata.get("width"),
                height=metadata.get("height"),
                format=metadata.get("format"),
                camera_make=metadata.get("camera_make"),
                camera_model=metadata.get("camera_model"),
                date_taken=metadata.get("date_taken"),
                gps_latitude=metadata.get("gps_latitude"),
                gps_longitude=metadata.get("gps_longitude"),
                gps_altitude=metadata.get("gps_altitude"),
                quality_score=quality_score
            )
            
            db.add(image)
            uploaded_images.append(image)
            
            # Log upload
            await ChainOfCustodyService.log_image_upload(
                db=db,
                project_id=project_id,
                image_filename=file.filename,
                file_hash=file_hash
            )
        
        await db.commit()
        
        # Refresh and return
        for img in uploaded_images:
            await db.refresh(img)
        
        return [ImageResponse.model_validate(img) for img in uploaded_images]
        
    except Exception as e:
        logger.error(f"Error uploading images: {e}")
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


def _convert_filepath_to_url(filepath: str, project_id: int) -> str:
    """Convert absolute file path to relative URL for frontend"""
    if filepath.startswith("static/"):
        return filepath
    # Extract filename from absolute path
    import os
    filename = os.path.basename(filepath)
    return f"static/uploads/{project_id}/{filename}"


@router.get("/projects/{project_id}/images", response_model=List[ImageResponse])
async def list_images(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """List all images in a project"""
    try:
        result = await db.execute(
            select(Image).where(Image.project_id == project_id).order_by(Image.uploaded_at)
        )
        images = result.scalars().all()
        responses = []
        for img in images:
            response = ImageResponse.model_validate(img)
            response.filepath = _convert_filepath_to_url(img.filepath, project_id)
            responses.append(response)
        return responses
    except Exception as e:
        logger.error(f"Error listing images: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/images/{image_id}/metadata", response_model=ImageResponse)
async def get_image_metadata(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get detailed image metadata"""
    try:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        return ImageResponse.model_validate(image)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
