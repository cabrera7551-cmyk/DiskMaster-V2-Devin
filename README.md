# DiskMaster V2 - Smart Storage Manager

Professional portable storage management tool for Windows 10/11.

## 🌟 Features

- **Portable Application**: Runs without installation from USB drive or local disk
- **Multi-Disk Support**: Works with SSD, HDD, NVMe, SATA, and M.2 drives
- **Safe File Management**: Focus on personal files, protects system folders
- **Terminal-Style Interface**: Professional "Terminal Blackout Blue" design
- **Real-Time Analysis**: Dynamic disk detection and folder size calculation
- **Intelligent Navigation**: Custom file explorer with system folder filtering
- **Batch Operations**: Select and move multiple files and folders efficiently

## 🎯 System Requirements

- **Operating System**: Windows 10 or Windows 11
- **Architecture**: x64 (64-bit)
- **Privileges**: Administrator rights recommended (optional for basic functionality)
- **Disk Space**: 50 MB for application files
- **RAM**: 4 GB minimum, 8 GB recommended

## 📦 Portable Application Structure

```
DiskMaster V2 Portable/
├── DiskMasterV2.exe          # Main executable
├── config/                   # Configuration files
├── data/                     # User data and cache
├── assets/                   # Application resources
├── logs/                     # Application logs
└── README.txt                # Quick start guide
```

## 🚀 Quick Start

### Running the Application

1. **From USB Drive**:
   - Copy the entire "DiskMaster V2 Portable" folder to your USB drive
   - Double-click `DiskMasterV2.exe` to run
   - No installation required

2. **From Local Disk**:
   - Extract the portable folder to any location on your computer
   - Double-click `DiskMasterV2.exe` to run
   - Application will create config and data folders automatically

### First Launch

1. The application will start in "Welcome" mode
2. Click "ANALIZAR DISCOS" to detect all connected drives
3. Select a disk to analyze its personal folders
4. Navigate through folders and select files to move
5. Choose destination and confirm the operation

## 🔧 Development Setup

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd DiskMaster-V2-Devin
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
venv\Scripts\activate  # On Windows
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Running from Source

```bash
python main.py
```

### Building Portable Version

1. Ensure all dependencies are installed:
```bash
pip install -r requirements.txt
```

2. Run the build script:
```bash
python build.py
```

3. The portable application will be created in `dist/DiskMaster V2 Portable/`

4. Copy the entire folder to your desired location (USB drive, etc.)

## 🏗️ Project Structure

```
DiskMaster-V2-Devin/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── build.py                   # Build script for portable version
├── build.spec                 # PyInstaller configuration
├── README.md                  # This file
│
├── config/                    # Configuration management
│   ├── __init__.py
│   └── app_config.py         # Portable configuration handler
│
├── core/                      # Business logic (to be implemented)
│   ├── __init__.py
│   ├── disk_analyzer.py      # Disk detection and analysis
│   ├── folder_scanner.py     # Folder scanning functionality
│   ├── file_manager.py       # File operations
│   ├── security.py           # Security validations
│   └── permissions.py        # Admin privilege handling
│
├── ui/                        # User interface
│   ├── __init__.py
│   ├── main_window.py        # Main application window
│   ├── sidebar.py            # Navigation sidebar
│   ├── panels/               # Content panels
│   │   ├── __init__.py
│   │   ├── welcome_panel.py  # Welcome screen
│   │   ├── analysis_panel.py # Disk analysis display
│   │   ├── explorer_panel.py # File explorer
│   │   ├── cleanup_panel.py  # Cleanup tools
│   │   └── settings_panel.py # Application settings
│   ├── components/           # Reusable UI components
│   │   ├── __init__.py
│   │   ├── disk_card.py      # Disk information card
│   │   ├── folder_item.py    # Folder display item
│   │   ├── file_item.py      # File display item
│   │   ├── progress_bar.py   # Progress bar component
│   │   └── info_panel.py     # Information panel
│   └── styles/               # Stylesheets
│       ├── __init__.py
│       └── terminal_blackout.qss  # Main stylesheet
│
├── utils/                     # Utility modules
│   ├── __init__.py
│   ├── constants.py          # Application constants
│   ├── path_handler.py       # Portable path management
│   ├── formatters.py         # Data formatting utilities
│   ├── async_worker.py       # Async operation workers
│   └── data_manager.py       # Data persistence
│
├── data/                      # Runtime data (created automatically)
├── assets/                    # Application resources
└── logs/                      # Application logs (created automatically)
```

