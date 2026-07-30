"""
Test script for DiskMaster V2 components
Validates core functionality without GUI
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
current_dir = Path(__file__).parent.absolute()
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

def test_imports():
    """Test all module imports"""
    print("Testing imports...")
    
    try:
        from utils.constants import AppConstants, DiskStatus, Messages
        print("✓ utils.constants imported successfully")
    except Exception as e:
        print(f"✗ utils.constants import failed: {e}")
        return False
    
    try:
        from utils.formatters import SizeFormatter, PercentageFormatter
        print("✓ utils.formatters imported successfully")
    except Exception as e:
        print(f"✗ utils.formatters import failed: {e}")
        return False
    
    try:
        from utils.path_handler import PathHandler
        print("✓ utils.path_handler imported successfully")
    except Exception as e:
        print(f"✗ utils.path_handler import failed: {e}")
        return False
    
    try:
        from utils.async_worker import AsyncWorker
        print("✓ utils.async_worker imported successfully")
    except Exception as e:
        print(f"✗ utils.async_worker import failed: {e}")
        return False
    
    try:
        from core.disk_analyzer import DiskAnalyzer, DiskInfo
        print("✓ core.disk_analyzer imported successfully")
    except Exception as e:
        print(f"✗ core.disk_analyzer import failed: {e}")
        return False
    
    try:
        from core.security import SecurityValidator
        print("✓ core.security imported successfully")
    except Exception as e:
        print(f"✗ core.security import failed: {e}")
        return False
    
    try:
        from core.permissions import PermissionManager
        print("✓ core.permissions imported successfully")
    except Exception as e:
        print(f"✗ core.permissions import failed: {e}")
        return False
    
    try:
        from core.folder_scanner import FolderScanner
        print("✓ core.folder_scanner imported successfully")
    except Exception as e:
        print(f"✗ core.folder_scanner import failed: {e}")
        return False
    
    try:
        from config.app_config import ConfigManager
        print("✓ config.app_config imported successfully")
    except Exception as e:
        print(f"✗ config.app_config import failed: {e}")
        return False
    
    return True

def test_disk_analyzer():
    """Test disk analyzer functionality"""
    print("\nTesting disk analyzer...")
    
    try:
        from core.disk_analyzer import DiskAnalyzer
        
        analyzer = DiskAnalyzer()
        print("✓ DiskAnalyzer instance created")
        
        # Test disk detection
        print("Detecting disks...")
        disks = analyzer.detect_disks()
        
        print(f"✓ Detected {len(disks)} disk(s)")
        
        for disk in disks:
            print(f"  - {disk.letter}: {disk.name} ({disk.disk_type.value})")
            print(f"    Total: {disk.get_formatted_total()}")
            print(f"    Used: {disk.get_formatted_used()}")
            print(f"    Free: {disk.get_formatted_free()}")
            print(f"    Usage: {disk.get_usage_percentage():.1f}%")
            print(f"    Status: {disk.status.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Disk analyzer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_security():
    """Test security validation"""
    print("\nTesting security validation...")
    
    try:
        from core.security import SecurityValidator
        from pathlib import Path
        
        validator = SecurityValidator()
        print("✓ SecurityValidator instance created")
        
        # Test safe path
        user_profile = Path.home()
        validation = validator.validate_path(user_profile)
        print(f"✓ User profile validation: {validation.security_level.value}")
        
        # Test unsafe path
        windows_path = Path("C:\\Windows")
        validation = validator.validate_path(windows_path)
        print(f"✓ Windows path validation: {validation.security_level.value}")
        
        return True
        
    except Exception as e:
        print(f"✗ Security validation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_permissions():
    """Test permission management"""
    print("\nTesting permission management...")
    
    try:
        from core.permissions import PermissionManager
        
        perm_manager = PermissionManager()
        print("✓ PermissionManager instance created")
        
        print(f"  Privilege level: {perm_manager.get_privilege_level().value}")
        print(f"  Is admin: {perm_manager.is_admin()}")
        print(f"  Is elevated: {perm_manager.is_elevated()}")
        
        return True
        
    except Exception as e:
        print(f"✗ Permission management test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_formatters():
    """Test data formatters"""
    print("\nTesting data formatters...")
    
    try:
        from utils.formatters import SizeFormatter, PercentageFormatter
        
        # Test size formatting
        sizes = [1024, 1024*1024, 1024*1024*1024, 1024*1024*1024*1024]
        for size in sizes:
            formatted = SizeFormatter.format_size(size)
            print(f"  {size} bytes = {formatted}")
        
        # Test percentage formatting
        percentages = [0, 50, 75, 100]
        for pct in percentages:
            formatted = PercentageFormatter.format_percentage(pct)
            bar = PercentageFormatter.format_bar(pct)
            print(f"  {pct}% = {formatted} |{bar}|")
        
        return True
        
    except Exception as e:
        print(f"✗ Formatters test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("DISKMASTER V2 - COMPONENT VALIDATION")
    print("=" * 60)
    
    results = []
    
    # Test imports
    results.append(("Imports", test_imports()))
    
    # Test formatters
    results.append(("Formatters", test_formatters()))
    
    # Test disk analyzer
    results.append(("Disk Analyzer", test_disk_analyzer()))
    
    # Test security
    results.append(("Security", test_security()))
    
    # Test permissions
    results.append(("Permissions", test_permissions()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:20s}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == '__main__':
    sys.exit(main())