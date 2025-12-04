"""
Cleaner tab - System cleaning interface
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QCheckBox, QProgressBar,
                             QPlainTextEdit, QMessageBox)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.cleaner import SystemCleaner
from utils.config import get_config
from utils.logger import get_logger



class CleaningThread(QThread):
    """Background thread for cleaning operations"""
    progress = pyqtSignal(str)
    finished = pyqtSignal(dict)
    
    def __init__(self, options, analyze_only=False):
        super().__init__()
        self.options = options
        self.analyze_only = analyze_only
    
    def run(self):
        """Run cleaning operation"""
        cleaner = SystemCleaner()
        
        if not self.analyze_only:
            results = cleaner.clean_all(self.options)
            stats = cleaner.get_total_statistics()
            self.finished.emit(stats)
        else:
            # Just analyze, don't clean
            self.progress.emit("Analyzing system...")
            self.finished.emit({'analyzed': True})


class CleanerTab(QWidget):
    """System cleaner tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.logger = get_logger()
        self.cleaning_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = QLabel("System Cleaner")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # Options Group
        options_group = QGroupBox("Cleaning Options")
        options_layout = QVBoxLayout()
        options_group.setLayout(options_layout)
        
        self.temp_files_cb = QCheckBox("Temporary Files")
        self.temp_files_cb.setChecked(self.config.get('cleaning.temp_files', True))
        options_layout.addWidget(self.temp_files_cb)
        
        self.browser_cache_cb = QCheckBox("Browser Cache")
        self.browser_cache_cb.setChecked(self.config.get('cleaning.browser_cache', True))
        options_layout.addWidget(self.browser_cache_cb)
        
        self.recycle_bin_cb = QCheckBox("Recycle Bin")
        self.recycle_bin_cb.setChecked(self.config.get('cleaning.recycle_bin', False))
        options_layout.addWidget(self.recycle_bin_cb)
        
        self.recent_files_cb = QCheckBox("Recent Files")
        self.recent_files_cb.setChecked(self.config.get('cleaning.recent_files', True))
        options_layout.addWidget(self.recent_files_cb)
        
        self.log_files_cb = QCheckBox("Windows Log Files")
        self.log_files_cb.setChecked(self.config.get('cleaning.log_files', True))
        options_layout.addWidget(self.log_files_cb)
        
        layout.addWidget(options_group)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Log output
        log_group = QGroupBox("Log")
        log_layout = QVBoxLayout()
        log_group.setLayout(log_layout)
        
        self.log_text = QPlainTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        self.analyze_btn = QPushButton("🔍 Analyze")
        self.analyze_btn.clicked.connect(self.analyze)
        button_layout.addWidget(self.analyze_btn)
        
        self.clean_btn = QPushButton("🧹 Clean")
        self.clean_btn.setObjectName("dangerButton")
        self.clean_btn.clicked.connect(self.clean)
        button_layout.addWidget(self.clean_btn)
        
        layout.addLayout(button_layout)
    
    def get_options(self):
        """Get selected cleaning options"""
        return {
            'temp_files': self.temp_files_cb.isChecked(),
            'browser_cache': self.browser_cache_cb.isChecked(),
            'recycle_bin': self.recycle_bin_cb.isChecked(),
            'recent_files': self.recent_files_cb.isChecked(),
            'log_files': self.log_files_cb.isChecked()
        }
    
    def analyze(self):
        """Analyze system without cleaning"""
        self.log_text.appendPlainText("Starting analysis...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate
        
        options = self.get_options()
        self.cleaning_thread = CleaningThread(options, analyze_only=True)
        self.cleaning_thread.finished.connect(self.on_analyze_finished)
        self.cleaning_thread.start()
    
    def clean(self):
        """Perform cleaning operation"""
        reply = QMessageBox.question(
            self,
            "Confirm Cleaning",
            "Are you sure you want to clean the selected items?\n"
            "This operation cannot be undone.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.log_text.clear()
            self.log_text.appendPlainText("Starting cleaning operation...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)
            
            self.analyze_btn.setEnabled(False)
            self.clean_btn.setEnabled(False)
            
            options = self.get_options()
            self.cleaning_thread = CleaningThread(options, analyze_only=False)
            self.cleaning_thread.finished.connect(self.on_clean_finished)
            self.cleaning_thread.start()
    
    def on_analyze_finished(self, stats):
        """Handle analyze completion"""
        self.progress_bar.setVisible(False)
        self.log_text.appendPlainText("Analysis complete!")
    
    def on_clean_finished(self, stats):
        """Handle cleaning completion"""
        self.progress_bar.setVisible(False)
        self.analyze_btn.setEnabled(True)
        self.clean_btn.setEnabled(True)
        
        self.log_text.appendPlainText(f"\nCleaning complete!")
        self.log_text.appendPlainText(f"Files removed: {stats.get('total_files_removed', 0)}")
        self.log_text.appendPlainText(f"Space freed: {stats.get('total_space_formatted', '0 B')}")
        
        self.logger.log_operation(
            "System Cleaning",
            f"Freed {stats.get('total_space_formatted', '0 B')}",
            success=True
        )
        
        QMessageBox.information(
            self,
            "Cleaning Complete",
            f"Successfully cleaned {stats.get('total_files_removed', 0)} files\n"
            f"Space freed: {stats.get('total_space_formatted', '0 B')}"
        )
