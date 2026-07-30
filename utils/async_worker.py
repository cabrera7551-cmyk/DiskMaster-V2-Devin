"""
Async Worker for DiskMaster V2
Provides async operation support for UI responsiveness
"""

from PyQt6.QtCore import QThread, pyqtSignal, QObject, QMutex, QMutexLocker
from typing import Callable, Any, Optional
import traceback


class WorkerSignals(QObject):
    """Signals for worker communication"""
    
    finished = pyqtSignal(object)  # Result signal
    error = pyqtSignal(str)  # Error signal
    progress = pyqtSignal(int, str)  # Progress signal (percentage, message)
    started = pyqtSignal()  # Started signal
    cancelled = pyqtSignal()  # Cancelled signal


class AsyncWorker(QThread):
    """
    Async worker for running operations in background thread
    
    This allows long-running operations to execute without blocking the UI
    """
    
    def __init__(self, func: Callable, *args, **kwargs):
        """
        Initialize async worker
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
        """
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()
        self._is_cancelled = False
        self._result = None
        self._exception = None
        self._mutex = QMutex()
        self._cleanup_done = False
    
    def run(self):
        """Execute the function in background thread"""
        try:
            self.signals.started.emit()
            
            # Check if function accepts progress callback
            if 'progress_callback' in self.kwargs:
                self.kwargs['progress_callback'] = self._progress_callback
            
            # Execute the function
            self._result = self.func(*self.args, **self.kwargs)
            
            with QMutexLocker(self._mutex):
                if not self._is_cancelled:
                    self.signals.finished.emit(self._result)
                else:
                    self.signals.cancelled.emit()
            
            self._cleanup_done = True
                
        except Exception as e:
            with QMutexLocker(self._mutex):
                self._exception = e
                error_msg = f"{type(e).__name__}: {str(e)}"
                self.signals.error.emit(error_msg)
                print(f"Worker error: {error_msg}")
                traceback.print_exc()
            self._cleanup_done = True
    
    def _progress_callback(self, percentage: int, message: str = ""):
        """
        Progress callback for long-running operations
        
        Args:
            percentage: Progress percentage (0-100)
            message: Progress message
        """
        with QMutexLocker(self._mutex):
            if not self._is_cancelled:
                self.signals.progress.emit(percentage, message)
    
    def cancel(self):
        """Cancel the running operation"""
        with QMutexLocker(self._mutex):
            self._is_cancelled = True
        
        # Quit the thread and wait for it to finish
        self.quit()
        self.wait(5000)  # Wait up to 5 seconds for thread to finish
    
    def safe_delete(self):
        """Safely delete the worker"""
        # Cancel if still running
        if self.isRunning():
            self.cancel()
        
        # Disconnect all signals safely
        try:
            # Disconnect specific signals instead of wildcard
            self.signals.finished.disconnect()
        except:
            pass
        
        try:
            self.signals.error.disconnect()
        except:
            pass
        
        try:
            self.signals.progress.disconnect()
        except:
            pass
        
        try:
            self.signals.started.disconnect()
        except:
            pass
        
        try:
            self.signals.cancelled.disconnect()
        except:
            pass
        
        # Wait for thread to finish
        if self.isRunning():
            self.wait(2000)  # Additional wait time
    
    def is_cancelled(self) -> bool:
        """Check if operation was cancelled"""
        with QMutexLocker(self._mutex):
            return self._is_cancelled
    
    def get_result(self) -> Any:
        """Get the result of the operation"""
        with QMutexLocker(self._mutex):
            return self._result
    
    def get_exception(self) -> Optional[Exception]:
        """Get any exception that occurred"""
        with QMutexLocker(self._mutex):
            return self._exception
    
    def __del__(self):
        """Cleanup when object is destroyed"""
        self.safe_delete()


class ParallelWorker:
    """
    Manages multiple parallel workers for concurrent operations
    """
    
    def __init__(self, max_workers: int = 4):
        """
        Initialize parallel worker manager
        
        Args:
            max_workers: Maximum number of concurrent workers
        """
        self.max_workers = max_workers
        self.active_workers = []
        self.pending_tasks = []
    
    def add_task(self, func: Callable, *args, **kwargs) -> AsyncWorker:
        """
        Add a task to the execution queue
        
        Args:
            func: Function to execute
            *args: Arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            Worker instance for the task
        """
        worker = AsyncWorker(func, *args, **kwargs)
        
        if len(self.active_workers) < self.max_workers:
            self._start_worker(worker)
        else:
            self.pending_tasks.append(worker)
        
        return worker
    
    def _start_worker(self, worker: AsyncWorker):
        """Start a worker and manage its lifecycle"""
        self.active_workers.append(worker)
        
        def on_finished():
            self.active_workers.remove(worker)
            self._process_pending()
        
        worker.signals.finished.connect(on_finished)
        worker.signals.error.connect(on_finished)
        worker.signals.cancelled.connect(on_finished)
        
        worker.start()
    
    def _process_pending(self):
        """Process pending tasks when a worker becomes available"""
        if self.pending_tasks and len(self.active_workers) < self.max_workers:
            worker = self.pending_tasks.pop(0)
            self._start_worker(worker)
    
    def cancel_all(self):
        """Cancel all active and pending workers"""
        for worker in self.active_workers:
            worker.cancel()
        
        self.pending_tasks.clear()
    
    def wait_all(self):
        """Wait for all workers to complete"""
        for worker in self.active_workers:
            worker.wait()
    
    def is_busy(self) -> bool:
        """Check if any workers are active"""
        return len(self.active_workers) > 0


class ProgressTracker:
    """
    Tracks progress for complex multi-stage operations
    """
    
    def __init__(self, total_stages: int):
        """
        Initialize progress tracker
        
        Args:
            total_stages: Total number of stages in the operation
        """
        self.total_stages = total_stages
        self.current_stage = 0
        self.stage_progress = 0
        self.stage_weights = [1.0] * total_stages  # Equal weight by default
    
    def set_stage_weights(self, weights: list):
        """
        Set custom weights for each stage
        
        Args:
            weights: List of weights for each stage
        """
        if len(weights) == self.total_stages:
            self.stage_weights = weights
    
    def next_stage(self):
        """Move to the next stage"""
        if self.current_stage < self.total_stages:
            self.current_stage += 1
            self.stage_progress = 0
    
    def update_stage_progress(self, progress: int):
        """
        Update progress within current stage
        
        Args:
            progress: Progress percentage (0-100)
        """
        self.stage_progress = progress
    
    def get_overall_progress(self) -> int:
        """
        Calculate overall progress across all stages
        
        Returns:
            Overall progress percentage (0-100)
        """
        if self.total_stages == 0:
            return 0
        
        total_weight = sum(self.stage_weights)
        current_weight = sum(self.stage_weights[:self.current_stage])
        stage_weight = self.stage_weights[self.current_stage] if self.current_stage < self.total_stages else 0
        
        stage_contribution = (self.stage_progress / 100) * stage_weight
        overall_progress = ((current_weight + stage_contribution) / total_weight) * 100
        
        return int(overall_progress)
    
    def get_stage_name(self) -> str:
        """
        Get current stage name
        
        Returns:
            Current stage identifier
        """
        return f"Stage {self.current_stage + 1}/{self.total_stages}"