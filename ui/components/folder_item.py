"""
Folder Item Component for DiskMaster V2
Displays folder information in Terminal Blackout Blue style
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from utils.constants import AppConstants
from utils.formatters import SizeFormatter
from core.folder_scanner import FolderInfo


class FolderItem(QFrame):
    """
    Component for displaying folder information with selection support
    """
    
    clicked = pyqtSignal(object)  # Signal when folder is clicked
    selected_changed = pyqtSignal(object, bool)  # Signal when selection changes
    
    def __init__(self, folder_info: FolderInfo):
        """
        Initialize folder item
        
        Args:
            folder_info: FolderInfo object with folder data
        """
        super().__init__()
        
        self.folder_info = folder_info
        self._is_selected = False
        
        self._setup_ui()
        self._update_content()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup item UI layout"""
        self.setFixedHeight(60)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 8, 10, 8)
        layout.setSpacing(10)
        
        # Checkbox for selection
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(16, 16)
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)
        layout.addWidget(self.checkbox)
        
        # Folder icon placeholder
        icon_label = QLabel("📁")
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 16px;")
        layout.addWidget(icon_label)
        
        # Folder info layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # Folder name
        self.name_label = QLabel()
        self.name_label.setObjectName("folder-name")
        info_layout.addWidget(self.name_label)
        
        # Folder size
        self.size_label = QLabel()
        self.size_label.setObjectName("folder-size")
        info_layout.addWidget(self.size_label)
        
        layout.addLayout(info_layout, 1)  # Take remaining space
        
        # File count
        self.count_label = QLabel()
        self.count_label.setObjectName("folder-count")
        self.count_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.count_label)
    
    def _update_content(self):
        """Update item content with folder information"""
        self.name_label.setText(self.folder_info.name)
        self.size_label.setText(self.folder_info.get_formatted_size())
        self.count_label.setText(f"{self.folder_info.file_count:,} archivos")
    
    def _apply_styles(self):
        """Apply Terminal Blackout Blue styles"""
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {AppConstants.COLOR_CARD_BACKGROUND};
                border: 1px solid {AppConstants.COLOR_BORDER};
                border-radius: 3px;
            }}
            QFrame:hover {{
                background-color: {AppConstants.COLOR_HOVER};
                border: 1px solid {AppConstants.COLOR_ACCENT};
            }}
            QLabel#folder-name {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-weight: bold;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#folder-size {{
                color: {AppConstants.COLOR_ACCENT};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#folder-count {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QCheckBox {{
                background-color: transparent;
            }}
            QCheckBox::indicator {{
                width: 14px;
                height: 14px;
                background-color: {AppConstants.COLOR_PROGRESS_EMPTY};
                border: 1px solid {AppConstants.COLOR_BORDER};
                border-radius: 2px;
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {AppConstants.COLOR_ACCENT};
            }}
            QCheckBox::indicator:checked {{
                background-color: {AppConstants.COLOR_ACCENT};
                border: 1px solid {AppConstants.COLOR_ACCENT};
            }}
        """)
    
    def mousePressEvent(self, event):
        """Handle mouse click event"""
        if event.button() == Qt.MouseButton.LeftButton:
            # Toggle selection if clicking on the item (not checkbox)
            if not self.checkbox.underMouse():
                self.toggle_selection()
                self.clicked.emit(self.folder_info)
        super().mousePressEvent(event)
    
    def _on_checkbox_changed(self, state):
        """Handle checkbox state change"""
        was_selected = self._is_selected
        self._is_selected = (state == 2)  # 2 = checked
        
        if was_selected != self._is_selected:
            self._update_selection_style()
            self.selected_changed.emit(self.folder_info, self._is_selected)
    
    def toggle_selection(self):
        """Toggle selection state"""
        self._is_selected = not self._is_selected
        self.checkbox.setChecked(self._is_selected)
        self._update_selection_style()
        self.selected_changed.emit(self.folder_info, self._is_selected)
    
    def set_selected(self, selected: bool):
        """
        Set selected state
        
        Args:
            selected: Whether the item is selected
        """
        if self._is_selected != selected:
            self._is_selected = selected
            self.checkbox.setChecked(selected)
            self._update_selection_style()
    
    def _update_selection_style(self):
        """Update visual style based on selection"""
        if self._is_selected:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: {AppConstants.COLOR_HOVER};
                    border: 2px solid {AppConstants.COLOR_ACCENT};
                    border-radius: 3px;
                }}
                QLabel#folder-name {{
                    color: {AppConstants.COLOR_TEXT_PRIMARY};
                    font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                    font-weight: bold;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
                QLabel#folder-size {{
                    color: {AppConstants.COLOR_ACCENT};
                    font-size: {AppConstants.FONT_SIZE_SMALL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
                QLabel#folder-count {{
                    color: {AppConstants.COLOR_TEXT_SECONDARY};
                    font-size: {AppConstants.FONT_SIZE_SMALL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
                QCheckBox {{
                    background-color: transparent;
                }}
                QCheckBox::indicator {{
                    width: 14px;
                    height: 14px;
                    background-color: {AppConstants.COLOR_ACCENT};
                    border: 1px solid {AppConstants.COLOR_ACCENT};
                    border-radius: 2px;
                }}
            """)
        else:
            self._apply_styles()
    
    def is_selected(self) -> bool:
        """Check if item is selected"""
        return self._is_selected
    
    def update_folder_info(self, folder_info: FolderInfo):
        """
        Update folder information
        
        Args:
            folder_info: New folder information
        """
        self.folder_info = folder_info
        self._update_content()
    
    def refresh(self):
        """Refresh the item display"""
        self._update_content()