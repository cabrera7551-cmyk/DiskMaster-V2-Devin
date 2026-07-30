"""
File Manager for DiskMaster V2
Safe file operations with backup and rollback support
"""

import shutil
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

from utils.path_handler import get_path_handler
from core.security import SecurityValidator
from utils.formatters import SizeFormatter


class OperationStatus(Enum):
    """Status of file operations"""
    PENDING = "pending"
    COPYING = "copying"
    VERIFYING = "verifying"
    DELETING = "deleting"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"
    CANCELLED = "cancelled"


@dataclass
class FileOperation:
    """Record of a file operation"""
    operation_id: str
    source_path: str
    destination_path: str
    original_size: int
    operation_type: str  # "move", "copy", "delete"
    status: OperationStatus
    checksum: str
    backup_path: Optional[str]
    timestamp: str
    error_message: Optional[str]
    rollback_possible: bool


class FileManager:
    """
    Manages safe file operations with backup and rollback support
    """
    
    def __init__(self):
        """Initialize file manager"""
        self.path_handler = get_path_handler()
        self.security_validator = SecurityValidator()
        self.operations: List[FileOperation] = []
        self._backup_dir = self.path_handler.get_data_dir() / "backups"
        self._backup_dir.mkdir(parents=True, exist_ok=True)
        self._operation_log = self.path_handler.get_data_dir() / "operations.json"
        self._load_operations()
    
    def _load_operations(self):
        """Load operation history from file"""
        if self._operation_log.exists():
            try:
                with open(self._operation_log, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.operations = [
                        FileOperation(**op) for op in data
                    ]
            except Exception as e:
                print(f"Error loading operations: {e}")
                self.operations = []
    
    def _save_operations(self):
        """Save operation history to file"""
        try:
            data = [op.__dict__ for op in self.operations]
            with open(self._operation_log, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving operations: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate SHA256 checksum of a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            Checksum string
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                # Read file in chunks to handle large files
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            print(f"Error calculating checksum for {file_path}: {e}")
            return ""
    
    def _verify_file_integrity(self, source: Path, destination: Path) -> bool:
        """
        Verify that copied file matches source
        
        Args:
            source: Source file path
            destination: Destination file path
            
        Returns:
            True if files match, False otherwise
        """
        try:
            if not destination.exists():
                return False
            
            # Compare sizes
            if source.stat().st_size != destination.stat().st_size:
                return False
            
            # Compare checksums
            source_checksum = self._calculate_checksum(source)
            dest_checksum = self._calculate_checksum(destination)
            
            return source_checksum == dest_checksum
            
        except Exception as e:
            print(f"Error verifying file integrity: {e}")
            return False
    
    def _create_backup(self, file_path: Path) -> Optional[Path]:
        """
        Create backup of a file before modification
        
        Args:
            file_path: Path to the file to backup
            
        Returns:
            Path to backup file or None if failed
        """
        try:
            if not file_path.exists():
                return None
            
            # Create backup filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"{file_path.stem}_{timestamp}{file_path.suffix}"
            backup_path = self._backup_dir / backup_name
            
            # Copy file to backup location
            shutil.copy2(file_path, backup_path)
            
            return backup_path
            
        except Exception as e:
            print(f"Error creating backup for {file_path}: {e}")
            return None
    
    def _restore_from_backup(self, backup_path: Path, original_path: Path) -> bool:
        """
        Restore file from backup
        
        Args:
            backup_path: Path to backup file
            original_path: Original file location
            
        Returns:
            True if restore successful, False otherwise
        """
        try:
            if not backup_path.exists():
                return False
            
            # Create parent directory if needed
            original_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Restore from backup
            shutil.copy2(backup_path, original_path)
            
            return True
            
        except Exception as e:
            print(f"Error restoring from backup: {e}")
            return False
    
    def can_move_file(self, source: Path, destination: Path) -> tuple[bool, str]:
        """
        Check if a file can be moved safely
        
        Args:
            source: Source file path
            destination: Destination path
            
        Returns:
            Tuple of (can_move, reason)
        """
        # Security check for source
        source_validation = self.security_validator.validate_path(source)
        if not source_validation.is_safe:
            return False, f"Source not safe: {source_validation.reason}"
        
        # Security check for destination
        dest_validation = self.security_validator.validate_path(destination.parent)
        if not dest_validation.is_safe:
            return False, f"Destination not safe: {dest_validation.reason}"
        
        # Check if source exists
        if not source.exists():
            return False, "Source file does not exist"
        
        # Check if destination already exists
        if destination.exists():
            return False, "Destination file already exists"
        
        # Check if destination has enough space
        try:
            source_size = source.stat().st_size
            dest_drive = destination.anchor
            dest_usage = shutil.disk_usage(dest_drive)
            
            if source_size > dest_usage.free:
                return False, f"Not enough space. Required: {SizeFormatter.format_size(source_size)}, Available: {SizeFormatter.format_size(dest_usage.free)}"
        except Exception as e:
            return False, f"Error checking disk space: {str(e)}"
        
        return True, "OK"
    
    def safe_move_file(
        self,
        source: Path,
        destination: Path,
        progress_callback: Optional[Callable] = None
    ) -> FileOperation:
        """
        Safely move a file with backup and verification
        
        Args:
            source: Source file path
            destination: Destination file path
            progress_callback: Optional callback for progress updates
            
        Returns:
            FileOperation record
        """
        operation_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        # Create operation record
        operation = FileOperation(
            operation_id=operation_id,
            source_path=str(source),
            destination_path=str(destination),
            original_size=source.stat().st_size if source.exists() else 0,
            operation_type="move",
            status=OperationStatus.PENDING,
            checksum="",
            backup_path=None,
            timestamp=datetime.now().isoformat(),
            error_message=None,
            rollback_possible=False
        )
        
        try:
            # Safety check
            can_move, reason = self.can_move_file(source, destination)
            if not can_move:
                operation.status = OperationStatus.FAILED
                operation.error_message = reason
                self.operations.append(operation)
                self._save_operations()
                return operation
            
            if progress_callback:
                progress_callback(10, "Creating backup...")
            
            # Create backup
            backup_path = self._create_backup(source)
            operation.backup_path = str(backup_path) if backup_path else None
            operation.rollback_possible = backup_path is not None
            
            # Calculate source checksum
            operation.checksum = self._calculate_checksum(source)
            
            if progress_callback:
                progress_callback(30, "Copying file...")
            
            operation.status = OperationStatus.COPYING
            
            # Copy file to destination
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            
            if progress_callback:
                progress_callback(60, "Verifying integrity...")
            
            operation.status = OperationStatus.VERIFYING
            
            # Verify copy
            if not self._verify_file_integrity(source, destination):
                raise Exception("File verification failed - copied file does not match source")
            
            if progress_callback:
                progress_callback(80, "Deleting source...")
            
            operation.status = OperationStatus.DELETING
            
            # Delete source
            source.unlink()
            
            operation.status = OperationStatus.COMPLETED
            
        except Exception as e:
            operation.status = OperationStatus.FAILED
            operation.error_message = str(e)
            
            # Attempt rollback if copy succeeded but delete failed
            if destination.exists():
                try:
                    destination.unlink()
                except:
                    pass
        
        self.operations.append(operation)
        self._save_operations()
        
        return operation
    
    def rollback_operation(self, operation_id: str) -> bool:
        """
        Rollback a specific operation
        
        Args:
            operation_id: ID of operation to rollback
            
        Returns:
            True if rollback successful, False otherwise
        """
        operation = next((op for op in self.operations if op.operation_id == operation_id), None)
        
        if not operation:
            return False
        
        if not operation.rollback_possible:
            return False
        
        try:
            source = Path(operation.source_path)
            destination = Path(operation.destination_path)
            backup_path = Path(operation.backup_path) if operation.backup_path else None
            
            if backup_path and backup_path.exists():
                # Restore from backup to original location
                if self._restore_from_backup(backup_path, source):
                    # Delete the copy at destination if it exists
                    if destination.exists():
                        destination.unlink()
                    
                    operation.status = OperationStatus.ROLLED_BACK
                    self._save_operations()
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error during rollback: {e}")
            return False
    
    def get_operation_history(self) -> List[FileOperation]:
        """
        Get operation history
        
        Returns:
            List of all operations
        """
        return self.operations.copy()
    
    def get_recent_operations(self, limit: int = 10) -> List[FileOperation]:
        """
        Get recent operations
        
        Args:
            limit: Maximum number of operations to return
            
        Returns:
            List of recent operations
        """
        return self.operations[-limit:] if self.operations else []
    
    def clear_old_operations(self, days: int = 30):
        """
        Clear operations older than specified days
        
        Args:
            days: Number of days to keep
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.operations = [
            op for op in self.operations
            if datetime.fromisoformat(op.timestamp) > cutoff_date
        ]
        
        self._save_operations()
    
    def get_total_moved_size(self) -> int:
        """
        Get total size of successfully moved files
        
        Returns:
            Total size in bytes
        """
        return sum(
            op.original_size for op in self.operations
            if op.status == OperationStatus.COMPLETED and op.operation_type == "move"
        )
    
    def get_operation_statistics(self) -> Dict[str, int]:
        """
        Get statistics about operations
        
        Returns:
            Dictionary with operation statistics
        """
        stats = {
            "total": len(self.operations),
            "completed": len([op for op in self.operations if op.status == OperationStatus.COMPLETED]),
            "failed": len([op for op in self.operations if op.status == OperationStatus.FAILED]),
            "rolled_back": len([op for op in self.operations if op.status == OperationStatus.ROLLED_BACK]),
            "rollback_possible": len([op for op in self.operations if op.rollback_possible])
        }
        
        return stats