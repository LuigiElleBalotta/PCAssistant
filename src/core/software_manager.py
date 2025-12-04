"""
Software manager - List and manage installed Windows software
Detects unused software and provides uninstallation
"""
import winreg
import os
import subprocess
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SoftwareInfo:
    """Installed software information"""
    name: str
    version: str
    publisher: str
    install_date: Optional[datetime]
    install_location: Optional[str]
    uninstall_string: Optional[str]
    estimated_size: int  # in KB
    registry_key: str
    
    def get_size_formatted(self) -> str:
        """Get formatted size string"""
        if self.estimated_size == 0:
            return "Unknown"
        size_mb = self.estimated_size / 1024
        if size_mb < 1024:
            return f"{size_mb:.1f} MB"
        else:
            return f"{size_mb/1024:.1f} GB"


class SoftwareManager:
    """Manage installed Windows software"""
    
    # Registry paths for installed software
    UNINSTALL_PATHS = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    
    # System software to exclude (partial name matching)
    SYSTEM_SOFTWARE = [
        "Microsoft Visual C++",
        "Microsoft .NET",
        "Windows",
        "Update for",
        "Security Update",
        "Hotfix for",
        "KB"
    ]
    
    def __init__(self, show_system_software: bool = False):
        """
        Initialize software manager
        
        Args:
            show_system_software: Include system/framework software
        """
        self.show_system_software = show_system_software
        self.software_list = []
    
    def _is_system_software(self, name: str) -> bool:
        """Check if software is system/framework software"""
        if self.show_system_software:
            return False
        
        name_lower = name.lower()
        for system_name in self.SYSTEM_SOFTWARE:
            if system_name.lower() in name_lower:
                return True
        return False
    
    def _parse_install_date(self, date_str: str) -> Optional[datetime]:
        """Parse install date from registry (YYYYMMDD format)"""
        if not date_str or len(date_str) != 8:
            return None
        
        try:
            year = int(date_str[0:4])
            month = int(date_str[4:6])
            day = int(date_str[6:8])
            return datetime(year, month, day)
        except (ValueError, IndexError):
            return None
    
    def _read_registry_key(self, hkey, path: str, subkey_name: str) -> Optional[SoftwareInfo]:
        """Read software info from registry key"""
        try:
            with winreg.OpenKey(hkey, f"{path}\\{subkey_name}") as key:
                # Read values
                try:
                    name = winreg.QueryValueEx(key, "DisplayName")[0]
                except FileNotFoundError:
                    return None
                
                # Skip if system software
                if self._is_system_software(name):
                    return None
                
                # Read other values with defaults
                try:
                    version = winreg.QueryValueEx(key, "DisplayVersion")[0]
                except FileNotFoundError:
                    version = ""
                
                try:
                    publisher = winreg.QueryValueEx(key, "Publisher")[0]
                except FileNotFoundError:
                    publisher = ""
                
                try:
                    install_date_str = winreg.QueryValueEx(key, "InstallDate")[0]
                    install_date = self._parse_install_date(install_date_str)
                except FileNotFoundError:
                    install_date = None
                
                try:
                    install_location = winreg.QueryValueEx(key, "InstallLocation")[0]
                except FileNotFoundError:
                    install_location = None
                
                try:
                    uninstall_string = winreg.QueryValueEx(key, "UninstallString")[0]
                except FileNotFoundError:
                    uninstall_string = None
                
                try:
                    size = int(winreg.QueryValueEx(key, "EstimatedSize")[0])
                except (FileNotFoundError, ValueError, TypeError):
                    size = 0
                
                return SoftwareInfo(
                    name=name,
                    version=version,
                    publisher=publisher,
                    install_date=install_date,
                    install_location=install_location,
                    uninstall_string=uninstall_string,
                    estimated_size=size,
                    registry_key=f"{path}\\{subkey_name}"
                )
        
        except (OSError, PermissionError):
            return None
    
    def get_installed_software(self) -> List[SoftwareInfo]:
        """
        Get list of installed software from Windows Registry
        
        Returns:
            List of SoftwareInfo objects
        """
        self.software_list = []
        seen_names = set()  # Avoid duplicates
        
        for path in self.UNINSTALL_PATHS:
            try:
                with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, path) as key:
                    # Enumerate all subkeys
                    index = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, index)
                            software = self._read_registry_key(winreg.HKEY_LOCAL_MACHINE, path, subkey_name)
                            
                            if software and software.name not in seen_names:
                                self.software_list.append(software)
                                seen_names.add(software.name)
                            
                            index += 1
                        except OSError:
                            break
            except (OSError, PermissionError):
                continue
        
        # Sort by name
        self.software_list.sort(key=lambda s: s.name.lower())
        return self.software_list
    
    def get_software_last_used(self, install_location: str) -> Optional[datetime]:
        """
        Estimate last usage date by checking file modification times
        
        Args:
            install_location: Installation directory path
        
        Returns:
            Most recent modification datetime or None
        """
        if not install_location or not os.path.exists(install_location):
            return None
        
        latest_time = None
        
        try:
            # Check .exe files in installation directory
            for root, dirs, files in os.walk(install_location):
                for filename in files:
                    if filename.endswith('.exe'):
                        filepath = os.path.join(root, filename)
                        try:
                            mtime = datetime.fromtimestamp(os.path.getmtime(filepath))
                            if latest_time is None or mtime > latest_time:
                                latest_time = mtime
                        except (OSError, PermissionError):
                            continue
        except (OSError, PermissionError):
            pass
        
        return latest_time
    
    def is_software_unused(self, software: SoftwareInfo, threshold_days: int = 90) -> bool:
        """
        Check if software appears unused
        
        Args:
            software: SoftwareInfo object
            threshold_days: Days threshold for "unused"
        
        Returns:
            True if software hasn't been used in threshold_days
        """
        last_used = self.get_software_last_used(software.install_location)
        
        if last_used is None:
            # Can't determine, assume used
            return False
        
        threshold_date = datetime.now() - timedelta(days=threshold_days)
        return last_used < threshold_date
    
    def uninstall_software(self, software: SoftwareInfo) -> bool:
        """
        Uninstall software using its uninstall string
        
        Args:
            software: SoftwareInfo object
        
        Returns:
            True if uninstall command was executed successfully
        """
        if not software.uninstall_string:
            return False
        
        try:
            # Execute uninstall command
            # Note: This may show UI dialogs from the uninstaller
            subprocess.Popen(software.uninstall_string, shell=True)
            return True
        except Exception as e:
            print(f"Failed to uninstall {software.name}: {e}")
            return False
    
    def get_statistics(self) -> dict:
        """Get software statistics"""
        total_size = sum(s.estimated_size for s in self.software_list)
        
        return {
            'total_programs': len(self.software_list),
            'total_size_kb': total_size,
            'total_size_formatted': f"{total_size / 1024 / 1024:.1f} GB"
        }
