"""
System cleaner - Remove temporary files, browser data, and junk
"""
import os
import shutil
import winshell
from typing import List, Dict
from dataclasses import dataclass
from pathlib import Path



@dataclass
class CleaningResult:
    """Result of a cleaning operation"""
    category: str
    files_removed: int
    space_freed: int  # bytes
    errors: List[str]
    success: bool
    
    def get_space_formatted(self) -> str:
        """Get formatted space string"""
        from utils.scanner import Scanner
        return Scanner.format_size(self.space_freed)



class SystemCleaner:
    """Clean temporary files and system junk"""
    
    def __init__(self):
        """Initialize system cleaner"""
        self.total_freed = 0
        self.total_files = 0
        self.results = []
    
    def _safe_remove(self, path: str) -> tuple[bool, int]:
        """
        Safely remove file or directory
        
        Returns:
            (success, size_freed)
        """
        try:
            if os.path.isfile(path):
                size = os.path.getsize(path)
                os.remove(path)
                return True, size
            elif os.path.isdir(path):
                # Calculate size before removal
                size = sum(
                    os.path.getsize(os.path.join(root, f))
                    for root, dirs, files in os.walk(path)
                    for f in files
                )
                shutil.rmtree(path)
                return True, size
        except (OSError, PermissionError):
            return False, 0
        
        return False, 0
    
    def clean_temp_files(self) -> CleaningResult:
        """Clean Windows temporary files"""
        temp_paths = [
            os.environ.get('TEMP', ''),
            os.environ.get('TMP', ''),
            r'C:\Windows\Temp',
            os.path.expanduser(r'~\AppData\Local\Temp'),
        ]
        
        files_removed = 0
        space_freed = 0
        errors = []
        
        for temp_dir in temp_paths:
            if not temp_dir or not os.path.exists(temp_dir):
                continue
            
            try:
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    success, size = self._safe_remove(item_path)
                    if success:
                        files_removed += 1
                        space_freed += size
                    else:
                        errors.append(f"Could not remove: {item_path}")
            except (OSError, PermissionError) as e:
                errors.append(f"Error accessing {temp_dir}: {str(e)}")
        
        result = CleaningResult(
            category="Temporary Files",
            files_removed=files_removed,
            space_freed=space_freed,
            errors=errors,
            success=files_removed > 0
        )
        self.results.append(result)
        return result
    
    def clean_browser_cache(self, browsers: List[str] = None) -> CleaningResult:
        """
        Clean browser cache and data
        
        Args:
            browsers: List of browsers ('chrome', 'firefox', 'edge')
        """
        if browsers is None:
            browsers = ['chrome', 'firefox', 'edge']
        
        browser_paths = {
            'chrome': [
                os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Default\Cache'),
                os.path.expanduser(r'~\AppData\Local\Google\Chrome\User Data\Default\Code Cache'),
            ],
            'firefox': [
                os.path.expanduser(r'~\AppData\Local\Mozilla\Firefox\Profiles'),
            ],
            'edge': [
                os.path.expanduser(r'~\AppData\Local\Microsoft\Edge\User Data\Default\Cache'),
                os.path.expanduser(r'~\AppData\Local\Microsoft\Edge\User Data\Default\Code Cache'),
            ]
        }
        
        files_removed = 0
        space_freed = 0
        errors = []
        
        for browser in browsers:
            if browser not in browser_paths:
                continue
            
            for cache_path in browser_paths[browser]:
                if not os.path.exists(cache_path):
                    continue
                
                if 'Profiles' in cache_path:  # Firefox special handling
                    try:
                        for profile in os.listdir(cache_path):
                            profile_cache = os.path.join(cache_path, profile, 'cache2')
                            if os.path.exists(profile_cache):
                                success, size = self._safe_remove(profile_cache)
                                if success:
                                    files_removed += 1
                                    space_freed += size
                    except (OSError, PermissionError) as e:
                        errors.append(f"Firefox error: {str(e)}")
                else:
                    success, size = self._safe_remove(cache_path)
                    if success:
                        files_removed += 1
                        space_freed += size
                    else:
                        errors.append(f"Could not remove: {cache_path}")
        
        result = CleaningResult(
            category="Browser Cache",
            files_removed=files_removed,
            space_freed=space_freed,
            errors=errors,
            success=files_removed > 0
        )
        self.results.append(result)
        return result
    
    def empty_recycle_bin(self) -> CleaningResult:
        """Empty Windows Recycle Bin"""
        try:
            # Get recycle bin size before emptying
            space_freed = 0
            files_removed = 0
            
            # Try to calculate size (may not work on all systems)
            try:
                for item in winshell.recycle_bin():
                    try:
                        space_freed += os.path.getsize(item.original_filename())
                        files_removed += 1
                    except:
                        pass
            except:
                pass
            
            # Empty recycle bin
            winshell.recycle_bin().empty(confirm=False, show_progress=False, sound=False)
            
            result = CleaningResult(
                category="Recycle Bin",
                files_removed=files_removed,
                space_freed=space_freed,
                errors=[],
                success=True
            )
        except Exception as e:
            result = CleaningResult(
                category="Recycle Bin",
                files_removed=0,
                space_freed=0,
                errors=[str(e)],
                success=False
            )
        
        self.results.append(result)
        return result
    
    def clean_recent_files(self) -> CleaningResult:
        """Clean recent files and jump lists"""
        recent_paths = [
            os.path.expanduser(r'~\AppData\Roaming\Microsoft\Windows\Recent'),
            os.path.expanduser(r'~\AppData\Roaming\Microsoft\Windows\Recent\AutomaticDestinations'),
            os.path.expanduser(r'~\AppData\Roaming\Microsoft\Windows\Recent\CustomDestinations'),
        ]
        
        files_removed = 0
        space_freed = 0
        errors = []
        
        for recent_dir in recent_paths:
            if not os.path.exists(recent_dir):
                continue
            
            try:
                for item in os.listdir(recent_dir):
                    item_path = os.path.join(recent_dir, item)
                    success, size = self._safe_remove(item_path)
                    if success:
                        files_removed += 1
                        space_freed += size
            except (OSError, PermissionError) as e:
                errors.append(f"Error: {str(e)}")
        
        result = CleaningResult(
            category="Recent Files",
            files_removed=files_removed,
            space_freed=space_freed,
            errors=errors,
            success=files_removed > 0
        )
        self.results.append(result)
        return result
    
    def clean_windows_logs(self) -> CleaningResult:
        """Clean Windows log files"""
        log_paths = [
            r'C:\Windows\Logs',
            r'C:\Windows\Prefetch',
        ]
        
        files_removed = 0
        space_freed = 0
        errors = []
        
        for log_dir in log_paths:
            if not os.path.exists(log_dir):
                continue
            
            try:
                for item in os.listdir(log_dir):
                    item_path = os.path.join(log_dir, item)
                    if os.path.isfile(item_path):
                        success, size = self._safe_remove(item_path)
                        if success:
                            files_removed += 1
                            space_freed += size
            except (OSError, PermissionError) as e:
                errors.append(f"Error: {str(e)}")
        
        result = CleaningResult(
            category="Windows Logs",
            files_removed=files_removed,
            space_freed=space_freed,
            errors=errors,
            success=files_removed > 0
        )
        self.results.append(result)
        return result
    
    def clean_all(self, options: Dict[str, bool] = None) -> List[CleaningResult]:
        """
        Run all cleaning operations based on options
        
        Args:
            options: Dictionary of cleaning options
        
        Returns:
            List of CleaningResult objects
        """
        if options is None:
            options = {
                'temp_files': True,
                'browser_cache': True,
                'recycle_bin': False,
                'recent_files': True,
                'log_files': True
            }
        
        self.results = []
        
        if options.get('temp_files', True):
            self.clean_temp_files()
        
        if options.get('browser_cache', True):
            self.clean_browser_cache()
        
        if options.get('recycle_bin', False):
            self.empty_recycle_bin()
        
        if options.get('recent_files', True):
            self.clean_recent_files()
        
        if options.get('log_files', True):
            self.clean_windows_logs()
        
        return self.results
    
    def get_total_statistics(self) -> Dict[str, any]:
        """Get total statistics from all cleaning operations"""
        total_files = sum(r.files_removed for r in self.results)
        total_space = sum(r.space_freed for r in self.results)
        
        from utils.scanner import Scanner
        
        return {
            'total_files_removed': total_files,
            'total_space_freed': total_space,
            'total_space_formatted': Scanner.format_size(total_space),
            'operations': len(self.results),
            'successful_operations': sum(1 for r in self.results if r.success)
        }

