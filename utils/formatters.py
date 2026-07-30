"""
Formatters for DiskMaster V2
Data formatting utilities for consistent display
"""

from typing import Optional
from datetime import timedelta


class SizeFormatter:
    """Formats file sizes in human-readable format"""
    
    UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    @staticmethod
    def format_size(size_bytes: int, precision: int = 2) -> str:
        """
        Format size in bytes to human-readable format
        
        Args:
            size_bytes: Size in bytes
            precision: Number of decimal places
            
        Returns:
            Formatted size string (e.g., "4.5 GB")
        """
        if size_bytes == 0:
            return "0 B"
        
        for unit in SizeFormatter.UNITS:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.{precision}f} {unit}"
            size_bytes /= 1024.0
        
        return f"{size_bytes:.{precision}f} {SizeFormatter.UNITS[-1]}"
    
    @staticmethod
    def parse_size(size_string: str) -> int:
        """
        Parse size string back to bytes
        
        Args:
            size_string: Size string (e.g., "4.5 GB")
            
        Returns:
            Size in bytes
        """
        size_string = size_string.strip().upper()
        
        for i, unit in enumerate(SizeFormatter.UNITS):
            if unit in size_string:
                value = float(size_string.replace(unit, '').strip())
                return int(value * (1024 ** i))
        
        return 0


class PercentageFormatter:
    """Formats percentages for display"""
    
    @staticmethod
    def format_percentage(value: float, precision: int = 1) -> str:
        """
        Format percentage value
        
        Args:
            value: Percentage value (0-100)
            precision: Number of decimal places
            
        Returns:
            Formatted percentage string
        """
        return f"{value:.{precision}f}%"
    
    @staticmethod
    def format_bar(value: float, total_bars: int = 20) -> str:
        """
        Create text-based progress bar
        
        Args:
            value: Percentage value (0-100)
            total_bars: Total number of bars in display
            
        Returns:
            Progress bar string
        """
        filled_bars = int((value / 100) * total_bars)
        empty_bars = total_bars - filled_bars
        
        return '█' * filled_bars + '░' * empty_bars


class TimeFormatter:
    """Formats time durations"""
    
    @staticmethod
    def format_duration(seconds: float) -> str:
        """
        Format duration in seconds to human-readable format
        
        Args:
            seconds: Duration in seconds
            
        Returns:
            Formatted duration string
        """
        if seconds < 60:
            return f"{seconds:.1f}s"
        
        minutes = seconds / 60
        if minutes < 60:
            return f"{minutes:.1f}m"
        
        hours = minutes / 60
        if hours < 24:
            return f"{hours:.1f}h"
        
        days = hours / 24
        return f"{days:.1f}d"
    
    @staticmethod
    def format_timestamp(timestamp: float) -> str:
        """
        Format Unix timestamp to readable string
        
        Args:
            timestamp: Unix timestamp
            
        Returns:
            Formatted datetime string
        """
        from datetime import datetime
        dt = datetime.fromtimestamp(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M:%S")


class NumberFormatter:
    """Formats numbers for display"""
    
    @staticmethod
    def format_number(number: int) -> str:
        """
        Format large numbers with thousands separator
        
        Args:
            number: Number to format
            
        Returns:
            Formatted number string
        """
        return f"{number:,}"
    
    @staticmethod
    def format_file_count(count: int) -> str:
        """
        Format file count with appropriate label
        
        Args:
            count: Number of files
            
        Returns:
            Formatted count string
        """
        if count == 1:
            return "1 archivo"
        return f"{NumberFormatter.format_number(count)} archivos"
    
    @staticmethod
    def format_folder_count(count: int) -> str:
        """
        Format folder count with appropriate label
        
        Args:
            count: Number of folders
            
        Returns:
            Formatted count string
        """
        if count == 1:
            return "1 carpeta"
        return f"{NumberFormatter.format_number(count)} carpetas"


class PathFormatter:
    """Formats file paths for display"""
    
    @staticmethod
    def format_path(path: str, max_length: int = 50) -> str:
        """
        Format path for display, truncating if too long
        
        Args:
            path: File path
            max_length: Maximum length for display
            
        Returns:
            Formatted path string
        """
        if len(path) <= max_length:
            return path
        
        # Truncate middle part
        half_length = (max_length - 3) // 2
        return f"{path[:half_length]}...{path[-half_length:]}"
    
    @staticmethod
    def format_filename(filename: str, max_length: int = 30) -> str:
        """
        Format filename for display, preserving extension
        
        Args:
            filename: Filename
            max_length: Maximum length for display
            
        Returns:
            Formatted filename string
        """
        if len(filename) <= max_length:
            return filename
        
        # Split name and extension
        if '.' in filename:
            name, ext = filename.rsplit('.', 1)
            max_name_length = max_length - len(ext) - 4  # -4 for "..."
            if max_name_length > 0:
                return f"{name[:max_name_length]}...{ext}"
        
        # No extension or too long
        return f"{filename[:max_length-3]}..."
    
    @staticmethod
    def get_extension(filename: str) -> str:
        """
        Get file extension from filename
        
        Args:
            filename: Filename
            
        Returns:
            File extension (without dot)
        """
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ""


class SpeedFormatter:
    """Formats transfer speeds"""
    
    @staticmethod
    def format_speed(bytes_per_second: float) -> str:
        """
        Format transfer speed
        
        Args:
            bytes_per_second: Speed in bytes per second
            
        Returns:
            Formatted speed string
        """
        return f"{SizeFormatter.format_size(int(bytes_per_second))}/s"
    
    @staticmethod
    def calculate_eta(remaining_bytes: int, speed: float) -> str:
        """
        Calculate estimated time of arrival
        
        Args:
            remaining_bytes: Remaining bytes to transfer
            speed: Current speed in bytes per second
            
        Returns:
            Formatted ETA string
        """
        if speed <= 0:
            return "∞"
        
        seconds = remaining_bytes / speed
        return TimeFormatter.format_duration(seconds)