"""
Constants for DiskMaster V2
Application-wide constants and configuration values
"""

from enum import Enum


class AppConstants:
    """Application constants"""
    
    # Application Info
    APP_NAME = "DiskMaster V2"
    APP_VERSION = "2.0.0"
    APP_TITLE = "DiskMaster V2 - Smart Storage Manager"
    APP_AUTHOR = "DiskMaster Team"
    
    # Window Settings
    WINDOW_MIN_WIDTH = 1200
    WINDOW_MIN_HEIGHT = 800
    WINDOW_DEFAULT_WIDTH = 1400
    WINDOW_DEFAULT_HEIGHT = 900
    
    # UI Settings
    SIDEBAR_WIDTH = 250
    INFO_PANEL_WIDTH = 300
    
    # Terminal Blackout Blue Color Scheme
    COLOR_BACKGROUND = "#000000"
    COLOR_ACCENT = "#2E8FE0"
    COLOR_TEXT_PRIMARY = "#FFFFFF"
    COLOR_TEXT_SECONDARY = "#888888"
    COLOR_BORDER = "#333333"
    COLOR_CARD_BACKGROUND = "#0A0A0A"
    COLOR_PROGRESS_BAR = "#2E8FE0"
    COLOR_PROGRESS_EMPTY = "#1A1A1A"
    COLOR_HOVER = "#1A1A3A"
    COLOR_SELECTED = "#2E8FE0"
    COLOR_DISABLED = "#444444"
    COLOR_SUCCESS = "#00FF00"
    COLOR_WARNING = "#FFAA00"
    COLOR_ERROR = "#FF0000"
    
    # Typography
    FONT_FAMILY = "Consolas"
    FONT_SIZE_SMALL = 9
    FONT_SIZE_NORMAL = 10
    FONT_SIZE_LARGE = 12
    FONT_SIZE_TITLE = 14
    FONT_SIZE_HEADER = 16
    
    # File Size Units
    SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    
    # Performance Settings
    SCAN_TIMEOUT = 30  # seconds
    CHUNK_SIZE = 8192  # bytes for file operations
    MAX_THREADS = 4
    
    # UI Refresh Rates
    UI_REFRESH_INTERVAL = 100  # milliseconds
    PROGRESS_UPDATE_INTERVAL = 200  # milliseconds


class ForbiddenFolders:
    """List of forbidden system folders"""
    
    FOLDERS = [
        'Windows',
        'Program Files',
        'Program Files (x86)',
        'Recovery',
        'PerfLogs',
        'System Volume Information',
        'Boot',
        'MSOCache',
        '$Recycle.Bin',
        'Config.Msi',
        '$SysReset',
        'System32',
        'Drivers'
    ]


class UserFolders:
    """Standard user folders to analyze"""
    
    STANDARD_FOLDERS = [
        'Desktop',
        'Documents',
        'Downloads',
        'Pictures',
        'Videos',
        'Music',
        'OneDrive',
        'Projects'
    ]
    
    # Alternative names (for different Windows languages)
    ALTERNATIVE_NAMES = {
        'Desktop': ['Escritorio', 'Desktop'],
        'Documents': ['Documentos', 'Documents'],
        'Downloads': ['Descargas', 'Downloads'],
        'Pictures': ['Imágenes', 'Pictures'],
        'Videos': ['Videos', 'Videos'],
        'Music': ['Música', 'Music']
    }


class DiskType(Enum):
    """Disk types"""
    SSD = "SSD"
    HDD = "HDD"
    NVME = "NVMe"
    SATA = "SATA"
    M2 = "M.2"
    USB = "USB"
    UNKNOWN = "Unknown"


class DiskStatus(Enum):
    """Disk status"""
    HEALTHY = "Healthy"
    WARNING = "Warning"
    CRITICAL = "Critical"
    OFFLINE = "Offline"


