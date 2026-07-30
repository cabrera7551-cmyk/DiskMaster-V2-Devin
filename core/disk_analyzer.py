"""
Disk Analyzer for DiskMaster V2
Handles disk detection, analysis, and information retrieval
"""

import psutil
from pathlib import Path
from typing import List, Dict, Optional, Callable
from dataclasses import dataclass
from enum import Enum

from utils.constants import DiskStatus
from utils.formatters import SizeFormatter


class DiskMediaType(Enum):
    """Disk media types"""
    SSD = "SSD"
    HDD = "HDD"
    NVME = "NVMe"
    SATA = "SATA"
    M2 = "M.2"
    USB = "USB"
    UNKNOWN = "Unknown"


@dataclass
class DiskInfo:
    """Information about a disk"""
    letter: str
    name: str
    disk_type: DiskMediaType
    total_space: int
    used_space: int
    free_space: int
    usage_percentage: float
    file_system: str
    is_removable: bool
    is_system: bool
    mount_point: str
    status: DiskStatus
    
    def get_formatted_total(self) -> str:
        """Get formatted total space"""
        return SizeFormatter.format_size(self.total_space)
    
    def get_formatted_used(self) -> str:
        """Get formatted used space"""
        return SizeFormatter.format_size(self.used_space)
    
    def get_formatted_free(self) -> str:
        """Get formatted free space"""
        return SizeFormatter.format_size(self.free_space)
    
    def get_usage_percentage(self) -> float:
        """Get usage percentage"""
        return self.usage_percentage
    
    def get_status(self) -> DiskStatus:
        """Get disk status based on usage"""
        if self.usage_percentage >= 95:
            return DiskStatus.CRITICAL
        elif self.usage_percentage >= 80:
            return DiskStatus.WARNING
        else:
            return DiskStatus.HEALTHY


