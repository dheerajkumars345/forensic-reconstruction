"""
Projects API Routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
import logging

from database import get_db
from models import Project, ProjectCreate, ProjectResponse, Image
from services.chain_of_custody import ChainOfCustodyService

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new forensic case project
    
    Args:
        project_data: Project creation data
        db: Database session
        
    Returns:
        Created project
    """
    try:
        # Check if case number already exists
        result = await db.execute(
            select(Project).where(Project.case_number == project_data.case_number)
        )
        existing_project = result.scalar_one_or_none()
        
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Project with case number {project_data.case_number} already exists"
            )
        
        # Create new project
        new_project = Project(
            **project_data.model_dump()
        )
        
        db.add(new_project)
        await db.commit()
        await db.refresh(new_project)
        
        # Log project creation
        await ChainOfCustodyService.log_event(
            db=db,
            project_id=new_project.id,
            event_type="project_created",
            event_description=f"Project created: {project_data.case_number}",
            user_name=project_data.examiner_name,
            metadata={
                "case_number": project_data.case_number,
                "case_title": project_data.case_title
            }
        )
        
        # Convert to response
        response = ProjectResponse.model_validate(new_project)
        response.image_count = 0
        
        logger.info(f"Created project: {new_project.case_number} (ID: {new_project.id})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating project: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create project: {str(e)}"
        )


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    List all projects
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        db: Database session
        
    Returns:
        List of projects
    """
    try:
        # Query projects
        result = await db.execute(
            select(Project)
            .order_by(Project.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        projects = result.scalars().all()
        
        # Get image counts for each project
        responses = []
        for project in projects:
            response = ProjectResponse.model_validate(project)
            
            # Count images
            count_result = await db.execute(
                select(func.count(Image.id)).where(Image.project_id == project.id)
            )
            response.image_count = count_result.scalar()
            
            responses.append(response)
        
        return responses
        
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list projects: {str(e)}"
        )


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Get project details by ID
    
    Args:
        project_id: Project ID
        db: Database session
        
    Returns:
        Project details
    """
    try:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Convert to response
        response = ProjectResponse.model_validate(project)
        
        # Count images
        count_result = await db.execute(
            select(func.count(Image.id)).where(Image.project_id == project.id)
        )
        response.image_count = count_result.scalar()
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting project: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get project: {str(e)}"
        )


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    project_data: ProjectCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update project details
    
    Args:
        project_id: Project ID
        project_data: Updated project data
        db: Database session
        
    Returns:
        Updated project
    """
    try:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        # Update fields
        for field, value in project_data.model_dump().items():
            setattr(project, field, value)
        
        await db.commit()
        await db.refresh(project)
        
        # Log update
        await ChainOfCustodyService.log_event(
            db=db,
            project_id=project.id,
            event_type="project_updated",
            event_description=f"Project updated: {project.case_number}",
            user_name=project_data.examiner_name
        )
        
        response = ProjectResponse.model_validate(project)
        
        logger.info(f"Updated project: {project.case_number} (ID: {project.id})")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating project: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update project: {str(e)}"
        )


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    project_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a project and all associated data
    
    Args:
        project_id: Project ID
        db: Database session
    """
    try:
        result = await db.execute(
            select(Project).where(Project.id == project_id)
        )
        project = result.scalar_one_or_none()
        
        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Project {project_id} not found"
            )
        
        case_number = project.case_number
        
        await db.delete(project)
        await db.commit()
        
        logger.info(f"Deleted project: {case_number} (ID: {project_id})")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting project: {e}")
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete project: {str(e)}"
        )
