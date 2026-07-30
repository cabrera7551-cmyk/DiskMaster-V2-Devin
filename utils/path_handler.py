"""
Path Handler for DiskMaster V2
Manages dynamic paths for portable application execution
"""

import os
import sys
from pathlib import Path
from typing import Optional


class PathHandler:
    """Handles dynamic path resolution for portable execution"""
    
    def __init__(self):
        self._app_dir: Optional[Path] = None
        self._is_portable: bool = False
        self._is_usb: bool = False
        self._initialize_paths()
    
    def _initialize_paths(self):
        """Initialize application paths based on execution location"""
        # Determine if running from executable or script
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            self._app_dir = Path(sys.executable).parent
        else:
            # Running as script
            self._app_dir = Path(__file__).parent.parent
        
        # Detect if running from portable/USB location
        self._detect_portable_mode()
    
    def _detect_portable_mode(self):
        """Detect if application is running in portable mode"""
        try:
            # Check if we can write to app directory
            test_file = self._app_dir / ".write_test"
            try:
                test_file.touch()
                test_file.unlink()
                self._is_portable = True
            except (PermissionError, OSError):
                self._is_portable = False
            
            # Detect if running from USB drive
            drive = self._app_dir.anchor
            if drive and len(drive) == 3:  # Windows drive letter (e.g., "C:\\")
                import psutil
                drive_info = psutil.disk_usage(drive)
                # USB drives are typically removable
                self._is_usb = drive_info is not None
                
        except Exception:
            # If detection fails, assume not portable
            self._is_portable = False
            self._is_usb = False
    
    @property
    def app_dir(self) -> Path:
        """Get application directory"""
        return self._app_dir
    
    @property
    def is_portable(self) -> bool:
        """Check if running in portable mode"""
        return self._is_portable
    
    @property
    def is_usb(self) -> bool:
        """Check if running from USB drive"""
        return self._is_usb
    
    def get_config_dir(self) -> Path:
        """Get configuration directory"""
        if self._is_portable:
            config_dir = self._app_dir / "config"
        else:
            # Fallback to AppData
            config_dir = Path(os.environ.get('LOCALAPPDATA', '~')) / "DiskMasterV2" / "config"
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    def get_data_dir(self) -> Path:
        """Get data directory"""
        if self._is_portable:
            data_dir = self._app_dir / "data"
        else:
            # Fallback to AppData
            data_dir = Path(os.environ.get('LOCALAPPDATA', '~')) / "DiskMasterV2" / "data"
        
        data_dir.mkdir(parents=True, exist_ok=True)
        return data_dir
    
    def get_cache_dir(self) -> Path:
        """Get cache directory"""
        cache_dir = self.get_data_dir() / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def get_logs_dir(self) -> Path:
        """Get logs directory"""
        if self._is_portable:
            logs_dir = self._app_dir / "logs"
        else:
            # Fallback to AppData
            logs_dir = Path(os.environ.get('LOCALAPPDATA', '~')) / "DiskMasterV2" / "logs"
        
        logs_dir.mkdir(parents=True, exist_ok=True)
        return logs_dir
    
    def get_assets_dir(self) -> Path:
        """Get assets directory"""
        if self._is_portable:
            assets_dir = self._app_dir / "assets"
        else:
            # For development/non-portable
            assets_dir = self._app_dir / "assets"
        
        assets_dir.mkdir(parents=True, exist_ok=True)
        return assets_dir
    
    def get_config_file(self, filename: str = "config.json") -> Path:
        """Get specific config file path"""
        return self.get_config_dir() / filename
    
    def get_log_file(self, filename: str = "diskmaster.log") -> Path:
        """Get specific log file path"""
        return self.get_logs_dir() / filename
    
    def get_user_profile_dir(self) -> Path:
        """Get current user profile directory"""
        return Path.home()
    
    def is_path_safe(self, path: Path) -> bool:
        """
        Check if a path is safe for operations
        Prevents system folder manipulation
        """
        try:
            path = Path(path).resolve()
            
            # List of forbidden system folders
            forbidden_names = [
                'Windows',
                'Program Files',
                'Program Files (x86)',
                'Recovery',
                'PerfLogs',
                'System Volume Information',
                'Boot',
                'MSOCache',
                '$Recycle.Bin'
            ]
            
            # Check if path contains forbidden folder names
            for part in path.parts:
                if part in forbidden_names:
                    return False
            
            # Ensure path is within user profile
            user_profile = self.get_user_profile_dir()
            try:
                path.relative_to(user_profile)
                return True
            except ValueError:
                # Path is outside user profile
                return False
                
        except Exception:
            return False
    
    def get_relative_path(self, path: Path, base: Optional[Path] = None) -> str:
        """Get relative path from base directory"""
        if base is None:
            base = self.get_user_profile_dir()
        
        try:
            return str(Path(path).relative_to(base))
        except ValueError:
            return str(path)


# Global instance
_path_handler: Optional[PathHandler] = None


def get_path_handler() -> PathHandler:
    """Get global path handler instance"""
    global _path_handler
    if _path_handler is None:
        _path_handler = PathHandler()
    return _path_handler