"""
Security Module for DiskMaster V2
Validates paths and operations to ensure system safety
"""

from pathlib import Path
from typing import List, Optional, Set
from dataclasses import dataclass
from enum import Enum

from utils.constants import ForbiddenFolders, UserFolders
from utils.path_handler import get_path_handler


class SecurityLevel(Enum):
    """Security levels for operations"""
    SAFE = "safe"  # Personal files only
    CAUTION = "caution"  # May affect user settings
    DANGER = "danger"  # System files
    FORBIDDEN = "forbidden"  # Never allowed


@dataclass
class SecurityValidation:
    """Result of security validation"""
    is_safe: bool
    security_level: SecurityLevel
    reason: str
    can_read: bool
    can_write: bool
    can_delete: bool


class SecurityValidator:
    """
    Validates file operations to ensure system safety
    """
    
    # System-critical paths that should never be accessed
    CRITICAL_PATHS = [
        'Windows',
        'Program Files',
        'Program Files (x86)',
        'ProgramData',
        'System Volume Information',
        'Recovery',
        'Boot',
        'EFI',
        '$Recycle.Bin',
        '$SysReset',
        'Config.Msi',
        'MSOCache',
        'PerfLogs',
    ]
    
    # Extensions that are potentially dangerous to manipulate
    DANGEROUS_EXTENSIONS = {
        '.sys', '.dll', '.exe', '.bat', '.cmd', '.ps1',
        '.reg', '.inf', '.cab', '.msi', '.msp'
    }
    
    def __init__(self):
        """Initialize security validator"""
        self.path_handler = get_path_handler()
        self.user_profile = self.path_handler.get_user_profile_dir()
        self._safe_folders: Set[str] = set()
        self._initialize_safe_folders()
    
    def _initialize_safe_folders(self):
        """Initialize list of safe user folders"""
        # Standard user folders
        for folder in UserFolders.STANDARD_FOLDERS:
            self._safe_folders.add(folder.lower())
        
        # Add alternative names for different languages
        for standard, alternatives in UserFolders.ALTERNATIVE_NAMES.items():
            for alt in alternatives:
                self._safe_folders.add(alt.lower())
    
    def validate_path(self, path: Path) -> SecurityValidation:
        """
        Validate a path for safety
        
        Args:
            path: Path to validate
            
        Returns:
            SecurityValidation result
        """
        try:
            path = Path(path).resolve()
            
            # Check if path is within user profile
            try:
                path.relative_to(self.user_profile)
                is_in_user_profile = True
            except ValueError:
                is_in_user_profile = False
            
            # Check for critical system folders
            for part in path.parts:
                if part.lower() in [p.lower() for p in self.CRITICAL_PATHS]:
                    return SecurityValidation(
                        is_safe=False,
                        security_level=SecurityLevel.FORBIDDEN,
                        reason=f"Path contains system folder: {part}",
                        can_read=False,
                        can_write=False,
                        can_delete=False
                    )
            
            # Check if it's a safe user folder
            if is_in_user_profile:
                # Check if it's directly in a safe folder
                relative_parts = path.relative_to(self.user_profile).parts
                if relative_parts and relative_parts[0].lower() in self._safe_folders:
                    return SecurityValidation(
                        is_safe=True,
                        security_level=SecurityLevel.SAFE,
                        reason="Path is in safe user folder",
                        can_read=True,
                        can_write=True,
                        can_delete=True
                    )
                
                # Check if it's deeper in a safe folder
                for part in relative_parts:
                    if part.lower() in self._safe_folders:
                        return SecurityValidation(
                            is_safe=True,
                            security_level=SecurityLevel.SAFE,
                            reason="Path is in safe user folder hierarchy",
                            can_read=True,
                            can_write=True,
                            can_delete=True
                        )
            
            # If not in user profile, check if it's on a different drive
            if path.anchor != self.user_profile.anchor:
                # Different drive - could be external or data drive
                # Allow with caution
                return SecurityValidation(
                    is_safe=True,
                    security_level=SecurityLevel.CAUTION,
                    reason="Path is on different drive",
                    can_read=True,
                    can_write=True,
                    can_delete=True
                )
            
            # Not in user profile but on same drive - use caution
            return SecurityValidation(
                is_safe=True,
                security_level=SecurityLevel.CAUTION,
                reason="Path is outside user profile",
                can_read=True,
                can_write=True,
                can_delete=True
            )
            
        except Exception as e:
            return SecurityValidation(
                is_safe=False,
                security_level=SecurityLevel.FORBIDDEN,
                reason=f"Error validating path: {str(e)}",
                can_read=False,
                can_write=False,
                can_delete=False
            )
    
    def validate_file_operation(self, file_path: Path, operation: str) -> SecurityValidation:
        """
        Validate a file operation
        
        Args:
            file_path: Path to the file
            operation: Operation type (read, write, delete, move)
            
        Returns:
            SecurityValidation result
        """
        # First validate the path
        validation = self.validate_path(file_path)
        
        if not validation.is_safe:
            return validation
        
        # Additional checks for specific operations
        if operation.lower() in ['delete', 'move']:
            # Check file extension
            if file_path.suffix.lower() in self.DANGEROUS_EXTENSIONS:
                return SecurityValidation(
                    is_safe=False,
                    security_level=SecurityLevel.DANGER,
                    reason=f"Dangerous file extension: {file_path.suffix}",
                    can_read=validation.can_read,
                    can_write=False,
                    can_delete=False
                )
        
        return validation
    
    def is_safe_folder(self, folder_name: str) -> bool:
        """
        Check if a folder name is considered safe
        
        Args:
            folder_name: Name of the folder
            
        Returns:
            True if safe, False otherwise
        """
        return folder_name.lower() in self._safe_folders
    
    def get_safe_user_folders(self) -> List[Path]:
        """
        Get list of safe user folder paths
        
        Returns:
            List of safe folder paths
        """
        safe_folders = []
        
        for folder_name in UserFolders.STANDARD_FOLDERS:
            folder_path = self.user_profile / folder_name
            if folder_path.exists():
                safe_folders.append(folder_path)
        
        # Also check alternative names
        for standard, alternatives in UserFolders.ALTERNATIVE_NAMES.items():
            for alt in alternatives:
                folder_path = self.user_profile / alt
                if folder_path.exists() and folder_path not in safe_folders:
                    safe_folders.append(folder_path)
        
        return safe_folders
    
    def filter_safe_paths(self, paths: List[Path]) -> List[Path]:
        """
        Filter a list of paths to only include safe ones
        
        Args:
            paths: List of paths to filter
            
        Returns:
            List of safe paths
        """
        safe_paths = []
        
        for path in paths:
            validation = self.validate_path(path)
            if validation.is_safe:
                safe_paths.append(path)
        
        return safe_paths
    
    def can_access_path(self, path: Path, require_write: bool = False) -> bool:
        """
        Check if a path can be accessed
        
        Args:
            path: Path to check
            require_write: Whether write access is required
            
        Returns:
            True if accessible, False otherwise
        """
        validation = self.validate_path(path)
        
        if not validation.is_safe:
            return False
        
        if require_write and not validation.can_write:
            return False
        
        return True
    
    def get_security_warning(self, path: Path) -> Optional[str]:
        """
        Get security warning for a path
        
        Args:
            path: Path to check
            
        Returns:
            Warning message or None if safe
        """
        validation = self.validate_path(path)
        
        if validation.security_level == SecurityLevel.FORBIDDEN:
            return f"FORBIDDEN: {validation.reason}"
        elif validation.security_level == SecurityLevel.DANGER:
            return f"DANGER: {validation.reason}"
        elif validation.security_level == SecurityLevel.CAUTION:
            return f"CAUTION: {validation.reason}"
        
        return None
    
    def is_system_file(self, file_path: Path) -> bool:
        """
        Check if a file is a system file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if system file, False otherwise
        """
        try:
            # Check extension
            if file_path.suffix.lower() in self.DANGEROUS_EXTENSIONS:
                return True
            
            # Check if in system folder
            validation = self.validate_path(file_path)
            return validation.security_level in [SecurityLevel.DANGER, SecurityLevel.FORBIDDEN]
            
        except Exception:
            return False
    
    def sanitize_path(self, path: Path) -> Optional[Path]:
        """
        Sanitize a path to ensure it's safe
        
        Args:
            path: Path to sanitize
            
        Returns:
            Sanitized path or None if unsafe
        """
        validation = self.validate_path(path)
        
        if validation.is_safe:
            return path
        
        return None


