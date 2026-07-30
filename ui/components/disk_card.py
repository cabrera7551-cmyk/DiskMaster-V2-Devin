"""
Disk Card Component for DiskMaster V2
Displays disk information in Terminal Blackout Blue style
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QProgressBar
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from utils.constants import AppConstants, DiskStatus
from utils.formatters import SizeFormatter, PercentageFormatter
from core.disk_analyzer import DiskInfo


class DiskCard(QFrame):
    """
    Card component displaying disk information
    """
    
    clicked = pyqtSignal(object)  # Signal when card is clicked
    
    def __init__(self, disk_info: DiskInfo):
        """
        Initialize disk card
        
        Args:
            disk_info: DiskInfo object with disk data
        """
        super().__init__()
        
        self.disk_info = disk_info
        self._is_selected = False
        
        self._setup_ui()
        self._update_content()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup card UI layout"""
        self.setFixedSize(280, 180)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # Disk name and letter
        header_layout = QHBoxLayout()
        self.name_label = QLabel()
        self.name_label.setObjectName("disk-name")
        self.letter_label = QLabel()
        self.letter_label.setObjectName("disk-letter")
        
        header_layout.addWidget(self.name_label)
        header_layout.addStretch()
        header_layout.addWidget(self.letter_label)
        layout.addLayout(header_layout)
        
        # Disk type
        self.type_label = QLabel()
        self.type_label.setObjectName("disk-type")
        layout.addWidget(self.type_label)
        
        layout.addSpacing(10)
        
        # Capacity info
        self.capacity_label = QLabel()
        self.capacity_label.setObjectName("disk-info-label")
        layout.addWidget(self.capacity_label)
        
        self.used_label = QLabel()
        self.used_label.setObjectName("disk-info")
        layout.addWidget(self.used_label)
        
        self.free_label = QLabel()
        self.free_label.setObjectName("disk-info")
        layout.addWidget(self.free_label)
        
        layout.addSpacing(5)
        
        # Usage percentage
        self.usage_label = QLabel()
        self.usage_label.setObjectName("disk-info-label")
        layout.addWidget(self.usage_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setObjectName("disk-progress")
        self.progress_bar.setFixedHeight(8)
        self.progress_bar.setTextVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Status indicator
        self.status_label = QLabel()
        self.status_label.setObjectName("disk-status")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
    
    def _update_content(self):
        """Update card content with disk information"""
        # Name and letter
        self.name_label.setText(self.disk_info.name)
        self.letter_label.setText(self.disk_info.letter)
        
        # Disk type
        self.type_label.setText(f"{self.disk_info.disk_type.value} Drive")
        
        # Capacity information
        self.capacity_label.setText("Capacidad:")
        self.used_label.setText(f"Usado: {self.disk_info.get_formatted_used()}")
        self.free_label.setText(f"Libre: {self.disk_info.get_formatted_free()}")
        
        # Usage
        usage_percent = self.disk_info.get_usage_percentage()
        self.usage_label.setText(f"Uso: {PercentageFormatter.format_percentage(usage_percent)}")
        
        # Progress bar
        self.progress_bar.setValue(int(usage_percent))
        
        # Status
        self.status_label.setText(self._get_status_text())
        
        # Apply status-specific styling
        self._apply_status_style()
    
    def _get_status_text(self) -> str:
        """Get status text based on disk status"""
        status = self.disk_info.status
        if status == DiskStatus.CRITICAL:
            return "⚠ CRÍTICO"
        elif status == DiskStatus.WARNING:
            return "⚠ ADVERTENCIA"
        elif status == DiskStatus.OFFLINE:
            return "⚠ OFFLINE"
        else:
            return "✓ SALUDABLE"
    
    def _apply_status_style(self):
        """Apply status-specific styling"""
        status = self.disk_info.status
        
        if status == DiskStatus.CRITICAL:
            self.progress_bar.setObjectName("disk-progress-critical")
        elif status == DiskStatus.WARNING:
            self.progress_bar.setObjectName("disk-progress-warning")
        else:
            self.progress_bar.setObjectName("disk-progress")
        
        # Reapply styles
        self.progress_bar.style().unpolish(self.progress_bar)
        self.progress_bar.style().polish(self.progress_bar)
    
    def _apply_styles(self):
        """Apply Terminal Blackout Blue styles"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppConstants.COLOR_CARD_BACKGROUND};
                border: 1px solid {AppConstants.COLOR_BORDER};
                border-radius: 4px;
            }}
            QFrame:hover {{
                border: 1px solid {AppConstants.COLOR_ACCENT};
            }}
            QLabel#disk-name {{
                color: {AppConstants.COLOR_ACCENT};
                font-size: {AppConstants.FONT_SIZE_LARGE}px;
                font-weight: bold;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#disk-letter {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_LARGE}px;
                font-weight: bold;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#disk-type {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#disk-info-label {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#disk-info {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#disk-status {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QProgressBar#disk-progress {{
                background-color: {AppConstants.COLOR_PROGRESS_EMPTY};
                border: none;
                border-radius: 2px;
            }}
            QProgressBar#disk-progress::chunk {{
                background-color: {AppConstants.COLOR_PROGRESS_BAR};
            }}
            QProgressBar#disk-progress-warning::chunk {{
                background-color: {AppConstants.COLOR_WARNING};
            }}
            QProgressBar#disk-progress-critical::chunk {{
                background-color: {AppConstants.COLOR_ERROR};
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse click event"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.disk_info)
        super().mousePressEvent(event)
    
    def set_selected(self, selected: bool):
        """
        Set selected state
        
        Args:
            selected: Whether the card is selected
        """
        self._is_selected = selected
        
        if selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {AppConstants.COLOR_HOVER};
                    border: 2px solid {AppConstants.COLOR_ACCENT};
                    border-radius: 4px;
                }}
            """)
        else:
            self._apply_styles()
    
    def is_selected(self) -> bool:
        """Check if card is selected"""
        return self._is_selected
    
    def update_disk_info(self, disk_info: DiskInfo):
        """
        Update disk information
        
        Args:
            disk_info: New disk information
        """
        self.disk_info = disk_info
        self._update_content()
    
    def refresh(self):
        """Refresh the card display"""
        self._update_content()