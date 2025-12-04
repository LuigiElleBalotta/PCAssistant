"""
Dashboard tab - Overview and statistics
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QGroupBox, QGridLayout)
from PyQt5.QtCore import Qt
from core.optimizer import SystemOptimizer
from utils.scanner import Scanner



class DashboardTab(QWidget):
    """Dashboard overview tab"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Header
        header = QLabel("Dashboard")
        header.setObjectName("headerLabel")
        layout.addWidget(header)
        
        # System Health Group
        health_group = QGroupBox("System Health")
        health_layout = QGridLayout()
        health_group.setLayout(health_layout)
        
        self.cpu_label = QLabel("CPU: --")
        self.memory_label = QLabel("Memory: --")
        self.disk_label = QLabel("Disk: --")
        
        health_layout.addWidget(QLabel("🖥️"), 0, 0)
        health_layout.addWidget(self.cpu_label, 0, 1)
        health_layout.addWidget(QLabel("💾"), 1, 0)
        health_layout.addWidget(self.memory_label, 1, 1)
        health_layout.addWidget(QLabel("💿"), 2, 0)
        health_layout.addWidget(self.disk_label, 2, 1)
        
        layout.addWidget(health_group)
        
        # Quick Stats Group
        stats_group = QGroupBox("Quick Statistics")
        stats_layout = QVBoxLayout()
        stats_group.setLayout(stats_layout)
        
        self.junk_label = QLabel("Junk Files: Analyzing...")
        self.junk_label.setObjectName("statsLabel")
        stats_layout.addWidget(self.junk_label)
        
        layout.addWidget(stats_group)
        
        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        actions_group.setLayout(actions_layout)
        
        analyze_btn = QPushButton("🔍 Quick Analyze")
        analyze_btn.clicked.connect(self.quick_analyze)
        actions_layout.addWidget(analyze_btn)
        
        clean_btn = QPushButton("🧹 Quick Clean")
        clean_btn.clicked.connect(self.quick_clean)
        actions_layout.addWidget(clean_btn)
        
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        # Update stats
        self.update_stats()
    
    def update_stats(self):
        """Update dashboard statistics"""
        try:
            optimizer = SystemOptimizer()
            stats = optimizer.get_system_resources()
            
            self.cpu_label.setText(f"CPU: {stats.cpu_percent:.1f}%")
            self.memory_label.setText(
                f"Memory: {stats.memory_percent:.1f}% "
                f"({stats.memory_used_mb} / {stats.memory_total_mb} MB)"
            )
            self.disk_label.setText(
                f"Disk: {stats.disk_percent:.1f}% "
                f"({stats.disk_used_gb:.1f} / {stats.disk_total_gb:.1f} GB)"
            )
        except Exception as e:
            print(f"Error updating stats: {e}")
    
    def quick_analyze(self):
        """Quick analyze action"""
        if self.parent_window:
            self.parent_window.quick_analyze()
    
    def quick_clean(self):
        """Quick clean action"""
        if self.parent_window:
            self.parent_window.tabs.setCurrentWidget(self.parent_window.cleaner_tab)
