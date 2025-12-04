"""
Optimizer tab - Startup programs and resource monitoring
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
                             QMessageBox, QHeaderView)
from PyQt5.QtCore import Qt, QTimer
from core.optimizer import SystemOptimizer
from utils.logger import get_logger



class OptimizerTab(QWidget):
    """System optimizer tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = get_logger()
        self.optimizer = SystemOptimizer()
        self.startup_items = []
        self.init_ui()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.update_resources)
        self.refresh_timer.start(2000)  # Update every 2 seconds
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = QLabel("System Optimizer")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # Resource Monitor Group
        resource_group = QGroupBox("Resource Monitor")
        resource_layout = QVBoxLayout()
        resource_group.setLayout(resource_layout)
        
        self.cpu_label = QLabel("CPU: --")
        self.memory_label = QLabel("Memory: --")
        self.disk_label = QLabel("Disk: --")
        
        resource_layout.addWidget(self.cpu_label)
        resource_layout.addWidget(self.memory_label)
        resource_layout.addWidget(self.disk_label)
        
        layout.addWidget(resource_group)
        
        # Startup Programs Group
        startup_group = QGroupBox("Startup Programs")
        startup_layout = QVBoxLayout()
        startup_group.setLayout(startup_layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh")
        refresh_btn.clicked.connect(self.refresh_startup_programs)
        controls_layout.addWidget(refresh_btn)
        
        controls_layout.addStretch()
        startup_layout.addLayout(controls_layout)
        
        # Startup table
        self.startup_table = QTableWidget()
        self.startup_table.setColumnCount(3)
        self.startup_table.setHorizontalHeaderLabels(["Name", "Command", "Location"])
        self.startup_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        startup_layout.addWidget(self.startup_table)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        disable_btn = QPushButton("🚫 Disable Selected")
        disable_btn.setObjectName("dangerButton")
        disable_btn.clicked.connect(self.disable_selected)
        action_layout.addWidget(disable_btn)
        
        action_layout.addStretch()
        startup_layout.addLayout(action_layout)
        
        layout.addWidget(startup_group)
        
        # Initial load
        self.refresh_startup_programs()
        self.update_resources()
    
    def update_resources(self):
        """Update resource statistics"""
        try:
            stats = self.optimizer.get_system_resources()
            
            self.cpu_label.setText(f"🖥️ CPU: {stats.cpu_percent:.1f}%")
            self.memory_label.setText(
                f"💾 Memory: {stats.memory_percent:.1f}% "
                f"({stats.memory_used_mb} / {stats.memory_total_mb} MB)"
            )
            self.disk_label.setText(
                f"💿 Disk: {stats.disk_percent:.1f}% "
                f"({stats.disk_used_gb:.1f} / {stats.disk_total_gb:.1f} GB)"
            )
        except Exception as e:
            self.logger.error(f"Error updating resources: {e}")
    
    def refresh_startup_programs(self):
        """Refresh startup programs list"""
        self.startup_items = self.optimizer.get_startup_programs()
        self.startup_table.setRowCount(len(self.startup_items))
        
        for row, item in enumerate(self.startup_items):
            self.startup_table.setItem(row, 0, QTableWidgetItem(item.name))
            self.startup_table.setItem(row, 1, QTableWidgetItem(item.command))
            self.startup_table.setItem(row, 2, QTableWidgetItem(item.location))
        
        self.logger.info(f"Found {len(self.startup_items)} startup programs")
    
    def disable_selected(self):
        """Disable selected startup programs"""
        selected_rows = set(item.row() for item in self.startup_table.selectedItems())
        
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select programs to disable")
            return
        
        selected_items = [self.startup_items[row] for row in selected_rows]
        
        reply = QMessageBox.question(
            self,
            "Confirm Disable",
            f"Are you sure you want to disable {len(selected_items)} startup program(s)?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            success_count = 0
            for item in selected_items:
                if self.optimizer.disable_startup_program(item):
                    success_count += 1
                    self.logger.info(f"Disabled startup program: {item.name}")
                else:
                    self.logger.error(f"Failed to disable: {item.name}")
            
            QMessageBox.information(
                self,
                "Operation Complete",
                f"Successfully disabled {success_count} of {len(selected_items)} programs"
            )
            
            self.refresh_startup_programs()
