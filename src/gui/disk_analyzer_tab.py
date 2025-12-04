"""
Disk Analyzer Tab - Analyze disk space usage with tree view
"""
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, QFileDialog,
                             QMessageBox, QHeaderView, QProgressDialog, QSpinBox,
                             QGroupBox, QApplication)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from core.analyzer import DiskAnalyzer, DiskItem
from core.secure_delete import SecureDelete
from utils.scanner import Scanner
from utils.logger import get_logger
import os
import shutil


class ScanThread(QThread):
    """Thread for directory scanning"""
    progress = pyqtSignal(str, int, int)
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    
    def __init__(self, directory, min_size_mb=0, max_depth=None):
        super().__init__()
        self.directory = directory
        self.min_size_mb = min_size_mb
        self.max_depth = max_depth
        self.analyzer = DiskAnalyzer()
        self._is_cancelled = False
    
    def run(self):
        """Run the scan"""
        try:
            min_size_bytes = self.min_size_mb * 1024 * 1024
            root = self.analyzer.build_directory_tree(
                self.directory,
                progress_callback=self.progress_callback,
                min_size=min_size_bytes,
                max_depth=self.max_depth
            )
            if not self._is_cancelled:
                self.finished.emit(root)
        except Exception as e:
            self.error.emit(str(e))
    
    def progress_callback(self, message, current, total):
        """Progress callback"""
        if not self._is_cancelled:
            self.progress.emit(message, current, total)
    
    def cancel(self):
        """Cancel the scan"""
        self._is_cancelled = True


class SecureDeleteThread(QThread):
    """Thread for secure deletion"""
    progress = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(int, int)  # deleted_count, total_count
    error = pyqtSignal(str)
    
    def __init__(self, items_to_delete):
        super().__init__()
        self.items_to_delete = items_to_delete
        self._is_cancelled = False
        self.deleted_count = 0
    
    def run(self):
        """Run secure deletion"""
        try:
            deleter = SecureDelete()
            total_items = len(self.items_to_delete)
            
            for idx, disk_item in enumerate(self.items_to_delete):
                if self._is_cancelled:
                    break
                
                overall_progress = int((idx / total_items) * 100)
                
                try:
                    if disk_item.is_dir:
                        # Secure delete folder
                        def folder_callback(current_file, file_idx, total_files):
                            if self._is_cancelled:
                                return
                            file_name = os.path.basename(current_file)
                            msg = f"Folder ({idx + 1}/{total_items}): {disk_item.name}\nFile {file_idx}/{total_files}: {file_name}"
                            self.progress.emit(msg, overall_progress)
                        
                        self.progress.emit(f"Folder ({idx + 1}/{total_items}): {disk_item.name}\nCounting files...", overall_progress)
                        
                        if deleter.secure_delete_folder(disk_item.path, passes=3, callback=folder_callback):
                            self.deleted_count += 1
                    else:
                        # Secure delete file
                        def file_callback(current_pass, total_passes, status):
                            if self._is_cancelled:
                                return
                            msg = f"File ({idx + 1}/{total_items}): {disk_item.name}\nPass {current_pass}/{total_passes}"
                            self.progress.emit(msg, overall_progress)
                        
                        if deleter.secure_delete_file(disk_item.path, passes=3, callback=file_callback):
                            self.deleted_count += 1
                except Exception as e:
                    self.error.emit(f"Error deleting {disk_item.path}: {str(e)}")
            
            self.finished.emit(self.deleted_count, total_items)
        except Exception as e:
            self.error.emit(str(e))
    
    def cancel(self):
        """Cancel the operation"""
        self._is_cancelled = True


