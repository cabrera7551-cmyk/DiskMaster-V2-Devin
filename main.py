"""
DiskMaster V2 - Smart Storage Manager
Main entry point for the portable application
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    from ui.main_window import MainWindow
    from utils.path_handler import get_path_handler
    from config.app_config import get_config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print(f"Current directory: {current_dir}")
    print(f"Python path: {sys.path}")
    sys.exit(1)


def check_admin_privileges():
    """Check if application has administrator privileges"""
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def main():
    """Main application entry point"""
    try:
        # Initialize path handler
        path_handler = get_path_handler()
        print("Path handler initialized")
        
        # Initialize configuration
        config = get_config()
        print("Configuration initialized")
        
        # Create Qt Application
        app = QApplication(sys.argv)
        app.setApplicationName("DiskMaster V2")
        app.setApplicationVersion("2.0.0")
        app.setOrganizationName("DiskMaster Team")
        print("Qt Application created")
        
        # Enable High DPI scaling
        app.setHighDpiScaleFactorRoundingPolicy(
            Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
        )
        
        # Check admin privileges (log only, don't block)
        is_admin = check_admin_privileges()
        if is_admin:
            print("Running with administrator privileges")
        else:
            print("Running without administrator privileges (some features may be limited)")
        
        # Create and show main window
        window = MainWindow()
        print("Main window created")
        window.show()
        print("Main window shown")
        
        # Run application
        print("Starting application event loop")
        sys.exit(app.exec())
        
    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()