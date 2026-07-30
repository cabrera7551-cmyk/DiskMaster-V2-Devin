"""
Backup Manager for DiskMaster V2
Comprehensive backup system for file operations
"""

import shutil
import gzip
import json
from pathlib import Path
from typing import List, Dict, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum
import zipfile

from utils.path_handler import get_path_handler
from utils.formatters import SizeFormatter


class BackupType(Enum):
    """Types of backups"""
    FULL = "full"  # Complete file backup
    INCREMENTAL = "incremental"  # Only changed files
    DIFFERENTIAL = "differential"  # Changes since last full backup


class BackupStatus(Enum):
    """Status of backup operations"""
    PENDING = "pending"
    CREATING = "creating"
    COMPLETED = "completed"
    FAILED = "failed"
    RESTORING = "restoring"
    RESTORED = "restored"
    CORRUPTED = "corrupted"


@dataclass
class BackupRecord:
    """Record of a backup operation"""
    backup_id: str
    backup_type: BackupType
    source_path: str
    backup_path: str
    file_count: int
    total_size: int
    compressed_size: int
    timestamp: str
    status: BackupStatus
    checksum: str
    expiration_date: str
    is_automatic: bool


class BackupManager:
    """
    Manages backup creation, restoration, and maintenance
    """
    
    def __init__(self):
        """Initialize backup manager"""
        self.path_handler = get_path_handler()
        self._backup_root = self.path_handler.get_data_dir() / "backups"
        self._backup_root.mkdir(parents=True, exist_ok=True)
        
        self._full_backup_dir = self._backup_root / "full"
        self._incremental_dir = self._backup_root / "incremental"
        self._metadata_file = self._backup_root / "backup_metadata.json"
        
        self._full_backup_dir.mkdir(exist_ok=True)
        self._incremental_dir.mkdir(exist_ok=True)
        
        self.backups: List[BackupRecord] = []
        self._load_metadata()
    
    def _load_metadata(self):
        """Load backup metadata from file"""
        if self._metadata_file.exists():
            try:
                with open(self._metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.backups = [
                        BackupRecord(**backup) for backup in data
                    ]
            except Exception as e:
                print(f"Error loading backup metadata: {e}")
                self.backups = []
    
    def _save_metadata(self):
        """Save backup metadata to file"""
        try:
            data = [asdict(backup) for backup in self.backups]
            with open(self._metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving backup metadata: {e}")
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """
        Calculate checksum of a file or directory
        
        Args:
            file_path: Path to file or directory
            
        Returns:
            Checksum string
        """
        import hashlib
        
        if file_path.is_file():
            try:
                sha256_hash = hashlib.sha256()
                with open(file_path, "rb") as f:
                    for byte_block in iter(lambda: f.read(4096), b""):
                        sha256_hash.update(byte_block)
                return sha256_hash.hexdigest()
            except Exception:
                return ""
        elif file_path.is_dir():
            # For directories, create checksum from file list and sizes
            try:
                files = list(file_path.rglob('*'))
                file_info = []
                for f in files:
                    if f.is_file():
                        try:
                            file_info.append(f"{f.name}:{f.stat().st_size}")
                        except:
                            pass
                file_info.sort()
                combined = "|".join(file_info)
                sha256_hash = hashlib.sha256()
                sha256_hash.update(combined.encode('utf-8'))
                return sha256_hash.hexdigest()
            except Exception:
                return ""
        
        return ""
    
    def create_backup(
        self,
        source_path: Path,
        backup_type: BackupType = BackupType.FULL,
        progress_callback: Optional[Callable] = None,
        compress: bool = True
    ) -> BackupRecord:
        """
        Create a backup of a file or directory
        
        Args:
            source_path: Path to backup
            backup_type: Type of backup
            progress_callback: Optional callback for progress updates
            compress: Whether to compress the backup
            
        Returns:
            BackupRecord
        """
        backup_id = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        
        if not source_path.exists():
            raise FileNotFoundError(f"Source path does not exist: {source_path}")
        
        # Determine backup directory
        if backup_type == BackupType.FULL:
            backup_dir = self._full_backup_dir
        else:
            backup_dir = self._incremental_dir
        
        # Create backup filename
        if source_path.is_file():
            backup_filename = f"{source_path.stem}_{backup_id}{source_path.suffix}"
        else:
            backup_filename = f"{source_path.name}_{backup_id}"
        
        backup_path = backup_dir / backup_filename
        
        # Create backup record
        record = BackupRecord(
            backup_id=backup_id,
            backup_type=backup_type,
            source_path=str(source_path),
            backup_path=str(backup_path),
            file_count=0,
            total_size=0,
            compressed_size=0,
            timestamp=datetime.now().isoformat(),
            status=BackupStatus.PENDING,
            checksum="",
            expiration_date=(datetime.now() + timedelta(days=30)).isoformat(),
            is_automatic=False
        )
        
        try:
            if progress_callback:
                progress_callback(10, "Calculating size...")
            
            # Calculate source size and file count
            if source_path.is_file():
                record.total_size = source_path.stat().st_size
                record.file_count = 1
            else:
                record.total_size = sum(f.stat().st_size for f in source_path.rglob('*') if f.is_file())
                record.file_count = len([f for f in source_path.rglob('*') if f.is_file()])
            
            if progress_callback:
                progress_callback(30, "Creating backup...")
            
            record.status = BackupStatus.CREATING
            
            if compress:
                if source_path.is_file():
                    # Compress single file
                    self._compress_file(source_path, backup_path)
                else:
                    # Create compressed archive
                    self._create_compressed_archive(source_path, backup_path)
            else:
                if source_path.is_file():
                    shutil.copy2(source_path, backup_path)
                else:
                    shutil.copytree(source_path, backup_path)
            
            if progress_callback:
                progress_callback(80, "Calculating checksum...")
            
            # Calculate checksum
            record.checksum = self._calculate_checksum(backup_path)
            
            # Get compressed size
            if backup_path.exists():
                record.compressed_size = backup_path.stat().st_size
            
            record.status = BackupStatus.COMPLETED
            
        except Exception as e:
            record.status = BackupStatus.FAILED
            print(f"Error creating backup: {e}")
        
        self.backups.append(record)
        self._save_metadata()
        
        return record
    
    def _compress_file(self, source: Path, destination: Path):
        """Compress a single file using gzip"""
        with open(source, 'rb') as f_in:
            with gzip.open(destination, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _create_compressed_archive(self, source: Path, destination: Path):
        """Create a compressed archive of a directory"""
        with zipfile.ZipFile(destination, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in source.rglob('*'):
                if file_path.is_file():
                    arcname = file_path.relative_to(source.parent)
                    zipf.write(file_path, arcname)
    
    def restore_backup(
        self,
        backup_id: str,
        destination_path: Optional[Path] = None,
        progress_callback: Optional[Callable] = None
    ) -> bool:
        """
        Restore a backup
        
        Args:
            backup_id: ID of backup to restore
            destination_path: Where to restore (original if None)
            progress_callback: Optional callback for progress updates
            
        Returns:
            True if successful, False otherwise
        """
        backup_record = next((b for b in self.backups if b.backup_id == backup_id), None)
        
        if not backup_record:
            return False
        
        if backup_record.status != BackupStatus.COMPLETED:
            return False
        
        backup_path = Path(backup_record.backup_path)
        
        if not backup_path.exists():
            backup_record.status = BackupStatus.CORRUPTED
            self._save_metadata()
            return False
        
        if destination_path is None:
            destination_path = Path(backup_record.source_path)
        
        try:
            if progress_callback:
                progress_callback(20, "Preparing restoration...")
            
            backup_record.status = BackupStatus.RESTORING
            
            # Verify backup integrity
            current_checksum = self._calculate_checksum(backup_path)
            if current_checksum != backup_record.checksum:
                backup_record.status = BackupStatus.CORRUPTED
                self._save_metadata()
                return False
            
            if progress_callback:
                progress_callback(50, "Restoring files...")
            
            # Restore based on compression
            if backup_path.suffix == '.gz':
                # Decompress gzip file
                self._decompress_file(backup_path, destination_path)
            elif backup_path.suffix == '.zip':
                # Extract zip archive
                self._extract_archive(backup_path, destination_path.parent)
            else:
                # Direct copy
                if backup_path.is_file():
                    destination_path.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copy2(backup_path, destination_path)
                else:
                    if destination_path.exists():
                        shutil.rmtree(destination_path)
                    shutil.copytree(backup_path, destination_path)
            
            if progress_callback:
                progress_callback(80, "Verifying restoration...")
            
            # Verify restoration
            restored_checksum = self._calculate_checksum(destination_path)
            if restored_checksum != backup_record.checksum:
                # Rollback
                if destination_path.exists():
                    if destination_path.is_file():
                        destination_path.unlink()
                    else:
                        shutil.rmtree(destination_path)
                return False
            
            backup_record.status = BackupStatus.RESTORED
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error restoring backup: {e}")
            backup_record.status = BackupStatus.FAILED
            self._save_metadata()
            return False
    
    def _decompress_file(self, source: Path, destination: Path):
        """Decompress a gzip file"""
        with gzip.open(source, 'rb') as f_in:
            with open(destination, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
    
    def _extract_archive(self, archive_path: Path, destination: Path):
        """Extract a zip archive"""
        with zipfile.ZipFile(archive_path, 'r') as zipf:
            zipf.extractall(destination)
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup
        
        Args:
            backup_id: ID of backup to delete
            
        Returns:
            True if successful, False otherwise
        """
        backup_record = next((b for b in self.backups if b.backup_id == backup_id), None)
        
        if not backup_record:
            return False
        
        try:
            backup_path = Path(backup_record.backup_path)
            if backup_path.exists():
                if backup_path.is_file():
                    backup_path.unlink()
                else:
                    shutil.rmtree(backup_path)
            
            # Remove from records
            self.backups.remove(backup_record)
            self._save_metadata()
            
            return True
            
        except Exception as e:
            print(f"Error deleting backup: {e}")
            return False
    
    def get_backup_by_id(self, backup_id: str) -> Optional[BackupRecord]:
        """
        Get backup record by ID
        
        Args:
            backup_id: Backup ID
            
        Returns:
            BackupRecord or None
        """
        return next((b for b in self.backups if b.backup_id == backup_id), None)
    
    def get_backups_for_source(self, source_path: Path) -> List[BackupRecord]:
        """
        Get all backups for a specific source
        
        Args:
            source_path: Source path
            
        Returns:
            List of backup records
        """
        source_str = str(source_path)
        return [b for b in self.backups if b.source_path == source_str]
    
    def get_expired_backups(self) -> List[BackupRecord]:
        """
        Get backups that have expired
        
        Returns:
            List of expired backup records
        """
        now = datetime.now()
        return [
            b for b in self.backups
            if datetime.fromisoformat(b.expiration_date) < now
        ]
    
    def cleanup_expired_backups(self) -> int:
        """
        Delete expired backups
        
        Returns:
            Number of backups deleted
        """
        expired = self.get_expired_backups()
        deleted_count = 0
        
        for backup in expired:
            if self.delete_backup(backup.backup_id):
                deleted_count += 1
        
        return deleted_count
    
    def get_total_backup_size(self) -> int:
        """
        Get total size of all backups
        
        Returns:
            Total size in bytes
        """
        return sum(b.compressed_size for b in self.backups)
    
    def get_backup_statistics(self) -> Dict[str, any]:
        """
        Get backup statistics
        
        Returns:
            Dictionary with statistics
        """
        return {
            "total_backups": len(self.backups),
            "full_backups": len([b for b in self.backups if b.backup_type == BackupType.FULL]),
            "incremental_backups": len([b for b in self.backups if b.backup_type == BackupType.INCREMENTAL]),
            "completed_backups": len([b for b in self.backups if b.status == BackupStatus.COMPLETED]),
            "failed_backups": len([b for b in self.backups if b.status == BackupStatus.FAILED]),
            "total_size": sum(b.compressed_size for b in self.backups),
            "total_files": sum(b.file_count for b in self.backups),
            "expired_backups": len(self.get_expired_backups())
        }