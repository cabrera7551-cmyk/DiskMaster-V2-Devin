"""
Main Window for DiskMaster V2
Primary application window with sidebar and content panels
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QFrame, QLabel, QPushButton
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

from utils.constants import AppConstants, PanelType
from config.app_config import get_config
from ui.panels.analysis_panel import AnalysisPanel
from ui.panels.explorer_panel import ExplorerPanel
from core.disk_analyzer import DiskInfo


class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        
        self.config = get_config()
        self.current_panel = None
        self.welcome_panel = None
        self.analysis_panel = None
        self.explorer_panel = None
        self.cleanup_panel = None
        self.settings_panel = None
        self.selected_disk: DiskInfo = None
        
        self._setup_window()
        self._setup_ui()
        self._apply_styles()
    
    def _setup_window(self):
        """Setup window properties"""
        self.setWindowTitle(AppConstants.APP_TITLE)
        
        # Set window size from config or defaults
        width = self.config.get('ui.window_width', AppConstants.WINDOW_DEFAULT_WIDTH)
        height = self.config.get('ui.window_height', AppConstants.WINDOW_DEFAULT_HEIGHT)
        
        self.setMinimumSize(AppConstants.WINDOW_MIN_WIDTH, AppConstants.WINDOW_MIN_HEIGHT)
        self.resize(width, height)
        
        # Center window on screen
        self._center_window()
    
    def _center_window(self):
        """Center window on screen"""
        screen = self.screen()
        if screen:
            screen_geometry = screen.availableGeometry()
            window_geometry = self.frameGeometry()
            center_point = screen_geometry.center()
            window_geometry.moveCenter(center_point)
            self.move(window_geometry.topLeft())
    
    def _setup_ui(self):
        """Setup user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = self._create_sidebar()
        main_layout.addWidget(self.sidebar)
        
        # Create content area
        self.content_area = self._create_content_area()
        main_layout.addWidget(self.content_area, 1)  # Content area takes remaining space
        
        # Initialize with welcome panel
        self._show_panel(PanelType.WELCOME)
    
    def _create_sidebar(self) -> QFrame:
        """Create sidebar navigation"""
        sidebar = QFrame()
        sidebar.setFixedWidth(AppConstants.SIDEBAR_WIDTH)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0A0A0A;
                border-right: 1px solid #333333;
            }
        """)
        
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(10, 20, 10, 20)
        layout.setSpacing(5)
        
        # App title
        title_label = QLabel("DISKMASTER V2")
        title_label.setStyleSheet("""
            QLabel {
                color: #2E8FE0;
                font-size: 14px;
                font-weight: bold;
                padding: 10px 0;
            }
        """)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # Navigation buttons
        nav_items = [
            ("~/panel", PanelType.WELCOME),
            ("~/archivos", PanelType.EXPLORER),
            ("~/limpieza", PanelType.CLEANUP),
            ("~/analisis", PanelType.ANALYSIS),
            ("~/ajustes", PanelType.SETTINGS),
        ]
        
        for text, panel_type in nav_items:
            btn = self._create_nav_button(text, panel_type)
            layout.addWidget(btn)
        
        layout.addStretch()
        
        # Version info
        version_label = QLabel(f"v{AppConstants.APP_VERSION}")
        version_label.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 9px;
                padding: 10px 0;
            }
        """)
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(version_label)
        
        return sidebar
    
    def _create_nav_button(self, text: str, panel_type: PanelType) -> QPushButton:
        """Create navigation button"""
        btn = QPushButton(text)
        btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #888888;
                border: none;
                text-align: left;
                padding: 10px;
                font-family: Consolas;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #1A1A3A;
                color: #FFFFFF;
            }
            QPushButton:pressed {
                background-color: #2E8FE0;
                color: #FFFFFF;
            }
        """)
        
        # Store panel type in button for click handler
        btn.panel_type = panel_type
        btn.clicked.connect(lambda: self._on_nav_click(panel_type))
        
        return btn
    
    def _create_content_area(self) -> QFrame:
        """Create main content area"""
        content_area = QFrame()
        content_area.setStyleSheet("""
            QFrame {
                background-color: #000000;
            }
        """)
        
        layout = QVBoxLayout(content_area)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        return content_area
    
    def _on_nav_click(self, panel_type: PanelType):
        """Handle navigation button click"""
        self._show_panel(panel_type)
    
    def _show_panel(self, panel_type: PanelType):
        """Show specific panel in content area"""
        # Remove current panel if exists
        if self.current_panel:
            self.content_area.layout().removeWidget(self.current_panel)
            # Don't delete yet, just remove from layout
        
        # Create or get panel based on type
        if panel_type == PanelType.WELCOME:
            self.current_panel = self._create_welcome_panel()
        elif panel_type == PanelType.ANALYSIS:
            self.current_panel = self._create_analysis_panel()
        elif panel_type == PanelType.EXPLORER:
            self.current_panel = self._create_explorer_panel()
        elif panel_type == PanelType.CLEANUP:
            self.current_panel = self._create_cleanup_panel()
        elif panel_type == PanelType.SETTINGS:
            self.current_panel = self._create_settings_panel()
        else:
            self.current_panel = self._create_welcome_panel()
        
        # Add new panel to content area
        self.content_area.layout().addWidget(self.current_panel)
        self.current_panel.show()
    
    def _create_welcome_panel(self) -> QWidget:
        """Create welcome panel"""
        if self.welcome_panel is None:
            panel = QWidget()
            layout = QVBoxLayout(panel)
            layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            # Title
            title = QLabel(AppConstants.APP_NAME)
            title.setStyleSheet(f"""
                QLabel {{
                    color: {AppConstants.COLOR_ACCENT};
                    font-size: {AppConstants.FONT_SIZE_HEADER}px;
                    font-weight: bold;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
            """)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            # Subtitle
            subtitle = QLabel(AppConstants.APP_TITLE.replace("DiskMaster V2 - ", ""))
            subtitle.setStyleSheet(f"""
                QLabel {{
                    color: {AppConstants.COLOR_TEXT_SECONDARY};
                    font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
            """)
            subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(subtitle)
            
            layout.addSpacing(50)
            
            # Message
            message = QLabel("No se ha realizado ningún análisis.")
            message.setStyleSheet(f"""
                QLabel {{
                    color: {AppConstants.COLOR_TEXT_PRIMARY};
                    font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                }}
            """)
            message.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(message)
            
            layout.addSpacing(30)
            
            # Analyze button
            analyze_btn = QPushButton("ANALIZAR DISCOS")
            analyze_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {AppConstants.COLOR_ACCENT};
                    color: {AppConstants.COLOR_TEXT_PRIMARY};
                    border: none;
                    padding: 15px 30px;
                    font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                    font-family: {AppConstants.FONT_FAMILY};
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: #3EA3F1;
                }}
                QPushButton:pressed {{
                    background-color: #1E7FD0;
                }}
            """)
            analyze_btn.setFixedWidth(200)
            analyze_btn.clicked.connect(self._on_analyze_click)
            layout.addWidget(analyze_btn, alignment=Qt.AlignmentFlag.AlignCenter)
            
            self.welcome_panel = panel
        
        return self.welcome_panel
    
    def _create_analysis_panel(self) -> QWidget:
        """Create analysis panel"""
        if self.analysis_panel is None:
            self.analysis_panel = AnalysisPanel()
            # Connect disk selection signal
            self.analysis_panel.disk_selected.connect(self._on_disk_selected)
        
        return self.analysis_panel
    
    def _create_explorer_panel(self) -> QWidget:
        """Create explorer panel"""
        if self.explorer_panel is None:
            self.explorer_panel = ExplorerPanel()
            # Connect back signal
            self.explorer_panel.back_requested.connect(self._on_explorer_back)
        
        return self.explorer_panel
    
    def _create_cleanup_panel(self) -> QWidget:
        """Create cleanup panel (placeholder)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        label = QLabel("Panel de Limpieza")
        label.setStyleSheet(f"""
            QLabel {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return panel
    
    def _create_settings_panel(self) -> QWidget:
        """Create settings panel (placeholder)"""
        panel = QWidget()
        layout = QVBoxLayout(panel)
        
        label = QLabel("Panel de Ajustes")
        label.setStyleSheet(f"""
            QLabel {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
        """)
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(label)
        
        return panel
    
    def _on_analyze_click(self):
        """Handle analyze button click"""
        # Navigate to analysis panel
        self._show_panel(PanelType.ANALYSIS)
    
    def _on_disk_selected(self, disk_info: DiskInfo):
        """Handle disk selection from analysis panel"""
        # Store selected disk
        self.selected_disk = disk_info
        
        # Navigate to explorer panel with selected disk
        print(f"Disk selected: {disk_info.letter} - {disk_info.name}")
        
        # Show explorer panel and set the disk
        self._show_panel(PanelType.EXPLORER)
        
        # Set the disk in explorer panel
        if self.explorer_panel:
            self.explorer_panel.set_disk(disk_info)
    
    def _on_explorer_back(self):
        """Handle back button from explorer panel"""
        # Return to analysis panel
        self._show_panel(PanelType.ANALYSIS)
    
    def _apply_styles(self):
        """Apply application-wide styles"""
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {AppConstants.COLOR_BACKGROUND};
            }}
            QWidget {{
                background-color: {AppConstants.COLOR_BACKGROUND};
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-family: {AppConstants.FONT_FAMILY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
            }}
        """)
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Save window size to config
        self.config.set('ui.window_width', self.width())
        self.config.set('ui.window_height', self.height())
        
        # Clean up workers in active panels
        if self.analysis_panel:
            self.analysis_panel._cleanup_workers()
        
        if self.explorer_panel:
            self.explorer_panel._cleanup_workers()
        
        super().closeEvent(event)
    
    def __del__(self):
        """Cleanup when window is destroyed"""
        # Clean up workers in active panels
        if self.analysis_panel:
            try:
                self.analysis_panel._cleanup_workers()
            except:
                pass
        
        if self.explorer_panel:
            try:
                self.explorer_panel._cleanup_workers()
            except:
                pass