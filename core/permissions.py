"""
Permissions Module for DiskMaster V2
Handles administrator privileges and permission elevation
"""

import ctypes
import os
import sys
from typing import Optional, Callable
from enum import Enum


class PrivilegeLevel(Enum):
    """Privilege levels for operations"""
    USER = "user"  # Standard user privileges
    ADMIN = "admin"  # Administrator privileges
    ELEVATED = "elevated"  # Elevated administrator privileges


class PermissionManager:
    """
    Manages Windows permissions and elevation
    """
    
    def __init__(self):
        """Initialize permission manager"""
        self._is_admin = self._check_admin()
        self._is_elevated = self._check_elevated()
        self._privilege_level = self._determine_privilege_level()
    
    def _check_admin(self) -> bool:
        """
        Check if current process has administrator privileges
        
        Returns:
            True if admin, False otherwise
        """
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    
    def _check_elevated(self) -> bool:
        """
        Check if process is running with elevated privileges
        
        Returns:
            True if elevated, False otherwise
        """
        try:
            # This is a simplified check
            # In a real implementation, you might check token elevation
            return self._is_admin  # For now, same as admin
        except Exception:
            return False
    
    def _determine_privilege_level(self) -> PrivilegeLevel:
        """
        Determine current privilege level
        
        Returns:
            Current privilege level
        """
        if self._is_elevated:
            return PrivilegeLevel.ELEVATED
        elif self._is_admin:
            return PrivilegeLevel.ADMIN
        else:
            return PrivilegeLevel.USER
    
    def is_admin(self) -> bool:
        """
        Check if running as administrator
        
        Returns:
            True if admin, False otherwise
        """
        return self._is_admin
    
    def is_elevated(self) -> bool:
        """
        Check if running with elevated privileges
        
        Returns:
            True if elevated, False otherwise
        """
        return self._is_elevated
    
    def get_privilege_level(self) -> PrivilegeLevel:
        """
        Get current privilege level
        
        Returns:
            Current privilege level
        """
        return self._privilege_level
    
    def request_elevation(self) -> bool:
        """
        Request administrator elevation
        
        Returns:
            True if elevation was requested, False otherwise
        """
        try:
            if self._is_admin:
                return True  # Already admin
            
            # Request elevation by restarting with admin rights
            if sys.executable:
                params = ' '.join([sys.executable] + sys.argv)
                ctypes.windll.shell32.ShellExecuteW(
                    None,
                    "runas",
                    sys.executable,
                    params,
                    None,
                    1
                )
                return True
            
            return False
            
        except Exception:
            return False
    
    def can_access_system_folders(self) -> bool:
        """
        Check if can access system folders
        
        Returns:
            True if can access, False otherwise
        """
        return self._is_admin
    
    def can_modify_system_files(self) -> bool:
        """
        Check if can modify system files
        
        Returns:
            True if can modify, False otherwise
        """
        return self._is_elevated
    
    def requires_admin_for_operation(self, operation: str) -> bool:
        """
        Check if an operation requires administrator privileges
        
        Args:
            operation: Operation description
            
        Returns:
            True if requires admin, False otherwise
        """
        # Define operations that require admin
        admin_operations = [
            'system_cleanup',
            'registry_access',
            'system_file_modification',
            'driver_installation',
            'service_management'
        ]
        
        return operation.lower() in admin_operations
    
    def get_permission_string(self) -> str:
        """
        Get human-readable permission string
        
        Returns:
            Permission description
        """
        if self._privilege_level == PrivilegeLevel.ELEVATED:
            return "Elevated Administrator"
        elif self._privilege_level == PrivilegeLevel.ADMIN:
            return "Administrator"
        else:
            return "Standard User"


class AccessChecker:
    """
    Checks file system access permissions
    """
    
    @staticmethod
    def can_read_file(file_path: str) -> bool:
        """
        Check if can read a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if can read, False otherwise
        """
        try:
            return os.access(file_path, os.R_OK)
        except Exception:
            return False
    
    @staticmethod
    def can_write_file(file_path: str) -> bool:
        """
        Check if can write to a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if can write, False otherwise
        """
        try:
            return os.access(file_path, os.W_OK)
        except Exception:
            return False
    
    @staticmethod
    def can_execute_file(file_path: str) -> bool:
        """
        Check if can execute a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if can execute, False otherwise
        """
        try:
            return os.access(file_path, os.X_OK)
        except Exception:
            return False
    
    @staticmethod
    def can_delete_file(file_path: str) -> bool:
        """
        Check if can delete a file
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if can delete, False otherwise
        """
        try:
            # Check if parent directory is writable
            parent_dir = os.path.dirname(file_path)
            return os.access(parent_dir, os.W_OK)
        except Exception:
            return False
    
    @staticmethod
    def can_create_file(directory: str) -> bool:
        """
        Check if can create a file in directory
        
        Args:
            directory: Directory path
            
        Returns:
            True if can create, False otherwise
        """
        try:
            return os.access(directory, os.W_OK)
        except Exception:
            return False
    
    @staticmethod
    def get_file_permissions(file_path: str) -> str:
        """
        Get file permissions string
        
        Args:
            file_path: Path to the file
            
        Returns:
            Permission string (e.g., "rwx", "r--")
        """
        permissions = []
        
        if AccessChecker.can_read_file(file_path):
            permissions.append('r')
        else:
            permissions.append('-')
        
        if AccessChecker.can_write_file(file_path):
            permissions.append('w')
        else:
            permissions.append('-')
        
        if AccessChecker.can_execute_file(file_path):
            permissions.append('x')
        else:
            permissions.append('-')
        
        return ''.join(permissions)


class PermissionRequest:
    """
    Handles permission requests from user
    """
    
    @staticmethod
    def request_admin_permission(reason: str) -> bool:
        """
        Request administrator permission with explanation
        
        Args:
            reason: Reason for admin permission
            
        Returns:
            True if granted/received, False otherwise
        """
        permission_manager = PermissionManager()
        
        if permission_manager.is_admin():
            return True
        
        # In a real application, you would show a dialog to the user
        # explaining why admin rights are needed and offer to elevate
        print(f"Admin permission required: {reason}")
        
        # For now, just try to elevate
        return permission_manager.request_elevation()
    
    @staticmethod
    def check_operation_permission(operation: str, path: str = "") -> bool:
        """
        Check if an operation can be performed with current permissions
        
        Args:
            operation: Operation to perform
            path: Path to operate on (optional)
            
        Returns:
            True if operation is allowed, False otherwise
        """
        permission_manager = PermissionManager()
        
        # Check if operation requires admin
        if permission_manager.requires_admin_for_operation(operation):
            return permission_manager.is_admin()
        
        # Check file-specific permissions if path provided
        if path:
            if operation in ['read', 'view']:
                return AccessChecker.can_read_file(path)
            elif operation in ['write', 'modify', 'move']:
                return AccessChecker.can_write_file(path)
            elif operation == 'delete':
                return AccessChecker.can_delete_file(path)
        
        return True


# Global permission manager instance
_permission_manager: Optional[PermissionManager] = None


def get_permission_manager() -> PermissionManager:
    """Get global permission manager instance"""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = PermissionManager()
    return _permission_manager