class DiskAnalyzer:
    """
    Analyzes system disks and provides detailed information
    """
    
    SYSTEM_DRIVES = ['C']
    FORBIDDEN_FILESYSTEMS = ['CDFS', 'UDF']  # Optical drives
    
    def __init__(self):
        """Initialize disk analyzer"""
        self._disks: List[DiskInfo] = []
        self._is_analyzing = False
    
    def detect_disks(self, progress_callback: Optional[Callable] = None) -> List[DiskInfo]:
        """
        Detect all available disks on the system
        
        Args:
            progress_callback: Optional callback for progress updates
            
        Returns:
            List of detected disk information
        """
        self._is_analyzing = True
        self._disks = []
        
        try:
            if progress_callback:
                progress_callback(10, "Detecting disks...")
            
            # Get all disk partitions
            partitions = psutil.disk_partitions(all=True)
            
            if progress_callback:
                progress_callback(30, "Analyzing partitions...")
            
            # Filter and analyze each partition
            total_partitions = len(partitions)
            for i, partition in enumerate(partitions):
                try:
                    # Skip optical drives and network drives
                    if partition.fstype in self.FORBIDDEN_FILESYSTEMS:
                        continue
                    
                    # Skip if mount point doesn't exist
                    if not Path(partition.mountpoint).exists():
                        continue
                    
                    # Get disk usage
                    usage = psutil.disk_usage(partition.mountpoint)
                    
                    # Determine disk type
                    disk_type = self._detect_disk_type(partition)
                    
                    # Determine if it's a system drive
                    is_system = partition.mountpoint.startswith('C:')
                    
                    # Determine if removable
                    is_removable = self._is_removable_drive(partition)
                    
                    # Create disk info
                    disk_info = DiskInfo(
                        letter=partition.mountpoint,
                        name=self._get_volume_name(partition.mountpoint),
                        disk_type=disk_type,
                        total_space=usage.total,
                        used_space=usage.used,
                        free_space=usage.free,
                        usage_percentage=(usage.used / usage.total) * 100 if usage.total > 0 else 0,
                        file_system=partition.fstype,
                        is_removable=is_removable,
                        is_system=is_system,
                        mount_point=partition.mountpoint,
                        status=DiskStatus.HEALTHY  # Will be updated by get_status()
                    )
                    
                    # Update status based on usage
                    disk_info.status = disk_info.get_status()
                    
                    self._disks.append(disk_info)
                    
                    # Update progress
                    if progress_callback:
                        progress_percent = 30 + int((i + 1) / total_partitions * 60)
                        progress_callback(progress_percent, f"Analyzing {partition.mountpoint}...")
                    
                except (PermissionError, OSError) as e:
                    # Skip drives we can't access
                    print(f"Skipping {partition.mountpoint}: {e}")
                    continue
            
            if progress_callback:
                progress_callback(100, "Disk analysis complete")
            
        except Exception as e:
            print(f"Error during disk detection: {e}")
            if progress_callback:
                progress_callback(0, f"Error: {str(e)}")
        
        self._is_analyzing = False
        return self._disks
    
    def _detect_disk_type(self, partition) -> DiskMediaType:
        """
        Detect disk type based on various indicators
        
        Args:
            partition: psutil partition information
            
        Returns:
            Detected disk media type
        """
        try:
            # Check if it's a removable drive (likely USB)
            if self._is_removable_drive(partition):
                return DiskMediaType.USB
            
            # Try to get physical disk information
            mount_point = partition.mountpoint
            
            # This is a simplified detection - in a real implementation,
            # you would use WMI queries on Windows for accurate detection
            # For now, we'll make educated guesses based on size and filesystem
            
            usage = psutil.disk_usage(mount_point)
            total_gb = usage.total / (1024 ** 3)
            
            # NVMe drives are typically high performance and smaller
            # This is a heuristic - real detection requires WMI
            if total_gb < 512 and mount_point.startswith('C:'):
                return DiskMediaType.NVME
            
            # For other drives, default to SSD if it's not obviously mechanical
            # In production, use WMI: win32_diskdrive.mediaType
            return DiskMediaType.SSD  # Default assumption for modern systems
            
        except Exception:
            return DiskMediaType.UNKNOWN
    
    def _is_removable_drive(self, partition) -> bool:
        """
        Check if drive is removable (USB, etc.)
        
        Args:
            partition: psutil partition information
            
        Returns:
            True if removable, False otherwise
        """
        try:
            # This is a simplified check
            # In production, use WMI: win32_logicaldisk.drivetype
            # DriveType 2 = Removable
            mount_point = partition.mountpoint
            
            # Check if it's not a fixed drive letter (A-Z)
            if len(mount_point) < 2 or mount_point[1] != ':':
                return True
            
            # Additional heuristics could be added here
            return False
            
        except Exception:
            return False
    
    def _get_volume_name(self, mount_point: str) -> str:
        """
        Get volume name for the drive
        
        Args:
            mount_point: Drive mount point
            
        Returns:
            Volume name or generic label
        """
        try:
            import win32api
            import win32file
            
            # Get volume name using Windows API
            drive_letter = mount_point[:2]
            volume_name = win32api.GetVolumeInformation(drive_letter + "\\")[0]
            
            if volume_name:
                return volume_name
            
        except Exception:
            pass
        
        # Fallback to generic name
        return f"Drive {mount_point[0]}"
    
    def get_disk_by_letter(self, letter: str) -> Optional[DiskInfo]:
        """
        Get disk information by drive letter
        
        Args:
            letter: Drive letter (e.g., "C:")
            
        Returns:
            DiskInfo if found, None otherwise
        """
        for disk in self._disks:
            if disk.letter == letter:
                return disk
        return None
    
    def get_system_disk(self) -> Optional[DiskInfo]:
        """
        Get the system disk (usually C:)
        
        Returns:
            System disk info if found, None otherwise
        """
        return self.get_disk_by_letter('C:')
    
    def get_removable_disks(self) -> List[DiskInfo]:
        """
        Get all removable disks
        
        Returns:
            List of removable disk information
        """
        return [disk for disk in self._disks if disk.is_removable]
    
    def get_fixed_disks(self) -> List[DiskInfo]:
        """
        Get all fixed (non-removable) disks
        
        Returns:
            List of fixed disk information
        """
        return [disk for disk in self._disks if not disk.is_removable]
    
    def get_total_capacity(self) -> int:
        """
        Get total capacity of all disks
        
        Returns:
            Total capacity in bytes
        """
        return sum(disk.total_space for disk in self._disks)
    
    def get_total_used_space(self) -> int:
        """
        Get total used space across all disks
        
        Returns:
            Total used space in bytes
        """
        return sum(disk.used_space for disk in self._disks)
    
    def get_total_free_space(self) -> int:
        """
        Get total free space across all disks
        
        Returns:
            Total free space in bytes
        """
        return sum(disk.free_space for disk in self._disks)
    
    def get_critical_disks(self) -> List[DiskInfo]:
        """
        Get disks with critical space usage (>= 95%)
        
        Returns:
            List of critical disk information
        """
        return [disk for disk in self._disks if disk.status == DiskStatus.CRITICAL]
    
    def get_warning_disks(self) -> List[DiskInfo]:
        """
        Get disks with warning space usage (>= 80%)
        
        Returns:
            List of warning disk information
        """
        return [disk for disk in self._disks if disk.status == DiskStatus.WARNING]
    
    def is_analyzing(self) -> bool:
        """
        Check if analysis is in progress
        
        Returns:
            True if analyzing, False otherwise
        """
        return self._is_analyzing
    
    def get_disk_count(self) -> int:
        """
        Get total number of detected disks
        
        Returns:
            Number of disks
        """
        return len(self._disks)
    
    def refresh_disk_info(self, letter: str) -> Optional[DiskInfo]:
        """
        Refresh information for a specific disk
        
        Args:
            letter: Drive letter
            
        Returns:
            Updated disk information
        """
        # Re-run detection for this specific disk
        old_disk = self.get_disk_by_letter(letter)
        if old_disk:
            try:
                usage = psutil.disk_usage(letter)
                old_disk.used_space = usage.used
                old_disk.free_space = usage.free
                old_disk.usage_percentage = (usage.used / usage.total) * 100 if usage.total > 0 else 0
                old_disk.status = old_disk.get_status()
                return old_disk
            except Exception:
                pass
        
        return None