## 🎨 Design Philosophy

### Terminal Blackout Blue Style

- **Background**: Pure black (#000000)
- **Accent Color**: Professional blue (#2E8FE0)
- **Typography**: Monospace fonts (Consolas)
- **Components**: Dark cards with discrete borders
- **Progress**: Terminal-style progress bars
- **Layout**: Clean, minimal, professional

### User Experience Principles

1. **Safety First**: System folders are protected, personal files only
2. **No Installation**: True portable application
3. **Professional Feel**: Terminal-style interface for power users
4. **Efficient Operations**: Batch processing with real-time feedback
5. **Clear Information**: Always show what's happening

## 🔒 Security Features

- **System Folder Protection**: Cannot modify Windows, Program Files, etc.
- **User Profile Focus**: Only works with user's personal files
- **Confirmation Dialogs**: All destructive operations require confirmation
- **Permission Handling**: Smart admin privilege detection
- **Path Validation**: All paths are validated before operations

## 📊 Usage Workflow

1. **Launch Application**: Double-click the executable
2. **Analyze Disks**: Click "ANALIZAR DISCOS" to detect drives
3. **Select Disk**: Click on a disk card to explore its contents
4. **Navigate Folders**: Browse through personal folders only
5. **Select Items**: Choose files/folders to move
6. **Choose Destination**: Select target disk
7. **Confirm Operation**: Review details and confirm
8. **Monitor Progress**: Watch real-time progress indicators

## 🛠️ Technical Details

### Technology Stack

- **GUI Framework**: PyQt6
- **System Information**: psutil
- **Windows Integration**: pywin32
- **Build Tool**: PyInstaller
- **Language**: Python 3.10+

### Portable Architecture

- **Path Management**: Dynamic path detection for USB/local execution
- **Configuration Storage**: Local to application folder with AppData fallback
- **No Registry Entries**: Completely clean operation
- **No System Dependencies**: Self-contained executable
- **Permission Handling**: Automatic detection and elevation when needed

## 📝 Development Status

### ✅ Phase 1: Base Structure (Completed)
- Portable directory structure
- Path handling system
- Configuration management
- Basic UI framework
- Terminal Blackout Blue styling
- PyInstaller build configuration

### ✅ Phase 2: Core Functionality (Completed & Validated)
- Disk detection and analysis with psutil
- Dynamic disk card components
- Analysis panel with interactive UI
- Folder scanning and size calculation
- Security validations and path filtering
- Permission handling and admin detection
- Async workers for non-blocking operations
- Data formatting utilities
- Data persistence and caching system
- **Full validation completed - all tests passing**

### 📋 Phase 3: Advanced Features (Part 1 Completed)
- File explorer implementation ✅
- Navigation by disk (C:, D:, etc.) ✅
- Folder and file display ✅
- Size calculation and formatting ✅
- Multi-selection system ✅
- Select all/deselect all ✅
- New folder creation ✅
- Thread-safe operations ✅
- Resource cleanup ✅

### 📋 Phase 3: Advanced Features (Part 2 Pending)
- File move operations
- Movement preview system
- User confirmation dialogs
- Operation logging system
- Backup system
- Rollback on error
- Critical folder blocking
- Progress tracking
- Error handling

### 🔮 Phase 4: Enhancement (Future)
- Cleanup tools
- Settings panel
- Additional analysis features
- Performance optimization

## 🤝 Contributing

This is a professional tool for Windows users. Development follows modular principles with clean architecture.

## 📄 License

[License information to be added]

## 🆘 Support

For issues, questions, or suggestions:
- Check the documentation
- Review the troubleshooting guide
- Contact the development team

## 🔮 Future Enhancements

- Additional disk analysis features
- File duplicate detection
- Temporary file cleanup
- Disk health monitoring
- Network drive support
- Cloud storage integration

---

**Version**: 2.0.0  
**Status**: Development Phase  
**Platform**: Windows 10/11 x64  
**Type**: Portable Application