class PathPermissionChecker:
    """
    Checks actual file system permissions
    """
    
    @staticmethod
    def can_read(path: Path) -> bool:
        """
        Check if path can be read
        
        Args:
            path: Path to check
            
        Returns:
            True if readable, False otherwise
        """
        try:
            return Path(path).exists()
        except Exception:
            return False
    
    @staticmethod
    def can_write(path: Path) -> bool:
        """
        Check if path can be written to
        
        Args:
            path: Path to check
            
        Returns:
            True if writable, False otherwise
        """
        try:
            if path.is_file():
                # For files, check if we can write to parent
                return Path(path.parent).exists()
            else:
                # For directories, check if we can create a test file
                test_file = path / ".write_test"
                test_file.touch()
                test_file.unlink()
                return True
        except Exception:
            return False
    
    @staticmethod
    def can_delete(path: Path) -> bool:
        """
        Check if path can be deleted
        
        Args:
            path: Path to check
            
        Returns:
            True if deletable, False otherwise
        """
        try:
            # For now, same as write permission
            return PathPermissionChecker.can_write(path)
        except Exception:
            return False
    
    @staticmethod
    def get_permission_string(path: Path) -> str:
        """
        Get human-readable permission string
        
        Args:
            path: Path to check
            
        Returns:
            Permission string (e.g., "r--", "rw-", "rwx")
        """
        permissions = []
        
        if PathPermissionChecker.can_read(path):
            permissions.append('r')
        else:
            permissions.append('-')
        
        if PathPermissionChecker.can_write(path):
            permissions.append('w')
        else:
            permissions.append('-')
        
        if PathPermissionChecker.can_delete(path):
            permissions.append('x')
        else:
            permissions.append('-')
        
        return ''.join(permissions)