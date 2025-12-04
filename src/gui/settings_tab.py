"""
Settings tab - Application configuration
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QCheckBox, QSpinBox,
                             QMessageBox)
from PyQt5.QtCore import Qt
from utils.config import get_config
from utils.logger import get_logger



class SettingsTab(QWidget):
    """Settings and configuration tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.logger = get_logger()
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = QLabel("Settings")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # Cleaning Settings
        cleaning_group = QGroupBox("Default Cleaning Options")
        cleaning_layout = QVBoxLayout()
        cleaning_group.setLayout(cleaning_layout)
        
        self.temp_files_cb = QCheckBox("Clean Temporary Files")
        self.temp_files_cb.setChecked(self.config.get('cleaning.temp_files', True))
        cleaning_layout.addWidget(self.temp_files_cb)
        
        self.browser_cache_cb = QCheckBox("Clean Browser Cache")
        self.browser_cache_cb.setChecked(self.config.get('cleaning.browser_cache', True))
        cleaning_layout.addWidget(self.browser_cache_cb)
        
        self.recycle_bin_cb = QCheckBox("Empty Recycle Bin")
        self.recycle_bin_cb.setChecked(self.config.get('cleaning.recycle_bin', False))
        cleaning_layout.addWidget(self.recycle_bin_cb)
        
        layout.addWidget(cleaning_group)
        
        # Security Settings
        security_group = QGroupBox("Security Settings")
        security_layout = QVBoxLayout()
        security_group.setLayout(security_layout)
        
        passes_layout = QHBoxLayout()
        passes_layout.addWidget(QLabel("Secure Delete Passes:"))
        self.passes_spin = QSpinBox()
        self.passes_spin.setMinimum(1)
        self.passes_spin.setMaximum(35)
        self.passes_spin.setValue(self.config.get('security.secure_delete_passes', 3))
        passes_layout.addWidget(self.passes_spin)
        passes_layout.addStretch()
        security_layout.addLayout(passes_layout)
        
        self.backup_registry_cb = QCheckBox("Backup Registry Before Cleaning")
        self.backup_registry_cb.setChecked(self.config.get('security.backup_registry', True))
        security_layout.addWidget(self.backup_registry_cb)
        
        layout.addWidget(security_group)
        
        # Software Settings
        software_group = QGroupBox("Software Manager Settings")
        software_layout = QVBoxLayout()
        software_group.setLayout(software_layout)
        
        threshold_layout = QHBoxLayout()
        threshold_layout.addWidget(QLabel("Unused Threshold (days):"))
        self.threshold_spin = QSpinBox()
        self.threshold_spin.setMinimum(1)
        self.threshold_spin.setMaximum(365)
        self.threshold_spin.setValue(self.config.get('software.unused_threshold_days', 90))
        threshold_layout.addWidget(self.threshold_spin)
        threshold_layout.addStretch()
        software_layout.addLayout(threshold_layout)
        
        self.show_system_cb = QCheckBox("Show System Software")
        self.show_system_cb.setChecked(self.config.get('software.show_system_software', False))
        software_layout.addWidget(self.show_system_cb)
        
        layout.addWidget(software_group)
        
        layout.addStretch()
        
        # Action buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("💾 Save Settings")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("🔄 Reset to Defaults")
        reset_btn.setObjectName("secondaryButton")
        reset_btn.clicked.connect(self.reset_settings)
        button_layout.addWidget(reset_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
    
    def save_settings(self):
        """Save settings to configuration"""
        # Cleaning settings
        self.config.set('cleaning.temp_files', self.temp_files_cb.isChecked())
        self.config.set('cleaning.browser_cache', self.browser_cache_cb.isChecked())
        self.config.set('cleaning.recycle_bin', self.recycle_bin_cb.isChecked())
        
        # Security settings
        self.config.set('security.secure_delete_passes', self.passes_spin.value())
        self.config.set('security.backup_registry', self.backup_registry_cb.isChecked())
        
        # Software settings
        self.config.set('software.unused_threshold_days', self.threshold_spin.value())
        self.config.set('software.show_system_software', self.show_system_cb.isChecked())
        
        # Save to file
        self.config.save()
        
        self.logger.info("Settings saved")
        QMessageBox.information(self, "Settings Saved", "Your settings have been saved successfully")
    
    def reset_settings(self):
        """Reset settings to defaults"""
        reply = QMessageBox.question(
            self,
            "Reset Settings",
            "Are you sure you want to reset all settings to defaults?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config.reset_to_defaults()
            
            # Update UI
            self.temp_files_cb.setChecked(self.config.get('cleaning.temp_files'))
            self.browser_cache_cb.setChecked(self.config.get('cleaning.browser_cache'))
            self.recycle_bin_cb.setChecked(self.config.get('cleaning.recycle_bin'))
            self.passes_spin.setValue(self.config.get('security.secure_delete_passes'))
            self.backup_registry_cb.setChecked(self.config.get('security.backup_registry'))
            self.threshold_spin.setValue(self.config.get('software.unused_threshold_days'))
            self.show_system_cb.setChecked(self.config.get('software.show_system_software'))
            
            self.logger.info("Settings reset to defaults")
            QMessageBox.information(self, "Settings Reset", "Settings have been reset to defaults")
