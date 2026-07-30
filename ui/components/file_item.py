"""
File Item Component for DiskMaster V2
Displays file information in Terminal Blackout Blue style
"""

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout, QLabel, QCheckBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from utils.constants import AppConstants
from utils.formatters import SizeFormatter, PathFormatter
from core.folder_scanner import FileInfo


class FileItem(QFrame):
    """
    Component for displaying file information with selection support
    """
    
    clicked = pyqtSignal(object)  # Signal when file is clicked
    selected_changed = pyqtSignal(object, bool)  # Signal when selection changes
    
    def __init__(self, file_info: FileInfo):
        """
        Initialize file item
        
        Args:
            file_info: FileInfo object with file data
        """
        super().__init__()
        
        self.file_info = file_info
        self._is_selected = False
        
        self._setup_ui()
        self._update_content()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup item UI layout"""
        self.setFixedHeight(50)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 6, 10, 6)
        layout.setSpacing(10)
        
        # Checkbox for selection
        self.checkbox = QCheckBox()
        self.checkbox.setFixedSize(16, 16)
        self.checkbox.stateChanged.connect(self._on_checkbox_changed)
        layout.addWidget(self.checkbox)
        
        # File icon based on extension
        icon_label = QLabel(self._get_file_icon())
        icon_label.setFixedSize(20, 20)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 14px;")
        layout.addWidget(icon_label)
        
        # File info layout
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        # File name
        self.name_label = QLabel()
        self.name_label.setObjectName("file-name")
        info_layout.addWidget(self.name_label)
        
        # File size and extension
        details_layout = QHBoxLayout()
        details_layout.setSpacing(10)
        
        self.size_label = QLabel()
        self.size_label.setObjectName("file-size")
        details_layout.addWidget(self.size_label)
        
        self.ext_label = QLabel()
        self.ext_label.setObjectName("file-ext")
        details_layout.addWidget(self.ext_label)
        
        info_layout.addLayout(details_layout)
        
        layout.addLayout(info_layout, 1)  # Take remaining space
        
        # Modified date
        self.date_label = QLabel()
        self.date_label.setObjectName("file-date")
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.date_label)
    
    def _get_file_icon(self) -> str:
        """Get appropriate icon based on file extension"""
        ext = self.file_info.extension.lower()
        
        # Common file type icons
        icon_map = {
            '.txt': '📄',
            '.doc': '📄',
            '.docx': '📄',
            '.pdf': '📄',
            '.xls': '📊',
            '.xlsx': '📊',
            '.ppt': '📊',
            '.pptx': '📊',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.mp3': '🎵',
            '.wav': '🎵',
            '.mp4': '🎬',
            '.avi': '🎬',
            '.mkv': '🎬',
            '.zip': '📦',
            '.rar': '📦',
            '.7z': '📦',
            '.exe': '⚙️',
            '.msi': '⚙️',
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.xml': '📋',
            '.sql': '🗃️',
            '.db': '🗃️',
        }
        
        return icon_map.get(ext, '📄')
    
    def _update_content(self):
        """Update item content with file information"""
        # Truncate name if too long
        display_name = PathFormatter.format_filename(self.file_info.name, 30)
        self.name_label.setText(display_name)
        
        self.size_label.setText(self.file_info.get_formatted_size())
        self.ext_label.setText(self.file_info.extension.upper() if self.file_info.extension else "FILE")
        
        # Format date
        from utils.formatters import TimeFormatter
        self.date_label.setText(TimeFormatter.format_timestamp(self.file_info.modified_time))
    
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
            QLabel#file-name {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#file-size {{
                color: {AppConstants.COLOR_ACCENT};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#file-ext {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_SMALL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
            QLabel#file-date {{
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
                self.clicked.emit(self.file_info)
        super().mousePressEvent(event)
    
    def _on_checkbox_changed(self, state):
        """Handle checkbox state change"""
        was_selected = self._is_selected
        self._is_selected = (state == 2)  # 2 = checked
        
        if was_selected != self._is_selected:
            self._update_selection_style()
            self.selected_changed.emit(self.file_info, self._is_selected)
    
    def toggle_selection(self):
        """Toggle selection state"""
        self._is_selected = not self._is_selected
        self.checkbox.setChecked(self._is_selected)
        self._update_selection_style()
        self.selected_changed.emit(self.file_info, self._is_selected)
    
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
                QLabel#file-name {{
                    color: {AppConstants.COLOR_TEXT_PRIMARY};
                    font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
                QLabel#file-size {{
                    color: {AppConstants.COLOR_ACCENT};
                    font-size: {AppConstants.FONT_SIZE_SMALL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
                QLabel#file-ext {{
                    color: {AppConstants.COLOR_TEXT_SECONDARY};
                    font-size: {AppConstants.FONT_SIZE_SMALL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
                QLabel#file-date {{
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
    
    def update_file_info(self, file_info: FileInfo):
        """
        Update file information
        
        Args:
            file_info: New file information
        """
        self.file_info = file_info
        self._update_content()
    
    def refresh(self):
        """Refresh the item display"""
        self._update_content()