"""
Build script for DiskMaster V2 Portable
Creates a directory-based portable application using PyInstaller
"""

import os
import sys
import shutil
from pathlib import Path


def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import PyInstaller
        print(f"✓ PyInstaller version: {PyInstaller.__version__}")
    except ImportError:
        print("✗ PyInstaller not found. Install with: pip install PyInstaller")
        return False
    
    try:
        import PyQt6
        print(f"✓ PyQt6 version: {PyQt6.QtCore.PYQT_VERSION_STR}")
    except ImportError:
        print("✗ PyQt6 not found. Install with: pip install PyQt6")
        return False
    
    try:
        import psutil
        print(f"✓ psutil version: {psutil.__version__}")
    except ImportError:
        print("✗ psutil not found. Install with: pip install psutil")
        return False
    
    return True


def prepare_build_directories():
    """Prepare directories for build"""
    base_dir = Path(__file__).parent
    
    # Create assets directory if it doesn't exist
    assets_dir = base_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create placeholder icon if none exists
    icon_file = assets_dir / "icon.ico"
    if not icon_file.exists():
        print("⚠ No icon.ico found in assets/ directory. Using default icon.")
    
    # Create config directory structure
    config_dir = base_dir / "config"
    config_dir.mkdir(exist_ok=True)
    
    # Create styles directory
    styles_dir = base_dir / "ui" / "styles"
    styles_dir.mkdir(parents=True, exist_ok=True)
    
    print("✓ Build directories prepared")
    return True


def clean_previous_builds():
    """Clean previous build artifacts"""
    base_dir = Path(__file__).parent
    
    # Directories to clean
    clean_dirs = [
        base_dir / "build",
        base_dir / "dist",
    ]
    
    for dir_path in clean_dirs:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"✓ Cleaned {dir_path.name}")
    
    # Clean spec file if it exists (we regenerate it)
    spec_file = base_dir / "build.spec"
    if spec_file.exists():
        # We keep our custom spec file
        pass


def build_portable():
    """Build portable application using PyInstaller"""
    import PyInstaller.__main__
    
    base_dir = Path(__file__).parent
    os.chdir(base_dir)
    
    print("\n🔨 Building DiskMaster V2 Portable...")
    
    PyInstaller.__main__.run([
        'build.spec',
        '--clean',
        '--noconfirm',
    ])
    
    print("\n✓ Build completed successfully!")
    return True


def create_portable_structure():
    """Create the final portable directory structure"""
    base_dir = Path(__file__).parent
    dist_dir = base_dir / "dist" / "DiskMaster V2 Portable"
    
    if not dist_dir.exists():
        print("✗ Build directory not found. Run build first.")
        return False
    
    # Create additional directories in the portable distribution
    additional_dirs = [
        dist_dir / "data",
        dist_dir / "logs",
    ]
    
    for dir_path in additional_dirs:
        dir_path.mkdir(exist_ok=True)
    
    # Create README.txt for the portable version
    readme_content = """DISKMASTER V2 - PORTABLE VERSION
============================

DiskMaster V2 is a professional storage management tool for Windows 10/11.

HOW TO USE:
1. Double-click DiskMasterV2.exe to run the application
2. No installation required - runs directly from this folder
3. Can be run from USB drive or local disk

REQUIREMENTS:
- Windows 10 or Windows 11
- Administrator privileges (recommended for full functionality)

DIRECTORY STRUCTURE:
- DiskMasterV2.exe - Main application executable
- config/ - Application configuration
- data/ - User data and cache
- logs/ - Application logs
- assets/ - Application resources

SUPPORT:
For issues and updates, visit the project repository.

VERSION: 2.0.0
"""
    
    readme_file = dist_dir / "README.txt"
    with open(readme_file, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("✓ Portable directory structure created")
    print(f"✓ Portable application ready in: {dist_dir}")
    return True


def main():
    """Main build process"""
    print("=" * 60)
    print("DISKMASTER V2 - PORTABLE BUILD SCRIPT")
    print("=" * 60)
    
    # Check dependencies
    print("\n📋 Checking dependencies...")
    if not check_dependencies():
        print("\n✗ Missing dependencies. Please install required packages.")
        sys.exit(1)
    
    # Prepare directories
    print("\n📁 Preparing build directories...")
    if not prepare_build_directories():
        print("\n✗ Failed to prepare directories.")
        sys.exit(1)
    
    # Clean previous builds
    print("\n🧹 Cleaning previous builds...")
    clean_previous_builds()
    
    # Build application
    if not build_portable():
        print("\n✗ Build failed.")
        sys.exit(1)
    
    # Create portable structure
    print("\n📦 Creating portable structure...")
    if not create_portable_structure():
        print("\n✗ Failed to create portable structure.")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✓ BUILD SUCCESSFUL!")
    print("=" * 60)
    print(f"\nPortable application is ready in:")
    print(f"  dist/DiskMaster V2 Portable/")
    print(f"\nYou can copy this entire folder to a USB drive or any location.")
    print("=" * 60)


if __name__ == '__main__':
    main()