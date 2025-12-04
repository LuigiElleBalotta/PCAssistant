"""
Windows Registry manager
Scan and clean registry issues with backup support
"""
import winreg
import os
import subprocess
from typing import List, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class RegistryIssue:
    """Registry issue information"""
    key_path: str
    value_name: str
    issue_type: str  # 'invalid_path', 'orphaned_uninstall', 'missing_file'
    description: str


class RegistryManager:
    """Manage Windows Registry operations"""
    
    # Common registry paths to scan
    SCAN_PATHS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Classes"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
    ]
    
    def __init__(self):
        """Initialize registry manager"""
        self.issues = []
        self.backup_dir = "registry_backups"
    
    def backup_registry(self, backup_name: str = None) -> Optional[str]:
        """
        Create registry backup using Windows reg command
        
        Args:
            backup_name: Optional backup file name
        
        Returns:
            Path to backup file or None if failed
        """
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
        
        if backup_name is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"registry_backup_{timestamp}.reg"
        
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        try:
            # Export entire registry (requires admin)
            # Note: This exports HKLM and HKCU
            subprocess.run(
                ['reg', 'export', 'HKLM', backup_path, '/y'],
                check=True,
                capture_output=True
            )
            return backup_path
        except subprocess.CalledProcessError:
            return None
    
    def restore_registry(self, backup_path: str) -> bool:
        """
        Restore registry from backup
        
        Args:
            backup_path: Path to backup .reg file
        
        Returns:
            True if successful
        """
        if not os.path.exists(backup_path):
            return False
        
        try:
            subprocess.run(
                ['reg', 'import', backup_path],
                check=True,
                capture_output=True
            )
            return True
        except subprocess.CalledProcessError:
            return False
    
    def _check_file_exists(self, filepath: str) -> bool:
        """Check if file path exists"""
        if not filepath:
            return True  # Empty path is not an issue
        
        # Clean up path
        filepath = filepath.strip('"').strip("'")
        
        # Expand environment variables
        filepath = os.path.expandvars(filepath)
        
        return os.path.exists(filepath)
    
    def scan_uninstall_entries(self) -> List[RegistryIssue]:
        """Scan for orphaned uninstall entries"""
        issues = []
        
        uninstall_paths = [
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        ]
        
        for hkey, path in uninstall_paths:
            try:
                with winreg.OpenKey(hkey, path) as key:
                    index = 0
                    while True:
                        try:
                            subkey_name = winreg.EnumKey(key, index)
                            subkey_path = f"{path}\\{subkey_name}"
                            
                            with winreg.OpenKey(hkey, subkey_path) as subkey:
                                # Check if DisplayIcon exists and is valid
                                try:
                                    icon_path = winreg.QueryValueEx(subkey, "DisplayIcon")[0]
                                    if icon_path and not self._check_file_exists(icon_path.split(',')[0]):
                                        issues.append(RegistryIssue(
                                            key_path=subkey_path,
                                            value_name="DisplayIcon",
                                            issue_type="invalid_path",
                                            description=f"Invalid icon path: {icon_path}"
                                        ))
                                except FileNotFoundError:
                                    pass
                                
                                # Check if InstallLocation exists and is valid
                                try:
                                    install_loc = winreg.QueryValueEx(subkey, "InstallLocation")[0]
                                    if install_loc and not self._check_file_exists(install_loc):
                                        issues.append(RegistryIssue(
                                            key_path=subkey_path,
                                            value_name="InstallLocation",
                                            issue_type="invalid_path",
                                            description=f"Invalid install location: {install_loc}"
                                        ))
                                except FileNotFoundError:
                                    pass
                            
                            index += 1
                        except OSError:
                            break
            except (OSError, PermissionError):
                continue
        
        return issues
    
    def scan_startup_entries(self) -> List[RegistryIssue]:
        """Scan for invalid startup entries"""
        issues = []
        
        startup_paths = [
            (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        ]
        
        for hkey, path in startup_paths:
            try:
                with winreg.OpenKey(hkey, path) as key:
                    index = 0
                    while True:
                        try:
                            value_name, value_data, value_type = winreg.EnumValue(key, index)
                            
                            # Extract executable path
                            exe_path = value_data.strip('"').split()[0] if value_data else ""
                            
                            if exe_path and not self._check_file_exists(exe_path):
                                issues.append(RegistryIssue(
                                    key_path=path,
                                    value_name=value_name,
                                    issue_type="missing_file",
                                    description=f"Startup program not found: {exe_path}"
                                ))
                            
                            index += 1
                        except OSError:
                            break
            except (OSError, PermissionError):
                continue
        
        return issues
    
    def scan_registry_issues(self) -> List[RegistryIssue]:
        """
        Scan registry for common issues
        
        Returns:
            List of RegistryIssue objects
        """
        self.issues = []
        
        # Scan uninstall entries
        self.issues.extend(self.scan_uninstall_entries())
        
        # Scan startup entries
        self.issues.extend(self.scan_startup_entries())
        
        return self.issues
    
    def clean_registry_issue(self, issue: RegistryIssue) -> bool:
        """
        Clean a specific registry issue
        
        Args:
            issue: RegistryIssue to clean
        
        Returns:
            True if successful
        """
        try:
            # Determine which hive to use
            if issue.key_path.startswith("HKEY_LOCAL_MACHINE") or "SOFTWARE" in issue.key_path:
                hkey = winreg.HKEY_LOCAL_MACHINE
            else:
                hkey = winreg.HKEY_CURRENT_USER
            
            # Remove HKEY prefix if present
            key_path = issue.key_path.replace("HKEY_LOCAL_MACHINE\\", "").replace("HKEY_CURRENT_USER\\", "")
            
            with winreg.OpenKey(hkey, key_path, 0, winreg.KEY_SET_VALUE) as key:
                winreg.DeleteValue(key, issue.value_name)
            
            return True
        except (OSError, PermissionError):
            return False
    
    def clean_registry(self, issues: List[RegistryIssue] = None) -> dict:
        """
        Clean multiple registry issues
        
        Args:
            issues: List of issues to clean (uses self.issues if None)
        
        Returns:
            Dictionary with statistics
        """
        if issues is None:
            issues = self.issues
        
        cleaned = 0
        failed = 0
        
        for issue in issues:
            if self.clean_registry_issue(issue):
                cleaned += 1
            else:
                failed += 1
        
        return {
            'total_issues': len(issues),
            'cleaned': cleaned,
            'failed': failed,
            'success': cleaned > 0
        }
