"""
Reconstruction API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import logging

from database import get_db
from models import Reconstruction, ReconstructionRequest, ReconstructionResponse, Project, Image
from services.photogrammetry import PhotogrammetryService
from services.reconstruction_3d import Reconstruction3DService
from services.image_processor import ImageProcessor
from services.chain_of_custody import ChainOfCustodyService

logger = logging.getLogger(__name__)
router = APIRouter()


async def run_reconstruction_task(project_id: int, quality: str):
    """Background task for running reconstruction"""
    # This would run the actual reconstruction process
    logger.info(f"Starting reconstruction for project {project_id} with quality {quality}")
    # Implementation would go here


@router.post("/projects/{project_id}/reconstruct", response_model=ReconstructionResponse)
async def start_reconstruction(
    project_id: int,
    request: ReconstructionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db)
):
    """Start 3D reconstruction process"""
    try:
        # Verify project exists
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get ALL images first
        all_images_result = await db.execute(
            select(Image).where(Image.project_id == project_id)
        )
        all_images = all_images_result.scalars().all()
        
        # Filter images: REJECT if is_suitable=False AND not manually verified
        # Accept if: is_verified=True OR is_suitable is not False (None or True)
        images = []
        rejected_images = []
        
        for img in all_images:
            # If explicitly marked as unsuitable and NOT manually verified → reject
            if img.is_suitable == False and img.is_verified != True:
                rejected_images.append(img)
                logger.info(f"Rejected image: {img.filename} (score={img.forensic_score}, suitable={img.is_suitable}, verified={img.is_verified})")
            else:
                images.append(img)
        
        rejected_count = len(rejected_images)
        logger.info(f"Reconstruction: {len(all_images)} total, {len(images)} usable, {rejected_count} rejected")
        
        if len(images) < 2:
            if rejected_count > 0:
                rejected_names = ", ".join([img.filename for img in rejected_images[:5]])
                raise HTTPException(
                    status_code=400, 
                    detail=f"Need at least 2 suitable images for reconstruction. {rejected_count} image(s) were rejected as irrelevant: {rejected_names}. Verify them manually in Evidence Images tab or upload appropriate crime scene photographs."
                )
            raise HTTPException(status_code=400, detail="Need at least 2 images for reconstruction")
        
        # Create reconstruction record
        reconstruction = Reconstruction(
            project_id=project_id,
            num_images_used=len(images),
            quality=request.quality,
            status="processing"
        )
        
        db.add(reconstruction)
        await db.commit()
        await db.refresh(reconstruction)
        
        # Log reconstruction start (include warning about skipped images)
        metadata = {"rejected_images": rejected_count} if rejected_count > 0 else None
        await ChainOfCustodyService.log_reconstruction_start(
            db=db,
            project_id=project_id,
            num_images=len(images),
            metadata=metadata
        )
        
        # Start background task
        background_tasks.add_task(run_reconstruction_task, project_id, request.quality)
        
        return ReconstructionResponse.model_validate(reconstruction)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting reconstruction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/reconstruction/status", response_model=ReconstructionResponse)
async def get_reconstruction_status(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get reconstruction status"""
    try:
        result = await db.execute(
            select(Reconstruction)
            .where(Reconstruction.project_id == project_id)
            .order_by(Reconstruction.started_at.desc())
            .limit(1)
        )
        reconstruction = result.scalars().first()
        
        if not reconstruction:
            raise HTTPException(status_code=404, detail="No reconstruction found")
        
        return ReconstructionResponse.model_validate(reconstruction)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
