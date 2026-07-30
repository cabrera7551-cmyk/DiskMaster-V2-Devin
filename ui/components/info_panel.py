"""
Info Panel Component for DiskMaster V2
Displays selection information in Terminal Blackout Blue style
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List, Union
from pathlib import Path

from utils.constants import AppConstants, Messages
from utils.formatters import SizeFormatter, NumberFormatter
from core.folder_scanner import FolderInfo, FileInfo
from core.disk_analyzer import DiskInfo


class InfoPanel(QFrame):
    """
    Panel for displaying selection and operation information
    """
    
    move_requested = pyqtSignal()  # Signal when move operation is requested
    
    def __init__(self):
        """Initialize info panel"""
        super().__init__()
        
        self.selected_items: List[Union[FolderInfo, FileInfo]] = []
        self.selected_disk: DiskInfo = None
        self.destination_disk: DiskInfo = None
        
        self._setup_ui()
        self._apply_styles()
        self._update_display()
    
    def _setup_ui(self):
        """Setup panel UI layout"""
        self.setFixedWidth(AppConstants.INFO_PANEL_WIDTH)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Title
        title_label = QLabel("INFORMACIÓN")
        title_label.setObjectName("info-title")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Scroll area for content
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        
        self.content_widget = QWidget()
        self.content_layout = QVBoxLayout(self.content_widget)
        self.content_layout.setSpacing(10)
        
        scroll_area.setWidget(self.content_widget)
        layout.addWidget(scroll_area)
        
        # Selection summary
        self.selection_summary = QLabel("No hay selección")
        self.selection_summary.setObjectName("selection-summary")
        self.selection_summary.setWordWrap(True)
        layout.addWidget(self.selection_summary)
        
        # Move button
        self.move_button = QPushButton(Messages.MOVE_SELECTION)
        self.move_button.setObjectName("move-button")
        self.move_button.setEnabled(False)
        self.move_button.clicked.connect(self._on_move_clicked)
        layout.addWidget(self.move_button)
        
        # Select all/deselect all buttons
        button_layout = QHBoxLayout()
        
        self.select_all_button = QPushButton(Messages.SELECT_ALL)
        self.select_all_button.setObjectName("secondary-button")
        self.select_all_button.setEnabled(False)
        # Connections will be set by parent panel
        button_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton(Messages.DESELECT_ALL)
        self.deselect_all_button.setObjectName("secondary-button")
        self.deselect_all_button.setEnabled(False)
        # Connections will be set by parent panel
        button_layout.addWidget(self.deselect_all_button)
        
        layout.addLayout(button_layout)
        
        # Destination selection
        self.destination_label = QLabel("DESTINO:")
        self.destination_label.setObjectName("info-label")
        layout.addWidget(self.destination_label)
        
        self.destination_display = QLabel("No seleccionado")
        self.destination_display.setObjectName("info-value")
        self.destination_display.setWordWrap(True)
        layout.addWidget(self.destination_display)
        
        layout.addStretch()
    
    def _apply_styles(self):
        """Apply Terminal Blackout Blue styles"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppConstants.COLOR_CARD_BACKGROUND};
                border-left: 1px solid {AppConstants.COLOR_BORDER};
            }}
            QLabel#info-title {{
                color: {AppConstants.COLOR_ACCENT};
                font-size: {AppConstants.FONT_SIZE_LARGE}px;
                font-weight: bold;
                font-family: {AppConstants.FONT_FAMILY};
                padding: 10px 0;
                border-bottom: 1px solid {AppConstants.COLOR_BORDER};
            }}
            QLabel#info-label {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
                margin-top: 10px;
            }}
            QLabel#info-value {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#selection-summary {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
                padding: 10px;
                background-color: {AppConstants.COLOR_PROGRESS_EMPTY};
                border-radius: 3px;
            }}
            QPushButton#move-button {{
                background-color: {AppConstants.COLOR_ACCENT};
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                border: none;
                padding: 12px;
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
                font-weight: bold;
                border-radius: 2px;
            }}
            QPushButton#move-button:hover {{
                background-color: #3EA3F1;
            }}
            QPushButton#move-button:disabled {{
                background-color: {AppConstants.COLOR_DISABLED};
                color: {AppConstants.COLOR_TEXT_SECONDARY};
            }}
            QPushButton#secondary-button {{
                background-color: {AppConstants.COLOR_BORDER};
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                border: none;
                padding: 8px;
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
                background-color: transparent;
                border: none;
            }}
        """)
    
    def set_selected_items(self, items: List[Union[FolderInfo, FileInfo]]):
        """
        Set selected items
        
        Args:
            items: List of selected folders and files
        """
        self.selected_items = items
        self._update_display()
    
    def set_selected_disk(self, disk_info: DiskInfo):
        """
        Set the currently selected disk
        
        Args:
            disk_info: Selected disk information
        """
        self.selected_disk = disk_info
        self._update_display()
    
    def set_destination_disk(self, disk_info: DiskInfo):
        """
        Set the destination disk for move operations
        
        Args:
            disk_info: Destination disk information
        """
        self.destination_disk = disk_info
        self._update_display()
    
    def _update_display(self):
        """Update the panel display based on current state"""
        # Clear content layout
        while self.content_layout.count():
            child = self.content_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        # Update selection summary
        if not self.selected_items:
            self.selection_summary.setText("No hay selección")
            self.move_button.setEnabled(False)
            self.select_all_button.setEnabled(False)
            self.deselect_all_button.setEnabled(False)
        else:
            folder_count = sum(1 for item in self.selected_items if isinstance(item, FolderInfo))
            file_count = sum(1 for item in self.selected_items if isinstance(item, FileInfo))
            total_size = sum(item.total_size if isinstance(item, FolderInfo) else item.size 
                           for item in self.selected_items)
            
            summary_text = f"{folder_count} carpetas, {file_count} archivos\n"
            summary_text += f"Total: {SizeFormatter.format_size(total_size)}"
            
            self.selection_summary.setText(summary_text)
            self.move_button.setEnabled(True)
            self.select_all_button.setEnabled(True)
            self.deselect_all_button.setEnabled(True)
        
        # Update destination display
        if self.destination_disk:
            self.destination_display.setText(
                f"{self.destination_disk.letter} - {self.destination_disk.name}\n"
                f"Libre: {self.destination_disk.get_formatted_free()}"
            )
        else:
            self.destination_display.setText("No seleccionado")
        
        # Add selected items details
        for item in self.selected_items[:10]:  # Show first 10 items
            item_label = QLabel()
            item_label.setObjectName("item-detail")
            
            if isinstance(item, FolderInfo):
                item_text = f"📁 {item.name}\n    {item.get_formatted_size()}"
            else:
                item_text = f"📄 {item.name}\n    {item.get_formatted_size()}"
            
            item_label.setText(item_text)
            self.content_layout.addWidget(item_label)
        
        if len(self.selected_items) > 10:
            more_label = QLabel(f"... y {len(self.selected_items) - 10} más")
            more_label.setObjectName("item-detail")
            more_label.setStyleSheet(f"color: {AppConstants.COLOR_TEXT_SECONDARY};")
            self.content_layout.addWidget(more_label)
        
        self.content_layout.addStretch()
    
    def _on_move_clicked(self):
        """Handle move button click"""
        if self.selected_items and self.destination_disk:
            self.move_requested.emit()
    
    def set_select_all_callback(self, callback):
        """Set callback for select all button"""
        try:
            self.select_all_button.clicked.disconnect()
        except TypeError:
            # No connection to disconnect
            pass
        self.select_all_button.clicked.connect(callback)
    
    def set_deselect_all_callback(self, callback):
        """Set callback for deselect all button"""
        try:
            self.deselect_all_button.clicked.disconnect()
        except TypeError:
            # No connection to disconnect
            pass
        self.deselect_all_button.clicked.connect(callback)
    
    def clear_selection(self):
        """Clear all selections"""
        self.selected_items.clear()
        self._update_display()
    
    def get_total_size(self) -> int:
        """Get total size of selected items"""
        return sum(item.total_size if isinstance(item, FolderInfo) else item.size 
                  for item in self.selected_items)
    
    def get_folder_count(self) -> int:
        """Get count of selected folders"""
        return sum(1 for item in self.selected_items if isinstance(item, FolderInfo))
    
    def get_file_count(self) -> int:
        """Get count of selected files"""
        return sum(1 for item in self.selected_items if isinstance(item, FileInfo))