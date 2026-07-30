"""
Application Configuration for DiskMaster V2
Manages portable configuration with fallback support
"""

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional
from utils.path_handler import get_path_handler
from utils.constants import AppConstants, AppConfig


class ConfigManager:
    """Manages application configuration with portable support"""
    
    def __init__(self):
        self.path_handler = get_path_handler()
        self.config_file = self.path_handler.get_config_file()
        self.config: Dict[str, Any] = {}
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file or create default"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading config: {e}, using defaults")
                self._create_default_config()
        else:
            self._create_default_config()
    
    def _create_default_config(self):
        """Create default configuration"""
        self.config = {
            'version': '2.0.0',
            'scan': {
                'hidden_files': AppConfig.SCAN_HIDDEN_FILES,
                'system_files': AppConfig.SCAN_SYSTEM_FILES,
                'large_files_threshold': AppConfig.SCAN_LARGE_FILES_THRESHOLD
            },
            'ui': {
                'show_file_sizes': AppConfig.SHOW_FILE_SIZES,
                'show_folder_counts': AppConfig.SHOW_FOLDER_COUNTS,
                'compact_mode': AppConfig.COMPACT_MODE,
                'dark_mode': AppConfig.DARK_MODE,
                'window_width': AppConstants.WINDOW_DEFAULT_WIDTH,
                'window_height': AppConstants.WINDOW_DEFAULT_HEIGHT
            },
            'performance': {
                'enable_parallel_scanning': AppConfig.ENABLE_PARALLEL_SCANNING,
                'max_scan_threads': AppConfig.MAX_SCAN_THREADS,
                'cache_results': AppConfig.CACHE_RESULTS
            },
            'safety': {
                'confirm_before_delete': AppConfig.CONFIRM_BEFORE_DELETE,
                'confirm_before_move': AppConfig.CONFIRM_BEFORE_MOVE,
                'show_system_folders': AppConfig.SHOW_SYSTEM_FOLDERS,
                'safe_mode': AppConfig.SAFE_MODE
            },
            'logging': {
                'enable_logging': AppConfig.ENABLE_LOGGING,
                'log_level': AppConfig.LOG_LEVEL,
                'log_max_size': AppConfig.LOG_MAX_SIZE,
                'log_backup_count': AppConfig.LOG_BACKUP_COUNT
            },
            'portable': {
                'is_portable': self.path_handler.is_portable,
                'is_usb': self.path_handler.is_usb,
                'app_dir': str(self.path_handler.app_dir)
            }
        }
        self._save_config()
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            self.config_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except IOError as e:
            print(f"Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        """Set configuration value"""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
        self._save_config()
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        return self.config.get(section, {})
    
    def update_section(self, section: str, values: Dict[str, Any]):
        """Update entire configuration section"""
        if section not in self.config:
            self.config[section] = {}
        self.config[section].update(values)
        self._save_config()
    
    def reset_to_defaults(self):
        """Reset configuration to defaults"""
        self._create_default_config()
    
    def is_portable_mode(self) -> bool:
        """Check if running in portable mode"""
        return self.get('portable.is_portable', False)
    
    def is_usb_mode(self) -> bool:
        """Check if running from USB"""
        return self.get('portable.is_usb', False)
    
    def get_app_dir(self) -> Path:
        """Get application directory"""
        return Path(self.get('portable.app_dir', str(Path.cwd())))


# Global configuration instance
_config_manager: Optional[ConfigManager] = None


def get_config() -> ConfigManager:
    """Get global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager