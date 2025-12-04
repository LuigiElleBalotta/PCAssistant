"""
Tools tab - Duplicate finder and software manager
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
                             QFileDialog, QMessageBox, QHeaderView, QTabWidget)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.duplicate_finder import DuplicateFinder
from core.software_manager import SoftwareManager
from utils.scanner import Scanner
from utils.logger import get_logger
import os



class DuplicateScanThread(QThread):
    """Thread for duplicate file scanning"""
    progress = pyqtSignal(str, int)
    finished = pyqtSignal(dict)
    
    def __init__(self, directories):
        super().__init__()
        self.directories = directories
    
    def run(self):
        """Run duplicate scan"""
        finder = DuplicateFinder(min_size=1024)  # 1KB minimum
        
        def callback(filepath, count):
            self.progress.emit(filepath, count)
        
        duplicates = finder.find_duplicates(self.directories, callback=callback)
        stats = finder.get_statistics()
        
        self.finished.emit({
            'duplicates': duplicates,
            'stats': stats
        })


class SoftwareScanThread(QThread):
    """Thread for software scanning"""
    finished = pyqtSignal(list)
    
    def run(self):
        """Run software scan"""
        manager = SoftwareManager(show_system_software=False)
        software_list = manager.get_installed_software()
        self.finished.emit(software_list)


class ToolsTab(QWidget):
    """Tools tab with duplicate finder and software manager"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.duplicates = {}
        self.software_list = []
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = QLabel("Advanced Tools")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # Create sub-tabs
        self.tool_tabs = QTabWidget()
        layout.addWidget(self.tool_tabs)
        
        # Duplicate Finder Tab
        dup_widget = self.create_duplicate_finder_tab()
        self.tool_tabs.addTab(dup_widget, "📁 Duplicate Files")
        
        # Software Manager Tab
        soft_widget = self.create_software_manager_tab()
        self.tool_tabs.addTab(soft_widget, "🗑️ Software Manager")
    
    def create_duplicate_finder_tab(self):
        """Create duplicate finder interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        select_dir_btn = QPushButton("📂 Select Directory")
        select_dir_btn.clicked.connect(self.select_directory)
        controls_layout.addWidget(select_dir_btn)
        
        scan_btn = QPushButton("🔍 Scan for Duplicates")
        scan_btn.clicked.connect(self.scan_duplicates)
        controls_layout.addWidget(scan_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Results table
        self.dup_table = QTableWidget()
        self.dup_table.setColumnCount(4)
        self.dup_table.setHorizontalHeaderLabels(["File Name", "Size", "Count", "Wasted Space"])
        self.dup_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.dup_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        delete_selected_btn = QPushButton("🗑️ Delete Selected")
        delete_selected_btn.setObjectName("dangerButton")
        delete_selected_btn.clicked.connect(self.delete_selected_duplicates)
        action_layout.addWidget(delete_selected_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        return widget
    
    def create_software_manager_tab(self):
        """Create software manager interface"""
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh List")
        refresh_btn.clicked.connect(self.refresh_software_list)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        layout.addLayout(controls_layout)
        
        # Software table
        self.software_table = QTableWidget()
        self.software_table.setColumnCount(4)
        self.software_table.setHorizontalHeaderLabels(["Name", "Version", "Size", "Publisher"])
        self.software_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        layout.addWidget(self.software_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        uninstall_btn = QPushButton("🗑️ Uninstall Selected")
        uninstall_btn.setObjectName("dangerButton")
        uninstall_btn.clicked.connect(self.uninstall_selected)
        action_layout.addWidget(uninstall_btn)
        
        action_layout.addStretch()
        layout.addLayout(action_layout)
        
        # Auto-refresh on tab show
        self.refresh_software_list()
        
        return widget
    
    def select_directory(self):
        """Select directory for duplicate scan"""
        directory = QFileDialog.getExistingDirectory(self, "Select Directory to Scan")
        if directory:
            self.scan_directory = directory
            QMessageBox.information(self, "Directory Selected", f"Will scan: {directory}")
    
    def scan_duplicates(self):
        """Scan for duplicate files"""
        if not hasattr(self, 'scan_directory'):
            self.scan_directory = "C:\\Users"
        
        self.dup_table.setRowCount(0)
        self.logger.info(f"Scanning for duplicates in {self.scan_directory}")
        
        self.scan_thread = DuplicateScanThread([self.scan_directory])
        self.scan_thread.finished.connect(self.on_duplicate_scan_finished)
        self.scan_thread.start()
    
    def on_duplicate_scan_finished(self, result):
        """Handle duplicate scan completion"""
        self.duplicates = result['duplicates']
        stats = result['stats']
        
        self.dup_table.setRowCount(len(self.duplicates))
        
        for row, (file_hash, group) in enumerate(self.duplicates.items()):
            # File name (first file in group)
            filename = os.path.basename(group.files[0].path)
            self.dup_table.setItem(row, 0, QTableWidgetItem(filename))
            
            # Size
            size_str = Scanner.format_size(group.files[0].size)
            self.dup_table.setItem(row, 1, QTableWidgetItem(size_str))
            
            # Count
            self.dup_table.setItem(row, 2, QTableWidgetItem(str(len(group.files))))
            
            # Wasted space
            wasted = Scanner.format_size(group.get_wasted_space())
            self.dup_table.setItem(row, 3, QTableWidgetItem(wasted))
        
        QMessageBox.information(
            self,
            "Scan Complete",
            f"Found {stats['total_groups']} groups of duplicates\n"
            f"Total duplicate files: {stats['total_duplicate_files']}\n"
            f"Wasted space: {stats['wasted_space_formatted']}"
        )
    
    def delete_selected_duplicates(self):
        """Delete selected duplicate files"""
        QMessageBox.information(self, "Feature", "Duplicate deletion will be implemented")
    
    def refresh_software_list(self):
        """Refresh installed software list"""
        self.software_table.setRowCount(0)
        self.logger.info("Scanning installed software")
        
        self.software_thread = SoftwareScanThread()
        self.software_thread.finished.connect(self.on_software_scan_finished)
        self.software_thread.start()
    
    def on_software_scan_finished(self, software_list):
        """Handle software scan completion"""
        self.software_list = software_list
        self.software_table.setRowCount(len(software_list))
        
        for row, software in enumerate(software_list):
            self.software_table.setItem(row, 0, QTableWidgetItem(software.name))
            self.software_table.setItem(row, 1, QTableWidgetItem(software.version))
            self.software_table.setItem(row, 2, QTableWidgetItem(software.get_size_formatted()))
            self.software_table.setItem(row, 3, QTableWidgetItem(software.publisher))
        
        self.logger.info(f"Found {len(software_list)} installed programs")
    
    def uninstall_selected(self):
        """Uninstall selected software"""
        selected_rows = set(item.row() for item in self.software_table.selectedItems())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select software to uninstall")
            return
        
        selected_software = [self.software_list[row] for row in selected_rows]
        
        reply = QMessageBox.question(
            self,
            "Confirm Uninstall",
            f"Are you sure you want to uninstall {len(selected_software)} program(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            manager = SoftwareManager()
            for software in selected_software:
                success = manager.uninstall_software(software)
                if success:
                    self.logger.info(f"Uninstalling: {software.name}")
                else:
                    self.logger.error(f"Failed to uninstall: {software.name}")
            
            QMessageBox.information(self, "Uninstall", "Uninstall commands executed")
            self.refresh_software_list()
