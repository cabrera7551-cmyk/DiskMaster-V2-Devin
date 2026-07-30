"""
Explorer Panel for DiskMaster V2
Internal file explorer with Terminal Blackout Blue style
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QFrame, QLineEdit, QInputDialog, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from pathlib import Path
from typing import List, Union, Optional

from utils.constants import AppConstants, Messages
from utils.async_worker import AsyncWorker
from core.folder_scanner import FolderScanner, FolderInfo, FileInfo
from core.security import SecurityValidator
from core.disk_analyzer import DiskInfo
from ui.components.folder_item import FolderItem
from ui.components.file_item import FileItem
from ui.components.info_panel import InfoPanel


class ExplorerPanel(QWidget):
    """
    Internal file explorer panel with navigation and selection
    """
    
    back_requested = pyqtSignal()  # Signal to go back to disk selection
    
    def __init__(self):
        super().__init__()
        
        self.folder_scanner = FolderScanner()
        self.security_validator = SecurityValidator()
        
        self.current_disk: Optional[DiskInfo] = None
        self.current_path: Optional[Path] = None
        self.current_items: List[Union[FolderInfo, FileInfo]] = []
        self.selected_items: List[Union[FolderInfo, FileInfo]] = []
        
        self.folder_items: List[FolderItem] = []
        self.file_items: List[FileItem] = []
        self.active_workers: List[AsyncWorker] = []
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup panel UI layout"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Main explorer area
        explorer_area = QWidget()
        explorer_layout = QVBoxLayout(explorer_area)
        explorer_layout.setContentsMargins(20, 20, 20, 20)
        explorer_layout.setSpacing(15)
        
        # Header with navigation
        header_layout = QHBoxLayout()
        
        # Back button
        self.back_button = QPushButton("← VOLVER")
        self.back_button.setObjectName("secondary-button")
        self.back_button.clicked.connect(self._on_back_clicked)
        header_layout.addWidget(self.back_button)
        
        # Current path display
        self.path_label = QLabel("RUTA: No seleccionada")
        self.path_label.setObjectName("path-label")
        header_layout.addWidget(self.path_label, 1)
        
        # Refresh button
        self.refresh_button = QPushButton("ACTUALIZAR")
        self.refresh_button.setObjectName("secondary-button")
        self.refresh_button.clicked.connect(self._on_refresh)
        header_layout.addWidget(self.refresh_button)
        
        explorer_layout.addLayout(header_layout)
        
        # Disk selector
        disk_selector_layout = QHBoxLayout()
        
        self.disk_label = QLabel("DISCO:")
        self.disk_label.setObjectName("info-label")
        disk_selector_layout.addWidget(self.disk_label)
        
        self.disk_selector = QPushButton("Seleccionar Disco")
        self.disk_selector.setObjectName("secondary-button")
        self.disk_selector.clicked.connect(self._on_disk_selector_clicked)
        disk_selector_layout.addWidget(self.disk_selector)
        
        disk_selector_layout.addStretch()
        
        # New folder button
        self.new_folder_button = QPushButton("+ NUEVA CARPETA")
        self.new_folder_button.setObjectName("secondary-button")
        self.new_folder_button.clicked.connect(self._on_new_folder)
        disk_selector_layout.addWidget(self.new_folder_button)
        
        explorer_layout.addLayout(disk_selector_layout)
        
        # Content area with scroll
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(8)
        self.content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        self.scroll_area.setWidget(self.content_widget)
        explorer_layout.addWidget(self.scroll_area)
        
        # Selection control buttons
        selection_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton(Messages.SELECT_ALL)
        self.select_all_button.setObjectName("secondary-button")
        self.select_all_button.setEnabled(False)
        self.select_all_button.clicked.connect(self._on_select_all)
        selection_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton(Messages.DESELECT_ALL)
        self.deselect_all_button.setObjectName("secondary-button")
        self.deselect_all_button.setEnabled(False)
        self.deselect_all_button.clicked.connect(self._on_deselect_all)
        selection_layout.addWidget(self.deselect_all_button)
        
        selection_layout.addStretch()
        
        explorer_layout.addLayout(selection_layout)
        
        layout.addWidget(explorer_area, 1)  # Explorer takes most space
        
        # Info panel
        self.info_panel = InfoPanel()
        self.info_panel.move_requested.connect(self._on_move_requested)
        self.info_panel.set_select_all_callback(self._on_select_all)
        self.info_panel.set_deselect_all_callback(self._on_deselect_all)
        layout.addWidget(self.info_panel)
    
    def _apply_styles(self):
        """Apply Terminal Blackout Blue styles"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {AppConstants.COLOR_BACKGROUND};
            }}
            QLabel#path-label {{
                color: {AppConstants.COLOR_ACCENT};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
                padding: 5px;
            }}
            QLabel#info-label {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QPushButton#secondary-button {{
                background-color: {AppConstants.COLOR_BORDER};
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                border: none;
                padding: 8px 16px;
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
                border-radius: 2px;
            }}
            QPushButton#secondary-button:hover {{
                background-color: {AppConstants.COLOR_HOVER};
            }}
            QPushButton#secondary-button:disabled {{
                background-color: {AppConstants.COLOR_DISABLED};
                color: {AppConstants.COLOR_TEXT_SECONDARY};
            }}
            QScrollArea {{
                background-color: {AppConstants.COLOR_BACKGROUND};
                border: none;
            }}
        """)
    
    def set_disk(self, disk_info: DiskInfo):
        """
        Set the current disk for exploration
        
        Args:
            disk_info: Disk information
        """
        self.current_disk = disk_info
        self.disk_selector.setText(f"{disk_info.letter} - {disk_info.name}")
        self.info_panel.set_selected_disk(disk_info)
        
        # Navigate to user profile on this disk
        user_profile = Path(disk_info.letter) / "Users"
        
        # Find current user directory
        import os
        username = os.environ.get('USERNAME', 'User')
        user_path = user_profile / username
        
        if user_path.exists():
            self.navigate_to_path(user_path)
        else:
            # Fallback to disk root
            self.navigate_to_path(Path(disk_info.letter))
    
    def navigate_to_path(self, path: Path):
        """
        Navigate to a specific path
        
        Args:
            path: Path to navigate to
        """
        if not path.exists() or not path.is_dir():
            QMessageBox.warning(self, "Error", f"La ruta no existe: {path}")
            return
        
        # Security check
        validation = self.security_validator.validate_path(path)
        if not validation.is_safe:
            QMessageBox.warning(self, "Acceso Denegado", f"No se puede acceder a esta ruta: {validation.reason}")
            return
        
        self.current_path = path
        self.path_label.setText(f"RUTA: {path}")
        
        # Clear current selection
        self._clear_selection()
        
        # Load folder contents asynchronously
        self._load_folder_contents(path)
    
    def _load_folder_contents(self, path: Path):
        """Load folder contents asynchronously"""
        # Show loading state
        self.path_label.setText(f"RUTA: {path} (Cargando...)")
        self._clear_content()
        
        # Cancel any existing workers
        self._cleanup_workers()
        
        # Create async worker for folder scanning
        worker = AsyncWorker(
            self.folder_scanner.get_folder_contents,
            path,
            False,  # include_hidden
            "name"  # sort_by
        )
        
        worker.signals.finished.connect(self._on_contents_loaded)
        worker.signals.error.connect(self._on_load_error)
        
        # Track worker for cleanup
        self.active_workers.append(worker)
        
        worker.start()
    
    def _on_contents_loaded(self, contents: List[Path]):
        """Handle folder contents loaded"""
        self.current_items.clear()
        self._clear_content()
        
        # Process contents and create UI items
        folders = []
        files = []
        
        for item_path in contents:
            try:
                if item_path.is_dir():
                    # Quick folder info
                    folder_size = self.folder_scanner.get_folder_size_quick(item_path)
                    file_count = len(list(item_path.glob('*'))) if item_path.exists() else 0
                    
                    folder_info = FolderInfo(
                        path=item_path,
                        name=item_path.name,
                        total_size=folder_size,
                        file_count=file_count,
                        folder_count=0,  # Simplified for now
                        is_hidden=False,
                        is_system=False,
                        contains_system_files=False,
                        modified_time=item_path.stat().st_mtime,
                        created_time=item_path.stat().st_ctime
                    )
                    folders.append(folder_info)
                    self.current_items.append(folder_info)
                    
                elif item_path.is_file():
                    # File info
                    file_info = FileInfo(
                        path=item_path,
                        name=item_path.name,
                        size=item_path.stat().st_size,
                        extension=item_path.suffix,
                        is_hidden=False,
                        is_system=False,
                        modified_time=item_path.stat().st_mtime,
                        created_time=item_path.stat().st_ctime
                    )
                    files.append(file_info)
                    self.current_items.append(file_info)
                    
            except (PermissionError, OSError):
                # Skip items we can't access
                continue
        
        # Create folder items
        for folder_info in folders:
            folder_item = FolderItem(folder_info)
            folder_item.clicked.connect(self._on_item_clicked)
            folder_item.selected_changed.connect(self._on_selection_changed)
            self.folder_items.append(folder_item)
            self.content_layout.addWidget(folder_item)
        
        # Create file items
        for file_info in files:
            file_item = FileItem(file_info)
            file_item.clicked.connect(self._on_item_clicked)
            file_item.selected_changed.connect(self._on_selection_changed)
            self.file_items.append(file_item)
            self.content_layout.addWidget(file_item)
        
        # Update path label
        self.path_label.setText(f"RUTA: {self.current_path}")
        
        # Update selection buttons
        self._update_selection_buttons()
    
    def _on_load_error(self, error_message: str):
        """Handle folder load error"""
        self.path_label.setText(f"RUTA: {self.current_path} (Error)")
        QMessageBox.warning(self, "Error", f"Error al cargar carpeta: {error_message}")
    
    def _clear_content(self):
        """Clear all content items"""
        for item in self.folder_items + self.file_items:
            item.deleteLater()
        
        self.folder_items.clear()
        self.file_items.clear()
    
    def _clear_selection(self):
        """Clear all selections"""
        self.selected_items.clear()
        
        for item in self.folder_items + self.file_items:
            item.set_selected(False)
        
        self.info_panel.set_selected_items([])
        self._update_selection_buttons()
    
    def _on_item_clicked(self, item_info: Union[FolderInfo, FileInfo]):
        """Handle item click"""
        if isinstance(item_info, FolderInfo):
            # Navigate into folder
            self.navigate_to_path(item_info.path)
        # For files, just select them (handled by selection change)
    
    def _on_selection_changed(self, item_info: Union[FolderInfo, FileInfo], selected: bool):
        """Handle selection change"""
        if selected:
            if item_info not in self.selected_items:
                self.selected_items.append(item_info)
        else:
            if item_info in self.selected_items:
                self.selected_items.remove(item_info)
        
        self.info_panel.set_selected_items(self.selected_items)
        self._update_selection_buttons()
    
    def _on_select_all(self):
        """Select all items"""
        for item in self.folder_items + self.file_items:
            item.set_selected(True)
        
        self.selected_items = self.current_items.copy()
        self.info_panel.set_selected_items(self.selected_items)
        self._update_selection_buttons()
    
    def _on_deselect_all(self):
        """Deselect all items"""
        self._clear_selection()
    
    def _update_selection_buttons(self):
        """Update selection button states"""
        has_items = len(self.current_items) > 0
        has_selection = len(self.selected_items) > 0
        
        self.select_all_button.setEnabled(has_items)
        self.deselect_all_button.setEnabled(has_selection)
    
    def _on_back_clicked(self):
        """Handle back button click"""
        self.back_requested.emit()
    
    def _on_refresh(self):
        """Handle refresh button click"""
        if self.current_path:
            self.navigate_to_path(self.current_path)
    
    def _on_disk_selector_clicked(self):
        """Handle disk selector click"""
        self.back_requested.emit()
    
    def _on_new_folder(self):
        """Handle new folder button click"""
        if not self.current_path:
            QMessageBox.warning(self, "Error", "No hay ruta seleccionada")
            return
        
        # Ask for folder name
        folder_name, ok = QInputDialog.getText(
            self, "Nueva Carpeta", "Nombre de la carpeta:"
        )
        
        if ok and folder_name:
            try:
                new_folder = self.current_path / folder_name
                
                # Security check
                validation = self.security_validator.validate_path(new_folder)
                if not validation.is_safe:
                    QMessageBox.warning(self, "Error", f"No se puede crear carpeta aquí: {validation.reason}")
                    return
                
                # Create folder
                new_folder.mkdir(exist_ok=True)
                
                # Refresh
                self.navigate_to_path(self.current_path)
                
            except Exception as e:
                QMessageBox.warning(self, "Error", f"No se pudo crear la carpeta: {str(e)}")
    
    def _on_move_requested(self):
        """Handle move request from info panel"""
        # This will be implemented in the next phase
        QMessageBox.information(
            self, 
            "Movimiento de Archivos", 
            "La funcionalidad de movimiento se implementará en la siguiente fase.\n\n"
            "Actualmente en modo de visualización y selección solamente."
        )
    
    def set_destination_disk(self, disk_info: DiskInfo):
        """
        Set destination disk for move operations
        
        Args:
            disk_info: Destination disk information
        """
        self.info_panel.set_destination_disk(disk_info)
    
    def _cleanup_workers(self):
        """Clean up all active workers"""
        for worker in self.active_workers:
            try:
                worker.safe_delete()
            except:
                pass
        self.active_workers.clear()
    
    def closeEvent(self, event):
        """Handle panel close event"""
        # Clean up all workers
        self._cleanup_workers()
        super().closeEvent(event)
    
    def __del__(self):
        """Cleanup when panel is destroyed"""
        self._cleanup_workers()