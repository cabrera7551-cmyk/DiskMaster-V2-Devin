"""
Folder Scanner for DiskMaster V2
Handles folder scanning, size calculation, and file indexing
"""

from pathlib import Path
from typing import List, Dict, Optional, Callable, Set
from dataclasses import dataclass
from enum import Enum
import os
import threading

from utils.formatters import SizeFormatter
from core.security import SecurityValidator


class ScanPriority(Enum):
    """Scan priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3


@dataclass
class FileInfo:
    """Information about a file"""
    path: Path
    name: str
    size: int
    extension: str
    is_hidden: bool
    is_system: bool
    modified_time: float
    created_time: float
    
    def get_formatted_size(self) -> str:
        """Get formatted file size"""
        return SizeFormatter.format_size(self.size)


@dataclass
class FolderInfo:
    """Information about a folder"""
    path: Path
    name: str
    total_size: int
    file_count: int
    folder_count: int
    is_hidden: bool
    is_system: bool
    contains_system_files: bool
    modified_time: float
    created_time: float
    
    def get_formatted_size(self) -> str:
        """Get formatted folder size"""
        return SizeFormatter.format_size(self.total_size)
    
    def get_file_count_str(self) -> str:
        """Get formatted file count"""
        return f"{self.file_count:,} archivos"
    
    def get_folder_count_str(self) -> str:
        """Get formatted folder count"""
        return f"{self.folder_count:,} carpetas"


class FolderScanner:
    """
    Scans folders and calculates sizes with progress tracking
    """
    
    def __init__(self):
        """Initialize folder scanner"""
        self.security_validator = SecurityValidator()
        self._is_scanning = False
        self._should_stop = False
        self._scan_thread: Optional[threading.Thread] = None
    
    def scan_folder(
        self,
        folder_path: Path,
        progress_callback: Optional[Callable] = None,
        include_hidden: bool = False,
        max_depth: int = 10
    ) -> FolderInfo:
        """
        Scan a folder and calculate its size
        
        Args:
            folder_path: Path to the folder to scan
            progress_callback: Optional callback for progress updates
            include_hidden: Whether to include hidden files
            max_depth: Maximum recursion depth
            
        Returns:
            FolderInfo with scan results
        """
        self._is_scanning = True
        self._should_stop = False
        
        try:
            folder_path = Path(folder_path).resolve()
            
            if not folder_path.exists() or not folder_path.is_dir():
                raise ValueError(f"Invalid folder path: {folder_path}")
            
            # Security check
            validation = self.security_validator.validate_path(folder_path)
            if not validation.is_safe:
                raise PermissionError(f"Unsafe folder: {validation.reason}")
            
            # Initialize counters
            total_size = 0
            file_count = 0
            folder_count = 0
            contains_system_files = False
            
            # Get folder metadata
            stat = folder_path.stat()
            modified_time = stat.st_mtime
            created_time = stat.st_ctime
            is_hidden = self._is_hidden(folder_path)
            is_system = validation.security_level.value in ['danger', 'forbidden']
            
            # Scan folder contents
            items = list(folder_path.iterdir())
            total_items = len(items)
            
            for i, item in enumerate(items):
                if self._should_stop:
                    break
                
                try:
                    if item.is_file():
                        # Skip hidden files if not including them
                        if not include_hidden and self._is_hidden(item):
                            continue
                        
                        # Skip system files
                        if self.security_validator.is_system_file(item):
                            contains_system_files = True
                            continue
                        
                        file_size = item.stat().st_size
                        total_size += file_size
                        file_count += 1
                        
                    elif item.is_dir():
                        # Skip hidden directories if not including them
                        if not include_hidden and self._is_hidden(item):
                            continue
                        
                        # Recursively scan subfolder
                        subfolder_info = self.scan_folder(
                            item,
                            progress_callback=None,  # Don't use callback for recursion
                            include_hidden=include_hidden,
                            max_depth=max_depth - 1 if max_depth > 0 else 0
                        )
                        
                        total_size += subfolder_info.total_size
                        file_count += subfolder_info.file_count
                        folder_count += subfolder_info.folder_count + 1
                        contains_system_files |= subfolder_info.contains_system_files
                    
                    # Update progress
                    if progress_callback and total_items > 0:
                        progress = int((i + 1) / total_items * 100)
                        progress_callback(progress, f"Scanning: {item.name}")
                    
                except (PermissionError, OSError) as e:
                    # Skip items we can't access
                    print(f"Skipping {item}: {e}")
                    continue
            
            # Create folder info
            folder_info = FolderInfo(
                path=folder_path,
                name=folder_path.name,
                total_size=total_size,
                file_count=file_count,
                folder_count=folder_count,
                is_hidden=is_hidden,
                is_system=is_system,
                contains_system_files=contains_system_files,
                modified_time=modified_time,
                created_time=created_time
            )
            
            self._is_scanning = False
            return folder_info
            
        except Exception as e:
            self._is_scanning = False
            raise e
    
    def scan_folder_fast(
        self,
        folder_path: Path,
        progress_callback: Optional[Callable] = None
    ) -> FolderInfo:
        """
        Fast folder scan using directory size estimation
        
        Args:
            folder_path: Path to the folder to scan
            progress_callback: Optional callback for progress updates
            
        Returns:
            FolderInfo with estimated results
        """
        self._is_scanning = True
        self._should_stop = False
        
        try:
            folder_path = Path(folder_path).resolve()
            
            if not folder_path.exists() or not folder_path.is_dir():
                raise ValueError(f"Invalid folder path: {folder_path}")
            
            # Security check
            validation = self.security_validator.validate_path(folder_path)
            if not validation.is_safe:
                raise PermissionError(f"Unsafe folder: {validation.reason}")
            
            # Get folder metadata
            stat = folder_path.stat()
            modified_time = stat.st_mtime
            created_time = stat.st_ctime
            is_hidden = self._is_hidden(folder_path)
            is_system = validation.security_level.value in ['danger', 'forbidden']
            
            # Count items and estimate size
            total_size = 0
            file_count = 0
            folder_count = 0
            
            try:
                for item in folder_path.iterdir():
                    if self._should_stop:
                        break
                    
                    try:
                        if item.is_file():
                            if not self._is_hidden(item):
                                file_size = item.stat().st_size
                                total_size += file_size
                                file_count += 1
                        elif item.is_dir():
                            if not self._is_hidden(item):
                                folder_count += 1
                                # Add estimated size for subfolder
                                # In a real implementation, you might use
                                # cached data or quick estimation
                                pass
                        
                    except (PermissionError, OSError):
                        continue
                    
            except (PermissionError, OSError):
                pass
            
            # Create folder info with estimated data
            folder_info = FolderInfo(
                path=folder_path,
                name=folder_path.name,
                total_size=total_size,
                file_count=file_count,
                folder_count=folder_count,
                is_hidden=is_hidden,
                is_system=is_system,
                contains_system_files=False,
                modified_time=modified_time,
                created_time=created_time
            )
            
            self._is_scanning = False
            return folder_info
            
        except Exception as e:
            self._is_scanning = False
            raise e
    
    def get_folder_contents(
        self,
        folder_path: Path,
        include_hidden: bool = False,
        sort_by: str = "name"
    ) -> List[Path]:
        """
        Get contents of a folder without calculating sizes
        
        Args:
            folder_path: Path to the folder
            include_hidden: Whether to include hidden items
            sort_by: Sort method ('name', 'size', 'date')
            
        Returns:
            List of folder contents
        """
        try:
            folder_path = Path(folder_path).resolve()
            
            if not folder_path.exists() or not folder_path.is_dir():
                return []
            
            # Security check
            validation = self.security_validator.validate_path(folder_path)
            if not validation.is_safe:
                return []
            
            # Get folder contents
            items = []
            
            for item in folder_path.iterdir():
                try:
                    # Skip hidden items if not including them
                    if not include_hidden and self._is_hidden(item):
                        continue
                    
                    # Skip system files
                    if item.is_file() and self.security_validator.is_system_file(item):
                        continue
                    
                    items.append(item)
                    
                except (PermissionError, OSError):
                    continue
            
            # Sort items
            if sort_by == "name":
                items.sort(key=lambda x: x.name.lower())
            elif sort_by == "size":
                items.sort(key=lambda x: x.stat().st_size if x.is_file() else 0, reverse=True)
            elif sort_by == "date":
                items.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            return items
            
        except Exception:
            return []
    
    def get_folder_size_quick(self, folder_path: Path) -> int:
        """
        Get quick folder size using OS-specific methods
        
        Args:
            folder_path: Path to the folder
            
        Returns:
            Estimated folder size in bytes
        """
        try:
            folder_path = Path(folder_path).resolve()
            
            if not folder_path.exists() or not folder_path.is_dir():
                return 0
            
            # On Windows, we could use WMI or other fast methods
            # For now, use a simple recursive sum
            total_size = 0
            
            for item in folder_path.rglob('*'):
                try:
                    if item.is_file():
                        total_size += item.stat().st_size
                except (PermissionError, OSError):
                    continue
            
            return total_size
            
        except Exception:
            return 0
    
    def stop_scan(self):
        """Stop the current scan operation"""
        self._should_stop = True
        self._is_scanning = False
    
    def is_scanning(self) -> bool:
        """Check if a scan is in progress"""
        return self._is_scanning
    
    def _is_hidden(self, path: Path) -> bool:
        """
        Check if a file or folder is hidden
        
        Args:
            path: Path to check
            
        Returns:
            True if hidden, False otherwise
        """
        try:
            # On Windows, check the hidden attribute
            if os.name == 'nt':
                import win32api
                import win32con
                
                attribute = win32api.GetFileAttributes(str(path))
                return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
            else:
                # On Unix-like systems, check if name starts with '.'
                return path.name.startswith('.')
                
        except Exception:
            return False
    
    def calculate_folder_sizes(
        self,
        folder_path: Path,
        progress_callback: Optional[Callable] = None
    ) -> Dict[str, int]:
        """
        Calculate sizes of immediate subfolders
        
        Args:
            folder_path: Path to the parent folder
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary mapping folder names to sizes
        """
        folder_sizes = {}
        
        try:
            folder_path = Path(folder_path).resolve()
            
            if not folder_path.exists() or not folder_path.is_dir():
                return folder_sizes
            
            # Security check
            validation = self.security_validator.validate_path(folder_path)
            if not validation.is_safe:
                return folder_sizes
            
            # Get immediate subfolders
            subfolders = [f for f in folder_path.iterdir() if f.is_dir()]
            total_subfolders = len(subfolders)
            
            for i, subfolder in enumerate(subfolders):
                if self._should_stop:
                    break
                
                try:
                    # Skip hidden folders
                    if self._is_hidden(subfolder):
                        continue
                    
                    # Skip system folders
                    validation = self.security_validator.validate_path(subfolder)
                    if not validation.is_safe:
                        continue
                    
                    # Calculate folder size
                    folder_size = self.get_folder_size_quick(subfolder)
                    folder_sizes[subfolder.name] = folder_size
                    
                    # Update progress
                    if progress_callback and total_subfolders > 0:
                        progress = int((i + 1) / total_subfolders * 100)
                        progress_callback(progress, f"Calculating: {subfolder.name}")
                    
                except (PermissionError, OSError):
                    continue
            
            return folder_sizes
            
        except Exception:
            return folder_sizes