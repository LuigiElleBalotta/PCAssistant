"""
Main application window
"""
from PyQt5.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, 
                             QMenuBar, QAction, QMessageBox, QWidget, QVBoxLayout)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QIcon
import os

from gui.dashboard_tab import DashboardTab
from gui.cleaner_tab import CleanerTab
from gui.tools_tab import ToolsTab
from gui.optimizer_tab import OptimizerTab
from gui.settings_tab import SettingsTab
from utils.config import get_config
from utils.logger import get_logger
from utils.admin import check_admin_and_warn



class MainWindow(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.config = get_config()
        self.logger = get_logger()
        
        self.init_ui()
        self.check_admin_status()
    
    def init_ui(self):
        """Initialize user interface"""
        self.setWindowTitle("PC Assistant - System Cleaner & Optimizer")
        self.setGeometry(100, 100, 1200, 800)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Create main layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Create tabs
        self.dashboard_tab = DashboardTab(self)
        self.cleaner_tab = CleanerTab(self)
        self.tools_tab = ToolsTab(self)
        self.optimizer_tab = OptimizerTab(self)
        self.settings_tab = SettingsTab(self)
        
        # Add tabs
        self.tabs.addTab(self.dashboard_tab, "📊 Dashboard")
        self.tabs.addTab(self.cleaner_tab, "🧹 Cleaner")
        self.tabs.addTab(self.tools_tab, "🔧 Tools")
        self.tabs.addTab(self.optimizer_tab, "🚀 Optimizer")
        self.tabs.addTab(self.settings_tab, "⚙️ Settings")
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Update status bar periodically
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_status_bar)
        self.status_timer.start(2000)  # Update every 2 seconds
        
        self.logger.info("Main window initialized")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("&File")
        
        exit_action = QAction("&Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("&Tools")
        
        analyze_action = QAction("&Quick Analyze", self)
        analyze_action.triggered.connect(self.quick_analyze)
        tools_menu.addAction(analyze_action)
        
        # Help menu
        help_menu = menubar.addMenu("&Help")
        
        about_action = QAction("&About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def check_admin_status(self):
        """Check if running with admin privileges"""
        warning = check_admin_and_warn()
        if warning:
            QMessageBox.warning(
                self,
                "Privilegi Amministratore",
                warning,
                QMessageBox.Ok
            )
            self.status_bar.showMessage("⚠️ Non in esecuzione come amministratore")
    
    def update_status_bar(self):
        """Update status bar with system info"""
        from core.optimizer import SystemOptimizer
        
        try:
            optimizer = SystemOptimizer()
            stats = optimizer.get_system_resources()
            
            status_text = (
                f"CPU: {stats.cpu_percent:.1f}% | "
                f"RAM: {stats.memory_percent:.1f}% | "
                f"Disk: {stats.disk_percent:.1f}%"
            )
            self.status_bar.showMessage(status_text)
        except Exception as e:
            self.logger.error(f"Error updating status bar: {e}")

    
    def quick_analyze(self):
        """Quick system analyze"""
        self.tabs.setCurrentWidget(self.cleaner_tab)
        self.cleaner_tab.analyze()
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About PC Assistant",
            "<h2>PC Assistant</h2>"
            "<p>Advanced System Cleaner & Optimizer</p>"
            "<p>Version 1.0</p>"
            "<p>Features:</p>"
            "<ul>"
            "<li>System cleaning</li>"
            "<li>Duplicate file detection</li>"
            "<li>Software management</li>"
            "<li>Registry optimization</li>"
            "<li>Startup management</li>"
            "</ul>"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        self.logger.info("Application closing")
        event.accept()