class DiskAnalyzerTab(QWidget):
    """Disk space analyzer tab"""
    
    def __init__(self):
        super().__init__()
        self.logger = get_logger()
        self.current_root = None
        self.scan_thread = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize UI"""
        layout = QVBoxLayout()
        
        # Top controls
        controls_layout = QHBoxLayout()
        
        self.select_btn = QPushButton("Select Directory")
        self.select_btn.clicked.connect(self.select_directory)
        controls_layout.addWidget(self.select_btn)
        
        self.path_label = QLabel("No directory selected")
        self.path_label.setStyleSheet("color: #0d7377; font-weight: bold;")
        controls_layout.addWidget(self.path_label, 1)
        
        self.scan_btn = QPushButton("Scan")
        self.scan_btn.clicked.connect(self.start_scan)
        self.scan_btn.setEnabled(False)
        controls_layout.addWidget(self.scan_btn)
        
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.clicked.connect(self.stop_scan)
        self.stop_btn.setEnabled(False)
        controls_layout.addWidget(self.stop_btn)
        
        layout.addLayout(controls_layout)
        
        # Filters
        filter_group = QGroupBox("Filters")
        filter_layout = QHBoxLayout()
        
        filter_layout.addWidget(QLabel("Min Size (MB):"))
        self.min_size_spin = QSpinBox()
        self.min_size_spin.setRange(0, 10000)
        self.min_size_spin.setValue(0)
        self.min_size_spin.setSuffix(" MB")
        filter_layout.addWidget(self.min_size_spin)
        
        filter_layout.addWidget(QLabel("Max Depth:"))
        self.max_depth_spin = QSpinBox()
        self.max_depth_spin.setRange(0, 20)
        self.max_depth_spin.setValue(0)
        self.max_depth_spin.setSpecialValueText("Unlimited")
        filter_layout.addWidget(self.max_depth_spin)
        
        filter_layout.addStretch()
        filter_group.setLayout(filter_layout)
        layout.addWidget(filter_group)
        
        # Tree view
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Name", "Size", "Items", "%", "Type"])
        self.tree.setColumnWidth(0, 300)
        self.tree.setColumnWidth(1, 100)
        self.tree.setColumnWidth(2, 80)
        self.tree.setColumnWidth(3, 60)
        self.tree.setColumnWidth(4, 100)
        self.tree.setSortingEnabled(True)
        self.tree.setSelectionMode(QTreeWidget.ExtendedSelection)
        self.tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        layout.addWidget(self.tree)
        
        # Bottom info and actions
        bottom_layout = QHBoxLayout()
        
        self.info_label = QLabel("No items selected")
        bottom_layout.addWidget(self.info_label, 1)
        
        self.delete_btn = QPushButton("Delete Selected")
        self.delete_btn.clicked.connect(self.delete_selected)
        self.delete_btn.setEnabled(False)
        bottom_layout.addWidget(self.delete_btn)
        
        self.secure_delete_btn = QPushButton("Secure Delete")
        self.secure_delete_btn.clicked.connect(self.secure_delete_selected)
        self.secure_delete_btn.setEnabled(False)
        bottom_layout.addWidget(self.secure_delete_btn)
        
        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        self.refresh_btn.setEnabled(False)
        bottom_layout.addWidget(self.refresh_btn)
        
        layout.addLayout(bottom_layout)
        
        self.setLayout(layout)
        
        # Connect selection changed
        self.tree.itemSelectionChanged.connect(self.update_selection_info)
    
    def select_directory(self):
        """Select directory to analyze"""
        directory = QFileDialog.getExistingDirectory(
            self,
            "Select Directory to Analyze",
            "",
            QFileDialog.ShowDirsOnly
        )
        
        if directory:
            self.current_root = directory
            self.path_label.setText(f"Root: {directory}")
            self.scan_btn.setEnabled(True)
            self.refresh_btn.setEnabled(True)
            self.tree.clear()
    
    def start_scan(self):
        """Start scanning"""
        if not self.current_root:
            return
        
        min_size_mb = self.min_size_spin.value()
        max_depth = self.max_depth_spin.value() if self.max_depth_spin.value() > 0 else None
        
        # Create progress dialog
        self.progress_dialog = QProgressDialog("Scanning directory...", "Cancel", 0, 100, self)
        self.progress_dialog.setWindowTitle("Disk Analyzer")
        self.progress_dialog.setWindowModality(Qt.WindowModal)
        self.progress_dialog.canceled.connect(self.stop_scan)
        
        # Start scan thread
        self.scan_thread = ScanThread(self.current_root, min_size_mb, max_depth)
        self.scan_thread.progress.connect(self.update_progress)
        self.scan_thread.finished.connect(self.scan_finished)
        self.scan_thread.error.connect(self.scan_error)
        self.scan_thread.start()
        
        self.scan_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.select_btn.setEnabled(False)
    
    def stop_scan(self):
        """Stop scanning"""
        if self.scan_thread:
            self.scan_thread.cancel()
            self.scan_thread.wait()
        
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_btn.setEnabled(True)
    
    def update_progress(self, message, current, total):
        """Update progress dialog"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.setLabelText(message)
            if total > 0:
                self.progress_dialog.setValue(int((current / total) * 100))
    
    def scan_finished(self, root_item: DiskItem):
        """Scan finished"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        self.tree.clear()
        self.populate_tree(root_item, None)
        self.tree.expandToDepth(0)
        
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_btn.setEnabled(True)
        
        self.logger.info(f"Disk scan completed: {root_item.name}")
    
    def scan_error(self, error_msg):
        """Scan error"""
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        
        QMessageBox.critical(self, "Scan Error", f"Error during scan:\n{error_msg}")
        
        self.scan_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.select_btn.setEnabled(True)
    
    def populate_tree(self, disk_item: DiskItem, parent_item):
        """Populate tree with disk items"""
        # Create tree item
        item = QTreeWidgetItem()
        item.setText(0, disk_item.name)
        item.setText(1, Scanner.format_size(disk_item.size))
        item.setText(2, str(disk_item.item_count))
        item.setText(3, f"{disk_item.percentage:.1f}%")
        item.setText(4, "Folder" if disk_item.is_dir else "File")
        
        # Set sort keys for numerical columns (for proper sorting)
        item.setData(1, Qt.UserRole, disk_item.size)  # Size for sorting
        item.setData(2, Qt.UserRole, disk_item.item_count)  # Items for sorting
        item.setData(3, Qt.UserRole, disk_item.percentage)  # Percentage for sorting
        
        # Store disk_item for later use
        item.setData(0, Qt.UserRole, disk_item)
        
        # Color code by size percentage
        if disk_item.percentage > 50:
            item.setForeground(1, Qt.red)
        elif disk_item.percentage > 20:
            item.setForeground(1, Qt.yellow)
        
        # Add to tree
        if parent_item is None:
            self.tree.addTopLevelItem(item)
        else:
            parent_item.addChild(item)
        
        # Add children
        for child in disk_item.children:
            self.populate_tree(child, item)
    
    def update_selection_info(self):
        """Update selection info"""
        selected = self.tree.selectedItems()
        
        if not selected:
            self.info_label.setText("No items selected")
            self.delete_btn.setEnabled(False)
            self.secure_delete_btn.setEnabled(False)
            return
        
        total_size = 0
        for item in selected:
            disk_item = item.data(0, Qt.UserRole)
            if disk_item:
                total_size += disk_item.size
        
        self.info_label.setText(
            f"Selected: {len(selected)} items ({Scanner.format_size(total_size)})"
        )
        self.delete_btn.setEnabled(True)
        self.secure_delete_btn.setEnabled(True)
    
    def delete_selected(self):
        """Delete selected items"""
        selected = self.tree.selectedItems()
        if not selected:
            return
        
        # Collect items data first (before tree modification)
        items_to_delete = []
        total_size = 0
        for item in selected:
            disk_item = item.data(0, Qt.UserRole)
            if disk_item:
                items_to_delete.append(disk_item)
                total_size += disk_item.size
        
        if not items_to_delete:
            return
        
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Deletion",
            f"Delete {len(items_to_delete)} items ({Scanner.format_size(total_size)})?\n\n"
            "This will move items to Recycle Bin.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Create progress dialog
        progress = QProgressDialog("Deleting items...", "Cancel", 0, len(items_to_delete), self)
        progress.setWindowTitle("Deleting")
        progress.setWindowModality(Qt.WindowModal)
        
        # Delete items
        deleted_count = 0
        for idx, disk_item in enumerate(items_to_delete):
            if progress.wasCanceled():
                break
            
            progress.setLabelText(f"Deleting: {disk_item.name}")
            progress.setValue(idx)
            QApplication.processEvents()
            
            try:
                if os.path.exists(disk_item.path):
                    if disk_item.is_dir:
                        shutil.rmtree(disk_item.path)
                    else:
                        os.remove(disk_item.path)
                    deleted_count += 1
                    self.logger.info(f"Deleted: {disk_item.path}")
            except Exception as e:
                self.logger.error(f"Error deleting {disk_item.path}: {e}")
        
        progress.setValue(len(items_to_delete))
        progress.close()
        
        QMessageBox.information(
            self,
            "Deletion Complete",
            f"Deleted {deleted_count} of {len(items_to_delete)} items."
        )
        
        self.refresh()
    
    def secure_delete_selected(self):
        """Securely delete selected items"""
        selected = self.tree.selectedItems()
        if not selected:
            return
        
        # Collect items data first
        items_to_delete = []
        total_size = 0
        for item in selected:
            disk_item = item.data(0, Qt.UserRole)
            if disk_item:
                items_to_delete.append(disk_item)
                total_size += disk_item.size
        
        if not items_to_delete:
            return
        
        # Confirm
        reply = QMessageBox.warning(
            self,
            "Confirm Secure Deletion",
            f"Securely delete {len(items_to_delete)} items ({Scanner.format_size(total_size)})?\n\n"
            "WARNING: This is PERMANENT and cannot be undone!\n"
            "Files will be overwritten 3 times before deletion.\n\n"
            "Note: Large folders may take several minutes.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply != QMessageBox.Yes:
            return
        
        # Create progress dialog
        self.secure_delete_progress = QProgressDialog("Starting secure deletion...", "Cancel", 0, 100, self)
        self.secure_delete_progress.setWindowTitle("Secure Delete")
        self.secure_delete_progress.setWindowModality(Qt.WindowModal)
        self.secure_delete_progress.setMinimumDuration(0)
        self.secure_delete_progress.setValue(0)
        self.secure_delete_progress.canceled.connect(self.cancel_secure_delete)
        
        # Start secure delete thread
        self.secure_delete_thread = SecureDeleteThread(items_to_delete)
        self.secure_delete_thread.progress.connect(self.update_secure_delete_progress)
        self.secure_delete_thread.finished.connect(self.secure_delete_finished)
        self.secure_delete_thread.error.connect(self.secure_delete_error)
        self.secure_delete_thread.start()
        
        # Disable buttons during deletion
        self.delete_btn.setEnabled(False)
        self.secure_delete_btn.setEnabled(False)
        self.scan_btn.setEnabled(False)
    
    def update_secure_delete_progress(self, message, percentage):
        """Update secure delete progress"""
        if hasattr(self, 'secure_delete_progress'):
            self.secure_delete_progress.setLabelText(message)
            self.secure_delete_progress.setValue(percentage)
    
    def secure_delete_finished(self, deleted_count, total_count):
        """Secure delete finished"""
        if hasattr(self, 'secure_delete_progress'):
            self.secure_delete_progress.close()
        
        # Re-enable buttons
        self.delete_btn.setEnabled(True)
        self.secure_delete_btn.setEnabled(True)
        self.scan_btn.setEnabled(True)
        
        QMessageBox.information(
            self,
            "Secure Deletion Complete",
            f"Securely deleted {deleted_count} of {total_count} items."
        )
        
        self.refresh()
    
    def secure_delete_error(self, error_msg):
        """Secure delete error"""
        self.logger.error(f"Secure delete error: {error_msg}")
    
    def cancel_secure_delete(self):
        """Cancel secure delete"""
        if hasattr(self, 'secure_delete_thread'):
            self.secure_delete_thread.cancel()
    
    def refresh(self):
        """Refresh the scan"""
        if self.current_root:
            self.start_scan()
    
    def show_context_menu(self, position):
        """Show context menu"""
        # TODO: Implement context menu with Open in Explorer, Properties, etc.
        pass
