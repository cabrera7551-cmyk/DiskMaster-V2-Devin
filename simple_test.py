"""
Simple test for DiskMaster V2 core functionality
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

print("Testing imports...")

try:
    from utils.constants import AppConstants, DiskStatus, Messages
    print("[OK] utils.constants imported successfully")
except Exception as e:
    print(f"[FAIL] utils.constants import failed: {e}")
    sys.exit(1)

try:
    from utils.formatters import SizeFormatter, PercentageFormatter
    print("[OK] utils.formatters imported successfully")
except Exception as e:
    print(f"[FAIL] utils.formatters import failed: {e}")
    sys.exit(1)

try:
    from utils.path_handler import PathHandler
    print("[OK] utils.path_handler imported successfully")
except Exception as e:
    print(f"[FAIL] utils.path_handler import failed: {e}")
    sys.exit(1)

try:
    from utils.async_worker import AsyncWorker
    print("[OK] utils.async_worker imported successfully")
except Exception as e:
    print(f"[FAIL] utils.async_worker import failed: {e}")
    sys.exit(1)

try:
    from core.disk_analyzer import DiskAnalyzer, DiskInfo
    print("[OK] core.disk_analyzer imported successfully")
except Exception as e:
    print(f"[FAIL] core.disk_analyzer import failed: {e}")
    sys.exit(1)

try:
    from core.security import SecurityValidator
    print("[OK] core.security imported successfully")
except Exception as e:
    print(f"[FAIL] core.security import failed: {e}")
    sys.exit(1)

try:
    from core.permissions import PermissionManager
    print("[OK] core.permissions imported successfully")
except Exception as e:
    print(f"[FAIL] core.permissions import failed: {e}")
    sys.exit(1)

try:
    from core.folder_scanner import FolderScanner
    print("[OK] core.folder_scanner imported successfully")
except Exception as e:
    print(f"[FAIL] core.folder_scanner import failed: {e}")
    sys.exit(1)

try:
    from config.app_config import ConfigManager
    print("[OK] config.app_config imported successfully")
except Exception as e:
    print(f"[FAIL] config.app_config import failed: {e}")
    sys.exit(1)

print("\nAll imports successful!")

print("\nTesting disk analyzer...")
try:
    from core.disk_analyzer import DiskAnalyzer
    
    analyzer = DiskAnalyzer()
    print("[OK] DiskAnalyzer instance created")
    
    # Test disk detection
    print("Detecting disks...")
    disks = analyzer.detect_disks()
    
    print(f"[OK] Detected {len(disks)} disk(s)")
    
    for disk in disks:
        print(f"  - {disk.letter}: {disk.name} ({disk.disk_type.value})")
        print(f"    Total: {disk.get_formatted_total()}")
        print(f"    Used: {disk.get_formatted_used()}")
        print(f"    Free: {disk.get_formatted_free()}")
        print(f"    Usage: {disk.get_usage_percentage():.1f}%")
        print(f"    Status: {disk.status.value}")
    
except Exception as e:
    print(f"[FAIL] Disk analyzer test failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n[OK] All tests passed!")