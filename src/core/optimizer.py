"""
System optimizer - Manage startup programs and monitor resources
"""
import winreg
import os
import psutil
from typing import List, Optional
from dataclasses import dataclass


@dataclass
class StartupItem:
    """Startup program information"""
    name: str
    command: str
    location: str  # 'registry' or 'folder'
    registry_path: Optional[str]
    enabled: bool


@dataclass
class ResourceStats:
    """System resource statistics"""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: int
    memory_total_mb: int
    disk_percent: float
    disk_used_gb: float
    disk_total_gb: float


class SystemOptimizer:
    """System optimization and monitoring"""
    
    STARTUP_REGISTRY_PATHS = [
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Run"),
    ]
    
    def __init__(self):
        """Initialize system optimizer"""
        self.startup_items = []
    
    def get_startup_programs(self) -> List[StartupItem]:
        """
        Get list of startup programs from registry and startup folder
        
        Returns:
            List of StartupItem objects
        """
        self.startup_items = []
        
        # Scan registry locations
        for hkey, path in self.STARTUP_REGISTRY_PATHS:
            try:
                with winreg.OpenKey(hkey, path) as key:
                    index = 0
                    while True:
                        try:
                            value_name, value_data, value_type = winreg.EnumValue(key, index)
                            
                            self.startup_items.append(StartupItem(
                                name=value_name,
                                command=value_data,
                                location='registry',
                                registry_path=path,
                                enabled=True
                            ))
                            
                            index += 1
                        except OSError:
                            break
            except (OSError, PermissionError):
                continue
        
        # Scan startup folder
        startup_folder = os.path.join(
            os.environ.get('APPDATA', ''),
            r'Microsoft\Windows\Start Menu\Programs\Startup'
        )
        
        if os.path.exists(startup_folder):
            try:
                for item in os.listdir(startup_folder):
                    item_path = os.path.join(startup_folder, item)
                    if os.path.isfile(item_path):
                        self.startup_items.append(StartupItem(
                            name=item,
                            command=item_path,
                            location='folder',
                            registry_path=None,
                            enabled=True
                        ))
            except (OSError, PermissionError):
                pass
        
        return self.startup_items
    
    def disable_startup_program(self, item: StartupItem) -> bool:
        """
        Disable a startup program
        
        Args:
            item: StartupItem to disable
        
        Returns:
            True if successful
        """
        if item.location == 'registry':
            return self._remove_registry_startup(item)
        elif item.location == 'folder':
            return self._remove_folder_startup(item)
        return False
    
    def _remove_registry_startup(self, item: StartupItem) -> bool:
        """Remove startup item from registry"""
        try:
            # Determine hive
            if "HKEY_CURRENT_USER" in item.registry_path or item.registry_path.startswith("SOFTWARE"):
                hkey = winreg.HKEY_CURRENT_USER
            else:
                hkey = winreg.HKEY_LOCAL_MACHINE
            
            # Clean path
            path = item.registry_path.replace("HKEY_LOCAL_MACHINE\\", "").replace("HKEY_CURRENT_USER\\", "")
            
            with winreg.OpenKey(hkey, path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, item.name)
            
            return True
        except (OSError, PermissionError):
            return False
    
    def _remove_folder_startup(self, item: StartupItem) -> bool:
        """Remove startup item from folder"""
        try:
            if os.path.exists(item.command):
                os.remove(item.command)
                return True
        except (OSError, PermissionError):
            pass
        return False
    
    def get_system_resources(self) -> ResourceStats:
        """
        Get current system resource usage
        
        Returns:
            ResourceStats object
        """
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_used_mb = memory.used / (1024 * 1024)
        memory_total_mb = memory.total / (1024 * 1024)
        
        # Disk usage (C: drive)
        disk = psutil.disk_usage('C:\\')
        disk_used_gb = disk.used / (1024 * 1024 * 1024)
        disk_total_gb = disk.total / (1024 * 1024 * 1024)
        
        return ResourceStats(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            memory_used_mb=int(memory_used_mb),
            memory_total_mb=int(memory_total_mb),
            disk_percent=disk.percent,
            disk_used_gb=round(disk_used_gb, 2),
            disk_total_gb=round(disk_total_gb, 2)
        )
    
    def get_process_list(self) -> List[dict]:
        """
        Get list of running processes
        
        Returns:
            List of process dictionaries
        """
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                processes.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cpu_percent': proc.info['cpu_percent'],
                    'memory_percent': proc.info['memory_percent']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda p: p['cpu_percent'] or 0, reverse=True)
        
        return processes
