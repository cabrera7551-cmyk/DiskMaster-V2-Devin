"""
Test GUI components without showing the window
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Add parent directory to path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

print("Testing GUI components...")

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    print("[OK] PyQt6 imported successfully")
except Exception as e:
    print(f"[FAIL] PyQt6 import failed: {e}")
    sys.exit(1)

try:
    from ui.main_window import MainWindow
    print("[OK] MainWindow imported successfully")
except Exception as e:
    print(f"[FAIL] MainWindow import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ui.panels.analysis_panel import AnalysisPanel
    print("[OK] AnalysisPanel imported successfully")
except Exception as e:
    print(f"[FAIL] AnalysisPanel import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ui.components.disk_card import DiskCard
    print("[OK] DiskCard imported successfully")
except Exception as e:
    print(f"[FAIL] DiskCard import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nCreating QApplication...")
try:
    app = QApplication(sys.argv)
    app.setApplicationName("DiskMaster V2")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DiskMaster Team")
    print("[OK] QApplication created")
except Exception as e:
    print(f"[FAIL] QApplication creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nCreating MainWindow...")
try:
    window = MainWindow()
    print("[OK] MainWindow created")
except Exception as e:
    print(f"[FAIL] MainWindow creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nCreating AnalysisPanel...")
try:
    from ui.panels.analysis_panel import AnalysisPanel
    analysis_panel = AnalysisPanel()
    print("[OK] AnalysisPanel created")
except Exception as e:
    print(f"[FAIL] AnalysisPanel creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] All GUI components test passed!")
print("The application can be started with: python main.py")