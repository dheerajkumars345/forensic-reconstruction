"""
Images API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from pathlib import Path
import shutil
import logging

from database import get_db
from models import Image, ImageResponse, Project
from config import settings
from services.image_processor import ImageProcessor
from services.chain_of_custody import ChainOfCustodyService
from services.forensic_validator import ForensicValidator

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
            
            # Run forensic validation
            forensic_result = ForensicValidator.validate_forensic_suitability(
                file_path, metadata
            )
            
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
                quality_score=quality_score,
                # Forensic validation fields
                forensic_score=forensic_result["forensic_score"],
                is_suitable=forensic_result["is_suitable"],
                validation_warnings=[
                    {"severity": w["severity"].value if hasattr(w["severity"], "value") else w["severity"],
                     "message": w["message"],
                     "code": w["code"]}
                    for w in forensic_result["warnings"]
                ],
                validation_flags=forensic_result["flags"]
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


@router.post("/images/{image_id}/verify")
async def verify_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Manually verify an image as forensically suitable"""
    try:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image.is_verified = True
        image.is_suitable = True
        await db.commit()
        
        return {"message": "Image verified successfully", "image_id": image_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/images/{image_id}/verify")
async def unverify_image(
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Remove manual verification from an image"""
    try:
        result = await db.execute(select(Image).where(Image.id == image_id))
        image = result.scalar_one_or_none()
        if not image:
            raise HTTPException(status_code=404, detail="Image not found")
        
        image.is_verified = False
        # Re-calculate suitability based on forensic score
        image.is_suitable = (image.forensic_score or 0) >= 0.3
        await db.commit()
        
        return {"message": "Image verification removed", "image_id": image_id}
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/images/validation-summary")
async def get_validation_summary(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get validation summary for all images in a project"""
    try:
        result = await db.execute(
            select(Image).where(Image.project_id == project_id)
        )
        images = result.scalars().all()
        
        if not images:
            return {
                "total": 0,
                "suitable": 0,
                "with_warnings": 0,
                "rejected": 0,
                "verified": 0,
                "average_forensic_score": 0,
                "warning_summary": {},
                "overall_recommendation": "No images uploaded yet."
            }
        
        suitable_count = sum(1 for img in images if img.is_suitable)
        verified_count = sum(1 for img in images if img.is_verified)
        
        # Count warnings
        warning_count = 0
        warning_codes: Dict[str, int] = {}
        for img in images:
            if img.validation_warnings:
                warning_count += 1 if img.is_suitable else 0
                for w in img.validation_warnings:
                    code = w.get("code", "UNKNOWN")
                    warning_codes[code] = warning_codes.get(code, 0) + 1
        
        rejected_count = sum(1 for img in images if not img.is_suitable)
        scores = [img.forensic_score for img in images if img.forensic_score is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        
        # Generate recommendation
        if rejected_count > suitable_count:
            recommendation = "Most images appear unsuitable for forensic analysis. Please review and upload appropriate crime scene photographs."
        elif avg_score < 0.5:
            recommendation = "Image set has significant quality issues. Consider re-capturing with proper forensic photography techniques."
        elif avg_score < 0.7:
            recommendation = "Image set is usable but has some quality concerns. Review warnings for specific improvements."
        else:
            recommendation = "Image set meets forensic standards. Proceed with analysis."
        
        return {
            "total": len(images),
            "suitable": suitable_count,
            "with_warnings": warning_count,
            "rejected": rejected_count,
            "verified": verified_count,
            "average_forensic_score": round(avg_score, 2),
            "warning_summary": warning_codes,
            "overall_recommendation": recommendation
        }
    except Exception as e:
        logger.error(f"Error getting validation summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))
