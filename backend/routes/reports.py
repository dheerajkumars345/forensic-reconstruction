"""
Reports API Routes
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import logging

from database import get_db
from models import Project, Image, Reconstruction, Measurement, AuditLog, ReportRequest, AuditLogResponse
from services.report_generator import ReportGenerator
from services.chain_of_custody import ChainOfCustodyService
from config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/projects/{project_id}/report/generate")
async def generate_report(
    project_id: int,
    request: ReportRequest,
    db: AsyncSession = Depends(get_db)
):
    """Generate forensic PDF report"""
    try:
        # Get project
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get images - only include suitable or verified images
        images_result = await db.execute(select(Image).where(Image.project_id == project_id))
        all_images = images_result.scalars().all()
        
        # Filter: only include images that are suitable OR manually verified
        images = [
            img for img in all_images
            if img.is_suitable != False or img.is_verified == True
        ]
        rejected_count = len(all_images) - len(images)
        
        if len(images) == 0:
            raise HTTPException(
                status_code=400, 
                detail=f"Cannot generate report: No suitable images found. {rejected_count} image(s) were rejected as irrelevant. Please upload valid crime scene photographs or manually verify existing images."
            )
        
        # Get reconstruction
        recon_result = await db.execute(
            select(Reconstruction)
            .where(Reconstruction.project_id == project_id)
            .order_by(Reconstruction.completed_at.desc())
            .limit(1)
        )
        reconstruction = recon_result.scalars().first()
        
        # Get measurements
        meas_result = await db.execute(select(Measurement).where(Measurement.project_id == project_id))
        measurements = meas_result.scalars().all()
        
        # Get audit logs
        logs_result = await db.execute(
            select(AuditLog)
            .where(AuditLog.project_id == project_id)
            .order_by(AuditLog.timestamp)
        )
        audit_logs = logs_result.scalars().all()
        
        # Prepare data
        project_data = {
            "case_number": project.case_number,
            "case_title": project.case_title,
            "description": project.description,
            "location": project.location,
            "incident_date": project.incident_date,
            "examiner_name": project.examiner_name,
            "examiner_id": project.examiner_id,
            "laboratory": project.laboratory
        }
        
        images_data = [
            {
                "filename": img.filename,
                "file_hash": img.file_hash,
                "date_taken": img.date_taken,
                "gps_latitude": img.gps_latitude,
                "gps_longitude": img.gps_longitude,
                "quality_score": img.quality_score,
                "forensic_score": img.forensic_score,
                "is_verified": img.is_verified
            }
            for img in images
        ]
        
        # Add note about rejected images if any
        if rejected_count > 0:
            if not request.additional_notes:
                request.additional_notes = ""
            request.additional_notes += f"\n\nNote: {rejected_count} image(s) were excluded from this report due to failing forensic validation."
        
        reconstruction_data = None
        if reconstruction:
            reconstruction_data = {
                "num_images_used": reconstruction.num_images_used,
                "num_points": reconstruction.num_points,
                "num_faces": reconstruction.num_faces,
                "scale_factor": reconstruction.scale_factor,
                "estimated_accuracy_cm": reconstruction.estimated_accuracy_cm,
                "quality": reconstruction.quality
            }
        
        measurements_data = [
            {
                "measurement_type": m.measurement_type,
                "name": m.name,
                "value": m.value,
                "unit": m.unit,
                "uncertainty": m.uncertainty
            }
            for m in measurements
        ]
        
        audit_logs_data = [
            {
                "timestamp": log.timestamp,
                "event_type": log.event_type,
                "user_name": log.user_name,
                "affected_resource": log.affected_resource
            }
            for log in audit_logs
        ]
        
        # Generate report
        report_dir = settings.REPORTS_DIR / str(project_id)
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"report_{project.case_number}.pdf"
        
        generator = ReportGenerator()
        generator.generate_forensic_report(
            output_path=report_path,
            project_data=project_data,
            images_data=images_data,
            reconstruction_data=reconstruction_data,
            measurements_data=measurements_data,
            audit_logs=audit_logs_data,
            include_images=request.include_images,
            include_3d_views=request.include_3d_views,
            include_measurements=request.include_measurements,
            include_audit_trail=request.include_audit_trail,
            examiner_signature=request.examiner_signature,
            additional_notes=request.additional_notes
        )
        
        # Calculate report hash
        report_hash = ChainOfCustodyService.calculate_file_hash(report_path)
        
        # Log report generation
        await ChainOfCustodyService.log_report_generation(
            db=db,
            project_id=project_id,
            report_path=str(report_path),
            report_hash=report_hash
        )
        
        # Return relative URL path for frontend
        relative_path = f"static/reports/{project_id}/report_{project.case_number}.pdf"
        
        return {
            "message": "Report generated successfully",
            "report_path": relative_path,
            "report_hash": report_hash
        }
        
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/report")
async def download_report(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Download PDF report"""
    try:
        result = await db.execute(select(Project).where(Project.id == project_id))
        project = result.scalar_one_or_none()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        report_path = settings.REPORTS_DIR / str(project_id) / f"report_{project.case_number}.pdf"
        
        if not report_path.exists():
            raise HTTPException(status_code=404, detail="Report not found")
        
        return FileResponse(
            path=str(report_path),
            media_type="application/pdf",
            filename=f"forensic_report_{project.case_number}.pdf"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/projects/{project_id}/audit-log", response_model=list)
async def get_audit_log(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """Get chain of custody audit log"""
    try:
        logs = await ChainOfCustodyService.get_audit_trail(db, project_id)
        return [AuditLogResponse.model_validate(log) for log in logs]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
