"""
Data Manager for DiskMaster V2
Handles data persistence and caching for portable application
"""

import json
import pickle
from pathlib import Path
from typing import Any, Optional, Dict
from datetime import datetime, timedelta

from utils.path_handler import get_path_handler


class DataManager:
    """
    Manages data persistence with portable support
    """
    
    def __init__(self):
        """Initialize data manager"""
        self.path_handler = get_path_handler()
        self.cache_dir = self.path_handler.get_cache_dir()
        self._cache_ttl = timedelta(hours=1)  # Cache expires after 1 hour
    
    def save_json(self, data: Any, filename: str) -> bool:
        """
        Save data as JSON file
        
        Args:
            data: Data to save
            filename: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.cache_dir / filename
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving JSON data: {e}")
            return False
    
    def load_json(self, filename: str) -> Optional[Any]:
        """
        Load data from JSON file
        
        Args:
            filename: Name of the file
            
        Returns:
            Loaded data or None if error
        """
        try:
            file_path = self.cache_dir / filename
            if not file_path.exists():
                return None
            
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading JSON data: {e}")
            return None
    
    def save_pickle(self, data: Any, filename: str) -> bool:
        """
        Save data as pickle file
        
        Args:
            data: Data to save
            filename: Name of the file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            file_path = self.cache_dir / filename
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"Error saving pickle data: {e}")
            return False
    
    def load_pickle(self, filename: str) -> Optional[Any]:
        """
        Load data from pickle file
        
        Args:
            filename: Name of the file
            
        Returns:
            Loaded data or None if error
        """
        try:
            file_path = self.cache_dir / filename
            if not file_path.exists():
                return None
            
            with open(file_path, 'rb') as f:
                return pickle.load(f)
        except Exception as e:
            print(f"Error loading pickle data: {e}")
            return None
    
    def cache_data(self, key: str, data: Any, ttl: Optional[timedelta] = None) -> bool:
        """
        Cache data with time-to-live
        
        Args:
            key: Cache key
            data: Data to cache
            ttl: Time-to-live (uses default if not specified)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cache_entry = {
                'data': data,
                'timestamp': datetime.now().isoformat(),
                'ttl': (ttl or self._cache_ttl).total_seconds()
            }
            
            filename = f"cache_{key}.json"
            return self.save_json(cache_entry, filename)
        except Exception as e:
            print(f"Error caching data: {e}")
            return False
    
    def get_cached_data(self, key: str) -> Optional[Any]:
        """
        Get cached data if still valid
        
        Args:
            key: Cache key
            
        Returns:
            Cached data or None if expired/not found
        """
        try:
            filename = f"cache_{key}.json"
            cache_entry = self.load_json(filename)
            
            if cache_entry is None:
                return None
            
            # Check if cache is still valid
            timestamp = datetime.fromisoformat(cache_entry['timestamp'])
            ttl = timedelta(seconds=cache_entry['ttl'])
            
            if datetime.now() - timestamp > ttl:
                # Cache expired, delete it
                self.delete_cache(key)
                return None
            
            return cache_entry['data']
        except Exception as e:
            print(f"Error getting cached data: {e}")
            return None
    
    def delete_cache(self, key: str) -> bool:
        """
        Delete cached data
        
        Args:
            key: Cache key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filename = f"cache_{key}.json"
            file_path = self.cache_dir / filename
            
            if file_path.exists():
                file_path.unlink()
                return True
            
            return False
        except Exception as e:
            print(f"Error deleting cache: {e}")
            return False
    
    def clear_all_cache(self) -> bool:
        """
        Clear all cached data
        
        Returns:
            True if successful, False otherwise
        """
        try:
            for file_path in self.cache_dir.glob("cache_*.json"):
                file_path.unlink()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False
    
    def save_scan_result(self, scan_data: Dict[str, Any], scan_id: str) -> bool:
        """
        Save disk scan result
        
        Args:
            scan_data: Scan result data
            scan_id: Unique scan identifier
            
        Returns:
            True if successful, False otherwise
        """
        filename = f"scan_{scan_id}.json"
        return self.save_json(scan_data, filename)
    
    def load_scan_result(self, scan_id: str) -> Optional[Dict[str, Any]]:
        """
        Load disk scan result
        
        Args:
            scan_id: Unique scan identifier
            
        Returns:
            Scan result data or None if not found
        """
        filename = f"scan_{scan_id}.json"
        return self.load_json(filename)
    
    def get_cache_size(self) -> int:
        """
        Get total cache size in bytes
        
        Returns:
            Cache size in bytes
        """
        try:
            total_size = 0
            for file_path in self.cache_dir.iterdir():
                if file_path.is_file():
                    total_size += file_path.stat().st_size
            return total_size
        except Exception:
            return 0
    
    def cleanup_old_cache(self, max_age: timedelta = timedelta(days=7)) -> int:
        """
        Clean up cache files older than specified age
        
        Args:
            max_age: Maximum age for cache files
            
        Returns:
            Number of files cleaned up
        """
        try:
            cleaned_count = 0
            cutoff_time = datetime.now() - max_age
            
            for file_path in self.cache_dir.iterdir():
                if file_path.is_file():
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if file_time < cutoff_time:
                        file_path.unlink()
                        cleaned_count += 1
            
            return cleaned_count
        except Exception as e:
            print(f"Error cleaning up cache: {e}")
            return 0


# Global data manager instance
_data_manager: Optional[DataManager] = None


def get_data_manager() -> DataManager:
    """Get global data manager instance"""
    global _data_manager
    if _data_manager is None:
        _data_manager = DataManager()
    return _data_manager