class PanelType(Enum):
    """UI Panel types"""
    WELCOME = "welcome"
    ANALYSIS = "analysis"
    EXPLORER = "explorer"
    CLEANUP = "cleanup"
    SETTINGS = "settings"


class FileOperation(Enum):
    """File operation types"""
    COPY = "copy"
    MOVE = "move"
    DELETE = "delete"
    ANALYZE = "analyze"


class ScanPriority(Enum):
    """Scan priority levels"""
    LOW = 1
    NORMAL = 2
    HIGH = 3


class AppConfig:
    """Default application configuration"""
    
    # Scan Settings
    SCAN_HIDDEN_FILES = False
    SCAN_SYSTEM_FILES = False
    SCAN_LARGE_FILES_THRESHOLD = 1024 * 1024 * 1024  # 1GB
    
    # UI Settings
    SHOW_FILE_SIZES = True
    SHOW_FOLDER_COUNTS = True
    COMPACT_MODE = False
    DARK_MODE = True
    
    # Performance Settings
    ENABLE_PARALLEL_SCANNING = True
    MAX_SCAN_THREADS = 4
    CACHE_RESULTS = True
    
    # Safety Settings
    CONFIRM_BEFORE_DELETE = True
    CONFIRM_BEFORE_MOVE = True
    SHOW_SYSTEM_FOLDERS = False
    SAFE_MODE = True
    
    # Logging Settings
    ENABLE_LOGGING = True
    LOG_LEVEL = "INFO"
    LOG_MAX_SIZE = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5


class Messages:
    """User-facing messages"""
    
    # Welcome Screen
    WELCOME_TITLE = "DISKMASTER V2"
    WELCOME_SUBTITLE = "Smart Storage Manager"
    NO_ANALYSIS = "No se ha realizado ningún análisis."
    ANALYZE_BUTTON = "ANALIZAR DISCOS"
    
    # Analysis
    ANALYZING = "Analizando discos..."
    CALCULATING_SIZE = "Calculando tamaño..."
    INDEXING_FILES = "Indexando archivos..."
    SCAN_COMPLETE = "Escaneo finalizado."
    
    # Disk Info
    CAPACITY = "Capacidad:"
    USED = "Usado:"
    FREE = "Libre:"
    USAGE = "Uso:"
    
    # File Operations
    MOVE_SELECTION = "MOVER SELECCIÓN"
    SELECT_ALL = "Seleccionar todo"
    DESELECT_ALL = "Deseleccionar todo"
    MOVE = "Mover"
    CANCEL = "Cancelar"
    CONFIRM = "Confirmar"
    
    # Info Panel
    NAME = "Nombre:"
    PATH = "Ruta:"
    SIZE = "Tamaño:"
    FILE_COUNT = "Cantidad de archivos:"
    FOLDER_COUNT = "Cantidad de carpetas:"
    DESTINATION = "Destino seleccionado:"
    
    # Errors
    ERROR_ACCESS_DENIED = "Acceso denegado"
    ERROR_FILE_NOT_FOUND = "Archivo no encontrado"
    ERROR_INSUFFICIENT_SPACE = "Espacio insuficiente"
    ERROR_OPERATION_FAILED = "Operación fallida"
    
    # Warnings
    WARNING_SYSTEM_FOLDER = "Carpeta del sistema - No se puede modificar"
    WARNING_LARGE_OPERATION = "Operación grande - Puede tardar varios minutos"


class KeyboardShortcuts:
    """Keyboard shortcuts"""
    
    NEW_SCAN = "Ctrl+N"
    REFRESH = "F5"
    SELECT_ALL = "Ctrl+A"
    DESELECT_ALL = "Ctrl+D"
    MOVE = "Ctrl+M"
    DELETE = "Del"
    PROPERTIES = "Alt+Enter"
    GO_BACK = "Alt+Left"
    GO_FORWARD = "Alt+Right"
    GO_UP = "Alt+Up"
    SETTINGS = "Ctrl+,"
    EXIT = "Ctrl+Q"