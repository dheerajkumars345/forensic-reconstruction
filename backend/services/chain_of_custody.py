"""
Chain of Custody Service
Maintains forensic integrity and audit trail
"""
import hashlib
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from models import AuditLog
from config import settings
import logging

logger = logging.getLogger(__name__)


class ChainOfCustodyService:
    """Manages forensic chain of custody and audit logging"""
    
    @staticmethod
    def calculate_file_hash(file_path: Path, algorithm: str = "sha256") -> str:
        """
        Calculate cryptographic hash of a file
        
        Args:
            file_path: Path to file
            algorithm: Hash algorithm (sha256, sha512, md5)
            
        Returns:
            Hex digest of file hash
        """
        hash_func = hashlib.new(algorithm.lower())
        
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for chunk in iter(lambda: f.read(8192), b''):
                hash_func.update(chunk)
        
        return hash_func.hexdigest()
    
    @staticmethod
    def calculate_string_hash(data: str, algorithm: str = "sha256") -> str:
        """Calculate hash of string data"""
        hash_func = hashlib.new(algorithm.lower())
        hash_func.update(data.encode('utf-8'))
        return hash_func.hexdigest()
    
    @staticmethod
    async def log_event(
        db: AsyncSession,
        project_id: int,
        event_type: str,
        event_description: str,
        user_name: str = "System",
        user_id: Optional[str] = None,
        affected_resource: Optional[str] = None,
        resource_hash_before: Optional[str] = None,
        resource_hash_after: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditLog:
        """
        Log an event in the chain of custody
        
        Args:
            db: Database session
            project_id: Project ID
            event_type: Type of event (upload, process, measure, export, etc.)
            event_description: Human-readable description
            user_name: Name of user performing action
            user_id: ID of user
            affected_resource: Resource affected (file path, ID, etc.)
            resource_hash_before: Hash before modification
            resource_hash_after: Hash after modification
            metadata: Additional metadata
            
        Returns:
            Created audit log entry
        """
        try:
            audit_log = AuditLog(
                project_id=project_id,
                event_type=event_type,
                event_description=event_description,
                user_name=user_name,
                user_id=user_id,
                affected_resource=affected_resource,
                resource_hash_before=resource_hash_before,
                resource_hash_after=resource_hash_after,
                timestamp=datetime.utcnow(),
                extra_metadata=metadata
            )
            
            db.add(audit_log)
            await db.commit()
            await db.refresh(audit_log)
            
            logger.info(f"Audit log created: {event_type} - {event_description}")
            return audit_log
            
        except Exception as e:
            logger.error(f"Failed to create audit log: {e}")
            await db.rollback()
            raise
    
    @staticmethod
    async def get_audit_trail(
        db: AsyncSession,
        project_id: int,
        limit: Optional[int] = None
    ) -> list[AuditLog]:
        """
        Retrieve audit trail for a project
        
        Args:
            db: Database session
            project_id: Project ID
            limit: Maximum number of entries to return
            
        Returns:
            List of audit log entries
        """
        query = select(AuditLog).where(
            AuditLog.project_id == project_id
        ).order_by(AuditLog.timestamp.desc())
        
        if limit:
            query = query.limit(limit)
        
        result = await db.execute(query)
        return result.scalars().all()
    
    @staticmethod
    def verify_file_integrity(file_path: Path, expected_hash: str, algorithm: str = "sha256") -> bool:
        """
        Verify file integrity by comparing hash
        
        Args:
            file_path: Path to file
            expected_hash: Expected hash value
            algorithm: Hash algorithm used
            
        Returns:
            True if hashes match, False otherwise
        """
        try:
            actual_hash = ChainOfCustodyService.calculate_file_hash(file_path, algorithm)
            is_valid = actual_hash == expected_hash
            
            if not is_valid:
                logger.warning(f"File integrity check FAILED for {file_path}")
                logger.warning(f"Expected: {expected_hash}")
                logger.warning(f"Actual: {actual_hash}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error verifying file integrity: {e}")
            return False
    
    @staticmethod
    def generate_custody_receipt(
        file_path: Path,
        case_number: str,
        examiner_name: str,
        additional_info: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a chain of custody receipt for a file
        
        Args:
            file_path: Path to file
            case_number: Case identification
            examiner_name: Name of examiner
            additional_info: Additional information
            
        Returns:
            Custody receipt as dictionary
        """
        file_hash = ChainOfCustodyService.calculate_file_hash(file_path)
        timestamp = datetime.utcnow().isoformat()
        
        receipt = {
            "case_number": case_number,
            "file_name": file_path.name,
            "file_path": str(file_path),
            "file_size_bytes": file_path.stat().st_size,
            "hash_algorithm": settings.HASH_ALGORITHM,
            "file_hash": file_hash,
            "examiner_name": examiner_name,
            "timestamp": timestamp,
            "system_version": settings.APP_VERSION,
        }
        
        if additional_info:
            receipt.update(additional_info)
        
        # Calculate hash of the receipt itself
        receipt_json = json.dumps(receipt, sort_keys=True, indent=2)
        receipt["receipt_hash"] = ChainOfCustodyService.calculate_string_hash(receipt_json)
        
        return receipt
    
    @staticmethod
    async def log_image_upload(
        db: AsyncSession,
        project_id: int,
        image_filename: str,
        file_hash: str,
        user_name: str = "System"
    ):
        """Log image upload event"""
        await ChainOfCustodyService.log_event(
            db=db,
            project_id=project_id,
            event_type="image_upload",
            event_description=f"Image uploaded: {image_filename}",
            user_name=user_name,
            affected_resource=image_filename,
            resource_hash_after=file_hash,
            metadata={"action": "upload", "filename": image_filename}
        )
    
    @staticmethod
    async def log_reconstruction_start(
        db: AsyncSession,
        project_id: int,
        num_images: int,
        user_name: str = "System"
    ):
        """Log 3D reconstruction start"""
        await ChainOfCustodyService.log_event(
            db=db,
            project_id=project_id,
            event_type="reconstruction_start",
            event_description=f"3D reconstruction started with {num_images} images",
            user_name=user_name,
            metadata={"num_images": num_images}
        )
    
    @staticmethod
    async def log_reconstruction_complete(
        db: AsyncSession,
        project_id: int,
        reconstruction_id: int,
        model_hash: str,
        user_name: str = "System"
    ):
        """Log 3D reconstruction completion"""
        await ChainOfCustodyService.log_event(
            db=db,
            project_id=project_id,
            event_type="reconstruction_complete",
            event_description=f"3D reconstruction completed (ID: {reconstruction_id})",
            user_name=user_name,
            affected_resource=f"reconstruction_{reconstruction_id}",
            resource_hash_after=model_hash,
            metadata={"reconstruction_id": reconstruction_id}
        )
    
    @staticmethod
    async def log_report_generation(
        db: AsyncSession,
        project_id: int,
        report_path: str,
        report_hash: str,
        user_name: str = "System"
    ):
        """Log report generation"""
        await ChainOfCustodyService.log_event(
            db=db,
            project_id=project_id,
            event_type="report_generated",
            event_description=f"Forensic report generated",
            user_name=user_name,
            affected_resource=report_path,
            resource_hash_after=report_hash,
            metadata={"report_path": report_path}
        )
