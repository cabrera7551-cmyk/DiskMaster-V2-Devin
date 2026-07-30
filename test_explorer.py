"""
Test script for DiskMaster V2 explorer components
Validates explorer functionality without GUI
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

print("Testing explorer components...")

try:
    from ui.components.folder_item import FolderItem
    print("[OK] FolderItem imported successfully")
except Exception as e:
    print(f"[FAIL] FolderItem import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ui.components.file_item import FileItem
    print("[OK] FileItem imported successfully")
except Exception as e:
    print(f"[FAIL] FileItem import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ui.components.info_panel import InfoPanel
    print("[OK] InfoPanel imported successfully")
except Exception as e:
    print(f"[FAIL] InfoPanel import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

try:
    from ui.panels.explorer_panel import ExplorerPanel
    print("[OK] ExplorerPanel imported successfully")
except Exception as e:
    print(f"[FAIL] ExplorerPanel import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting GUI components with QApplication...")
try:
    from PyQt6.QtWidgets import QApplication
    from PyQt6.QtCore import Qt
    
    app = QApplication(sys.argv)
    app.setApplicationName("DiskMaster V2 Test")
    print("[OK] QApplication created")
except Exception as e:
    print(f"[FAIL] QApplication creation failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nCreating explorer components...")
try:
    from core.folder_scanner import FolderInfo, FileInfo
    from core.disk_analyzer import DiskInfo
    
    # Create test folder info
    test_folder_info = FolderInfo(
        path=Path("C:/Users/Test"),
        name="TestFolder",
        total_size=1024*1024*100,  # 100MB
        file_count=50,
        folder_count=5,
        is_hidden=False,
        is_system=False,
        contains_system_files=False,
        modified_time=1234567890.0,
        created_time=1234567890.0
    )
    
    folder_item = FolderItem(test_folder_info)
    print("[OK] FolderItem created with test data")
    
    # Create test file info
    test_file_info = FileInfo(
        path=Path("C:/Users/Test/test.txt"),
        name="test.txt",
        size=1024*10,  # 10KB
        extension=".txt",
        is_hidden=False,
        is_system=False,
        modified_time=1234567890.0,
        created_time=1234567890.0
    )
    
    file_item = FileItem(test_file_info)
    print("[OK] FileItem created with test data")
    
    # Create info panel
    info_panel = InfoPanel()
    print("[OK] InfoPanel created")
    
    # Test selection functionality
    info_panel.set_selected_items([test_folder_info, test_file_info])
    print("[OK] InfoPanel selection tested")
    
    # Create explorer panel
    explorer_panel = ExplorerPanel()
    print("[OK] ExplorerPanel created")
    
    # Test disk setting
    test_disk_info = DiskInfo(
        letter="C:",
        name="Test Disk",
        disk_type="SSD",
        total_space=1024*1024*1024*500,  # 500GB
        used_space=1024*1024*1024*250,  # 250GB
        free_space=1024*1024*1024*250,  # 250GB
        usage_percentage=50.0,
        file_system="NTFS",
        is_removable=False,
        is_system=True,
        mount_point="C:\\",
        status="Healthy"
    )
    
    explorer_panel.set_disk(test_disk_info)
    print("[OK] ExplorerPanel disk setting tested")
    
    # Clean up panel workers
    explorer_panel._cleanup_workers()
    print("[OK] ExplorerPanel workers cleaned up")
    
except Exception as e:
    print(f"[FAIL] Component creation test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting folder scanner integration...")
try:
    from core.folder_scanner import FolderScanner
    from pathlib import Path
    
    scanner = FolderScanner()
    print("[OK] FolderScanner instance created")
    
    # Test getting safe user folders
    safe_folders = scanner.security_validator.get_safe_user_folders()
    print(f"[OK] Found {len(safe_folders)} safe user folders")
    
    for folder in safe_folders[:3]:  # Show first 3
        print(f"  - {folder}")
    
except Exception as e:
    print(f"[FAIL] Folder scanner test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting security validation...")
try:
    from core.security import SecurityValidator
    
    validator = SecurityValidator()
    print("[OK] SecurityValidator instance created")
    
    # Test safe path
    user_profile = Path.home()
    validation = validator.validate_path(user_profile)
    print(f"[OK] User profile validation: {validation.security_level.value}")
    
    # Test unsafe path
    windows_path = Path("C:\\Windows")
    validation = validator.validate_path(windows_path)
    print(f"[OK] Windows path validation: {validation.security_level.value}")
    
except Exception as e:
    print(f"[FAIL] Security validation test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] All explorer component tests passed!")
print("The explorer functionality is ready for integration.")