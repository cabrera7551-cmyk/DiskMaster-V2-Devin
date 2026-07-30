"""
Analysis Panel for DiskMaster V2
Displays disk analysis results with interactive disk cards
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QScrollArea,
    QLabel, QPushButton, QFrame, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont
from typing import List

from utils.constants import AppConstants, Messages
from utils.async_worker import AsyncWorker
from core.disk_analyzer import DiskAnalyzer, DiskInfo
from ui.components.disk_card import DiskCard


class AnalysisPanel(QWidget):
    """
    Panel for displaying disk analysis results
    """
    
    disk_selected = pyqtSignal(object)  # Signal when disk is selected
    
    def __init__(self):
        super().__init__()
        
        self.disk_analyzer = DiskAnalyzer()
        self.disk_cards: List[DiskCard] = []
        self.selected_disk: DiskInfo = None
        self.is_analyzing = False
        self.active_workers: List[AsyncWorker] = []
        
        self._setup_ui()
        self._apply_styles()
    
    def _setup_ui(self):
        """Setup panel UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # Header
        header_layout = QHBoxLayout()
        
        title_label = QLabel("ANÁLISIS DE DISCOS")
        title_label.setObjectName("panel-title")
        title_label.setStyleSheet(f"""
            QLabel {{
                color: {AppConstants.COLOR_ACCENT};
                font-size: {AppConstants.FONT_SIZE_TITLE}px;
                font-weight: bold;
                font-family: {AppConstants.FONT_FAMILY};
            }}
        """)
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        # Refresh button
        self.refresh_button = QPushButton("ACTUALIZAR")
        self.refresh_button.setObjectName("secondary-button")
        self.refresh_button.clicked.connect(self._on_refresh)
        header_layout.addWidget(self.refresh_button)
        
        layout.addLayout(header_layout)
        
        # Status label
        self.status_label = QLabel("No se ha realizado ningún análisis.")
        self.status_label.setObjectName("status-label")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet(f"""
            QLabel {{
                color: {AppConstants.COLOR_TEXT_SECONDARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
                padding: 20px;
            }}
        """)
        layout.addWidget(self.status_label)
        
        # Analyze button (initial state)
        self.analyze_button = QPushButton("ANALIZAR DISCOS")
        self.analyze_button.setObjectName("analyze-button")
        self.analyze_button.setFixedWidth(200)
        self.analyze_button.clicked.connect(self._on_analyze)
        layout.addWidget(self.analyze_button, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Disk cards container (scrollable)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFrameShape(QFrame.Shape.NoFrame)
        self.scroll_area.setVisible(False)
        
        self.cards_container = QWidget()
        self.cards_layout = QGridLayout(self.cards_container)
        self.cards_layout.setSpacing(15)
        self.cards_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        self.scroll_area.setWidget(self.cards_container)
        layout.addWidget(self.scroll_area)
        
        # Summary section
        self.summary_frame = QFrame()
        self.summary_frame.setVisible(False)
        summary_layout = QVBoxLayout(self.summary_frame)
        
        summary_label = QLabel("RESUMEN DEL SISTEMA")
        summary_label.setStyleSheet(f"""
            QLabel {{
                color: {AppConstants.COLOR_ACCENT};
                font-size: {AppConstants.FONT_SIZE_LARGE}px;
                font-weight: bold;
                font-family: {AppConstants.FONT_FAMILY};
            }}
        """)
        summary_layout.addWidget(summary_label)
        
        self.summary_info = QLabel()
        self.summary_info.setObjectName("summary-info")
        self.summary_info.setStyleSheet(f"""
            QLabel {{
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
            }}
        """)
        summary_layout.addWidget(self.summary_info)
        
        layout.addWidget(self.summary_frame)
    
    def _apply_styles(self):
        """Apply panel styles"""
        self.setStyleSheet(f"""
            QWidget {{
                background-color: {AppConstants.COLOR_BACKGROUND};
            }}
            QPushButton#analyze-button {{
                background-color: {AppConstants.COLOR_ACCENT};
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                border: none;
                padding: 15px 30px;
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
                font-weight: bold;
                border-radius: 2px;
            }}
            QPushButton#analyze-button:hover {{
                background-color: #3EA3F1;
            }}
            QPushButton#analyze-button:pressed {{
                background-color: #1E7FD0;
            }}
            QPushButton#analyze-button:disabled {{
                background-color: {AppConstants.COLOR_DISABLED};
                color: {AppConstants.COLOR_TEXT_SECONDARY};
            }}
            QPushButton#secondary-button {{
                background-color: {AppConstants.COLOR_BORDER};
                color: {AppConstants.COLOR_TEXT_PRIMARY};
                border: none;
                padding: 8px 16px;
                font-size: {AppConstants.FONT_SIZE_NORMAL}px;
                font-family: {AppConstants.FONT_FAMILY};
                border-radius: 2px;
            }}
            QPushButton#secondary-button:hover {{
                background-color: {AppConstants.COLOR_HOVER};
            }}
            QScrollArea {{
                background-color: {AppConstants.COLOR_BACKGROUND};
                border: none;
            }}
        """)
    
    def _on_analyze(self):
        """Handle analyze button click"""
        if self.is_analyzing:
            return
        
        self._start_analysis()
    
    def _on_refresh(self):
        """Handle refresh button click"""
        if self.is_analyzing:
            return
        
        self._start_analysis()
    
    def _start_analysis(self):
        """Start disk analysis"""
        self.is_analyzing = True
        self.analyze_button.setEnabled(False)
        self.refresh_button.setEnabled(False)
        self.status_label.setText(Messages.ANALYZING)
        
        # Cancel any existing workers
        self._cleanup_workers()
        
        # Create async worker for disk analysis
        worker = AsyncWorker(
            self.disk_analyzer.detect_disks,
            progress_callback=self._on_analysis_progress
        )
        
        worker.signals.progress.connect(self._on_analysis_progress)
        worker.signals.finished.connect(self._on_analysis_complete)
        worker.signals.error.connect(self._on_analysis_error)
        
        # Track worker for cleanup
        self.active_workers.append(worker)
        
        worker.start()
    
    def _on_analysis_progress(self, percentage: int, message: str):
        """Handle analysis progress updates"""
        self.status_label.setText(f"{message} ({percentage}%)")
    
    def _on_analysis_complete(self, disks: List[DiskInfo]):
        """Handle analysis completion"""
        self.is_analyzing = False
        self.analyze_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        
        if not disks:
            self.status_label.setText("No se detectaron discos.")
            return
        
        # Update UI with results
        self.status_label.setText(Messages.SCAN_COMPLETE)
        self.status_label.setVisible(False)
        self.analyze_button.setVisible(False)
        self.scroll_area.setVisible(True)
        self.summary_frame.setVisible(True)
        
        # Clear existing cards
        self._clear_disk_cards()
        
        # Create disk cards
        self._create_disk_cards(disks)
        
        # Update summary
        self._update_summary(disks)
    
    def _on_analysis_error(self, error_message: str):
        """Handle analysis error"""
        self.is_analyzing = False
        self.analyze_button.setEnabled(True)
        self.refresh_button.setEnabled(True)
        
        self.status_label.setText(f"Error: {error_message}")
    
    def _create_disk_cards(self, disks: List[DiskInfo]):
        """Create disk cards for detected disks"""
        row = 0
        col = 0
        max_cols = 3  # Number of cards per row
        
        for disk_info in disks:
            disk_card = DiskCard(disk_info)
            disk_card.clicked.connect(self._on_disk_selected)
            
            self.cards_layout.addWidget(disk_card, row, col)
            self.disk_cards.append(disk_card)
            
            col += 1
            if col >= max_cols:
                col = 0
                row += 1
    
    def _clear_disk_cards(self):
        """Clear existing disk cards"""
        for card in self.disk_cards:
            card.deleteLater()
        
        self.disk_cards.clear()
        self.selected_disk = None
    
    def _on_disk_selected(self, disk_info: DiskInfo):
        """Handle disk card selection"""
        # Deselect all cards
        for card in self.disk_cards:
            card.set_selected(False)
        
        # Find and select the clicked card
        for card in self.disk_cards:
            if card.disk_info == disk_info:
                card.set_selected(True)
                self.selected_disk = disk_info
                break
        
        # Emit signal
        self.disk_selected.emit(disk_info)
    
    def _update_summary(self, disks: List[DiskInfo]):
        """Update system summary information"""
        total_capacity = sum(disk.total_space for disk in disks)
        total_used = sum(disk.used_space for disk in disks)
        total_free = sum(disk.free_space for disk in disks)
        critical_disks = len([d for d in disks if d.status.value == "critical"])
        warning_disks = len([d for d in disks if d.status.value == "warning"])
        
        from utils.formatters import SizeFormatter, NumberFormatter
        
        summary_text = f"""
Discos detectados: {len(disks)}
Capacidad total: {SizeFormatter.format_size(total_capacity)}
Espacio usado: {SizeFormatter.format_size(total_used)}
Espacio libre: {SizeFormatter.format_size(total_free)}
Discos críticos: {critical_disks}
Discos con advertencia: {warning_disks}
        """.strip()
        
        self.summary_info.setText(summary_text)
    
    def reset_panel(self):
        """Reset panel to initial state"""
        self._clear_disk_cards()
        self.status_label.setVisible(True)
        self.status_label.setText("No se ha realizado ningún análisis.")
        self.analyze_button.setVisible(True)
        self.scroll_area.setVisible(False)
        self.summary_frame.setVisible(False)
        self.selected_disk = None
    
    def get_selected_disk(self) -> DiskInfo:
        """Get currently selected disk"""
        return self.selected_disk
    
    def refresh_selected_disk(self):
        """Refresh information for selected disk"""
        if self.selected_disk:
            updated_disk = self.disk_analyzer.refresh_disk_info(self.selected_disk.letter)
            if updated_disk:
                # Update the corresponding card
                for card in self.disk_cards:
                    if card.disk_info.letter == updated_disk.letter:
                        card.update_disk_info(updated_disk)
                        break
    
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