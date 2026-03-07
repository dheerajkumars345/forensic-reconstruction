"""
Reconstruction API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from datetime import datetime
import logging
import json
import numpy as np

from database import get_db
from models import Reconstruction, ReconstructionRequest, ReconstructionResponse, Project, Image
from services.photogrammetry import PhotogrammetryService
from services.reconstruction_3d import Reconstruction3DService
from services.image_processor import ImageProcessor
from services.chain_of_custody import ChainOfCustodyService
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


def run_photogrammetry_pipeline(project_id: int, image_paths: list, quality: str) -> dict:
    """
    Run actual photogrammetry pipeline to generate 3D point cloud from images.
    
    This performs:
    1. Feature extraction from each image (SIFT)
    2. Feature matching between image pairs
    3. Triangulation to get 3D points
    4. Point cloud generation with colors from images
    """
    logger.info(f"Starting photogrammetry pipeline for project {project_id} with {len(image_paths)} images")
    
    output_dir = settings.UPLOAD_DIR / str(project_id) / "reconstruction"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Extract features from all images
    keypoints_list = []
    descriptors_list = []
    image_dimensions = []
    
    for img_path in image_paths:
        try:
            kp, desc = ImageProcessor.extract_features(img_path, detector_type="SIFT")
            keypoints_list.append(kp)
            descriptors_list.append(desc)
            
            # Get image dimensions
            import cv2
            img = cv2.imread(str(img_path))
            if img is not None:
                h, w = img.shape[:2]
                image_dimensions.append((w, h))
            else:
                image_dimensions.append((1920, 1080))  # fallback
                
            logger.info(f"Extracted {len(kp)} features from {img_path.name}")
        except Exception as e:
            logger.error(f"Error extracting features from {img_path}: {e}")
            keypoints_list.append([])
            descriptors_list.append(np.array([]))
            image_dimensions.append((1920, 1080))
    
    # Run reconstruction
    try:
        result = PhotogrammetryService.reconstruct_with_opencv(
            image_paths=image_paths,
            output_dir=output_dir,
            keypoints_list=keypoints_list,
            descriptors_list=descriptors_list
        )
        return result
    except Exception as e:
        logger.error(f"Photogrammetry pipeline failed: {e}")
        raise


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
            status="processing",
            started_at=datetime.utcnow()
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
        
        # Run actual photogrammetry pipeline (synchronously for now)
        try:
            image_paths = []
            for img in images:
                # Get actual file path from filepath
                img_path = settings.UPLOAD_DIR / str(project_id) / img.filename
                if img_path.exists():
                    image_paths.append(img_path)
                else:
                    logger.warning(f"Image file not found: {img_path}")
            
            if len(image_paths) < 2:
                raise HTTPException(status_code=400, detail="Not enough valid image files found")
            
            # Run the pipeline
            result = run_photogrammetry_pipeline(project_id, image_paths, request.quality)
            
            # Update reconstruction with results
            reconstruction.point_cloud_path = result.get("point_cloud_path")
            reconstruction.num_points = result.get("num_points", 0)
            reconstruction.status = "completed" if result.get("num_points", 0) > 0 else "failed"
            reconstruction.completed_at = datetime.utcnow()
            
            if result.get("num_points", 0) == 0:
                reconstruction.error_message = "No 3D points could be reconstructed. Images may lack sufficient overlap or features."
            
            await db.commit()
            await db.refresh(reconstruction)
            
        except Exception as e:
            logger.error(f"Reconstruction failed: {e}")
            reconstruction.status = "failed"
            reconstruction.error_message = str(e)
            reconstruction.completed_at = datetime.utcnow()
            await db.commit()
        
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


@router.get("/projects/{project_id}/reconstruction/pointcloud")
async def get_point_cloud_data(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get point cloud data as JSON for 3D visualization.
    Returns positions and colors arrays for Three.js rendering.
    """
    try:
        # Get latest reconstruction
        result = await db.execute(
            select(Reconstruction)
            .where(Reconstruction.project_id == project_id)
            .order_by(Reconstruction.started_at.desc())
            .limit(1)
        )
        reconstruction = result.scalars().first()
        
        if not reconstruction:
            raise HTTPException(status_code=404, detail="No reconstruction found")
        
        if reconstruction.status != "completed":
            raise HTTPException(status_code=400, detail=f"Reconstruction status: {reconstruction.status}")
        
        # Load point cloud from PLY file
        if not reconstruction.point_cloud_path:
            raise HTTPException(status_code=404, detail="No point cloud file available")
        
        point_cloud_path = Path(reconstruction.point_cloud_path)
        if not point_cloud_path.exists():
            raise HTTPException(status_code=404, detail="Point cloud file not found")
        
        # Parse PLY file
        positions = []
        colors = []
        has_colors = False
        
        with open(point_cloud_path, 'r') as f:
            # Skip header
            line = f.readline()
            while line.strip() != "end_header":
                if "property uchar red" in line:
                    has_colors = True
                line = f.readline()
            
            # Read vertices
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 3:
                    positions.extend([float(parts[0]), float(parts[1]), float(parts[2])])
                    if has_colors and len(parts) >= 6:
                        # Normalize colors to 0-1 range
                        colors.extend([
                            int(parts[3]) / 255.0,
                            int(parts[4]) / 255.0,
                            int(parts[5]) / 255.0
                        ])
                    else:
                        # Default gray color
                        colors.extend([0.5, 0.5, 0.5])
        
        # Also get camera positions from images (for visualization)
        images_result = await db.execute(
            select(Image).where(Image.project_id == project_id)
        )
        images = images_result.scalars().all()
        
        camera_positions = []
        for i, img in enumerate(images):
            if img.is_suitable != False or img.is_verified == True:
                # Calculate camera position based on image order
                # This creates a rough arc around the scene
                angle = (i / max(len(images), 1)) * 3.14159 * 2
                radius = 5.0
                camera_positions.append({
                    "filename": img.filename,
                    "filepath": f"static/uploads/{project_id}/{img.filename}",
                    "position": [
                        radius * np.cos(angle),
                        2.0,  # height
                        radius * np.sin(angle)
                    ]
                })
        
        return JSONResponse({
            "positions": positions,
            "colors": colors,
            "num_points": len(positions) // 3,
            "camera_positions": camera_positions,
            "reconstruction_id": reconstruction.id,
            "quality": reconstruction.quality
        })
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading point cloud: {e}")
        raise HTTPException(status_code=500, detail=str(e))
