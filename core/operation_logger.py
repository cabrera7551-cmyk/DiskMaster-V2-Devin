"""
Operation Logger for DiskMaster V2
Detailed logging and history tracking for file operations
"""

import json
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from enum import Enum

from utils.path_handler import get_path_handler
from core.file_manager import FileOperation, OperationStatus


class LogLevel(Enum):
    """Log levels for operations"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"


@dataclass
class OperationLog:
    """Detailed log entry for an operation"""
    log_id: str
    operation_id: str
    timestamp: str
    level: LogLevel
    operation_type: str
    source_path: str
    destination_path: str
    file_size: int
    status: str
    duration_seconds: float
    error_message: Optional[str]
    details: Dict[str, any]


class OperationLogger:
    """
    Detailed logging system for file operations
    """
    
    def __init__(self):
        """Initialize operation logger"""
        self.path_handler = get_path_handler()
        self.logs: List[OperationLog] = []
        self._log_file = self.path_handler.get_logs_dir() / "operations.log"
        self._log_file.parent.mkdir(parents=True, exist_ok=True)
        self._load_logs()
    
    def _load_logs(self):
        """Load logs from file"""
        if self._log_file.exists():
            try:
                with open(self._log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.logs = [
                        OperationLog(**log) for log in data
                    ]
            except Exception as e:
                print(f"Error loading logs: {e}")
                self.logs = []
    
    def _save_logs(self):
        """Save logs to file"""
        try:
            data = [asdict(log) for log in self.logs]
            with open(self._log_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving logs: {e}")
    
    def log_operation(
        self,
        operation: FileOperation,
        level: LogLevel = LogLevel.INFO,
        details: Optional[Dict[str, any]] = None,
        duration: float = 0.0
    ):
        """
        Log a file operation
        
        Args:
            operation: File operation to log
            level: Log level
            details: Additional details
            duration: Operation duration in seconds
        """
        log_entry = OperationLog(
            log_id=datetime.now().strftime("%Y%m%d_%H%M%S_%f"),
            operation_id=operation.operation_id,
            timestamp=datetime.now().isoformat(),
            level=level,
            operation_type=operation.operation_type,
            source_path=operation.source_path,
            destination_path=operation.destination_path,
            file_size=operation.original_size,
            status=operation.status.value,
            duration_seconds=duration,
            error_message=operation.error_message,
            details=details or {}
        )
        
        self.logs.append(log_entry)
        self._save_logs()
    
    def log_batch_operation(
        self,
        operations: List[FileOperation],
        level: LogLevel = LogLevel.INFO,
        details: Optional[Dict[str, any]] = None,
        duration: float = 0.0
    ):
        """
        Log a batch of operations
        
        Args:
            operations: List of file operations
            level: Log level
            details: Additional details
            duration: Total duration in seconds
        """
        batch_details = details or {}
        batch_details["batch_operation"] = True
        batch_details["operation_count"] = len(operations)
        
        for operation in operations:
            self.log_operation(operation, level, batch_details, duration)
    
    def get_logs_by_operation_id(self, operation_id: str) -> List[OperationLog]:
        """
        Get all logs for a specific operation
        
        Args:
            operation_id: Operation ID
            
        Returns:
            List of log entries
        """
        return [log for log in self.logs if log.operation_id == operation_id]
    
    def get_logs_by_level(self, level: LogLevel) -> List[OperationLog]:
        """
        Get logs by level
        
        Args:
            level: Log level
            
        Returns:
            List of log entries
        """
        return [log for log in self.logs if log.level == level]
    
    def get_logs_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> List[OperationLog]:
        """
        Get logs within a date range
        
        Args:
            start_date: Start date
            end_date: End date
            
        Returns:
            List of log entries
        """
        return [
            log for log in self.logs
            if start_date <= datetime.fromisoformat(log.timestamp) <= end_date
        ]
    
    def get_recent_logs(self, limit: int = 50) -> List[OperationLog]:
        """
        Get recent logs
        
        Args:
            limit: Maximum number of logs to return
            
        Returns:
            List of recent log entries
        """
        return self.logs[-limit:] if self.logs else []
    
    def get_error_logs(self) -> List[OperationLog]:
        """
        Get all error logs
        
        Returns:
            List of error log entries
        """
        return [log for log in self.logs if log.level == LogLevel.ERROR]
    
    def get_statistics(self) -> Dict[str, any]:
        """
        Get logging statistics
        
        Returns:
            Dictionary with statistics
        """
        stats = {
            "total_logs": len(self.logs),
            "info_logs": len([log for log in self.logs if log.level == LogLevel.INFO]),
            "warning_logs": len([log for log in self.logs if log.level == LogLevel.WARNING]),
            "error_logs": len([log for log in self.logs if log.level == LogLevel.ERROR]),
            "success_logs": len([log for log in self.logs if log.level == LogLevel.SUCCESS]),
            "move_operations": len([log for log in self.logs if log.operation_type == "move"]),
            "copy_operations": len([log for log in self.logs if log.operation_type == "copy"]),
            "delete_operations": len([log for log in self.logs if log.operation_type == "delete"]),
            "total_bytes_processed": sum(log.file_size for log in self.logs),
        }
        
        return stats
    
    def clear_old_logs(self, days: int = 30):
        """
        Clear logs older than specified days
        
        Args:
            days: Number of days to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        
        self.logs = [
            log for log in self.logs
            if datetime.fromisoformat(log.timestamp) > cutoff_date
        ]
        
        self._save_logs()
    
    def export_logs(self, output_path: Path) -> bool:
        """
        Export logs to a file
        
        Args:
            output_path: Path to export file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            data = [asdict(log) for log in self.logs]
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            print(f"Error exporting logs: {e}")
            return False
    
    def get_operation_summary(self, operation_id: str) -> Dict[str, any]:
        """
        Get summary of a specific operation
        
        Args:
            operation_id: Operation ID
            
        Returns:
            Operation summary
        """
        logs = self.get_logs_by_operation_id(operation_id)
        
        if not logs:
            return {}
        
        latest_log = logs[-1]
        
        return {
            "operation_id": operation_id,
            "timestamp": latest_log.timestamp,
            "status": latest_log.status,
            "type": latest_log.operation_type,
            "source": latest_log.source_path,
            "destination": latest_log.destination_path,
            "size": latest_log.file_size,
            "duration": latest_log.duration_seconds,
            "has_errors": latest_log.level == LogLevel.ERROR,
            "error_message": latest_log.error_message,
            "log_count": len(logs)
        }