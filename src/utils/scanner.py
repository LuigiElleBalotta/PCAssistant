"""
File system scanner utilities
Provides efficient file scanning with progress callbacks
"""
import os
from typing import List, Callable, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class FileInfo:
    """File information container"""
    path: str
    size: int
    modified: datetime
    is_dir: bool = False
    
    def __hash__(self):
        return hash(self.path)


class Scanner:
    """File system scanner with progress tracking"""
    
    def __init__(self, excluded_paths: List[str] = None):
        """Initialize scanner with optional exclusions"""
        self.excluded_paths = excluded_paths or []
        self.scanned_count = 0
        self.total_size = 0
    
    def is_excluded(self, path: str) -> bool:
        """Check if path should be excluded"""
        path_lower = path.lower()
        for excluded in self.excluded_paths:
            if path_lower.startswith(excluded.lower()):
                return True
        return False
    
    def scan_directory(
        self,
        directory: str,
        recursive: bool = True,
        callback: Optional[Callable[[str, int], None]] = None
    ) -> List[FileInfo]:
        """
        Scan directory and return list of files
        
        Args:
            directory: Directory to scan
            recursive: Scan subdirectories
            callback: Progress callback(current_file, count)
        
        Returns:
            List of FileInfo objects
        """
        files = []
        self.scanned_count = 0
        self.total_size = 0
        
        try:
            if recursive:
                for root, dirs, filenames in os.walk(directory):
                    # Skip excluded directories
                    if self.is_excluded(root):
                        dirs.clear()  # Don't descend into subdirectories
                        continue
                    
                    for filename in filenames:
                        filepath = os.path.join(root, filename)
                        
                        if self.is_excluded(filepath):
                            continue
                        
                        try:
                            stat = os.stat(filepath)
                            file_info = FileInfo(
                                path=filepath,
                                size=stat.st_size,
                                modified=datetime.fromtimestamp(stat.st_mtime),
                                is_dir=False
                            )
                            files.append(file_info)
                            self.scanned_count += 1
                            self.total_size += stat.st_size
                            
                            if callback:
                                callback(filepath, self.scanned_count)
                        except (OSError, PermissionError):
                            # Skip files we can't access
                            continue
            else:
                # Non-recursive scan
                for item in os.listdir(directory):
                    filepath = os.path.join(directory, item)
                    
                    if self.is_excluded(filepath):
                        continue
                    
                    try:
                        stat = os.stat(filepath)
                        if os.path.isfile(filepath):
                            file_info = FileInfo(
                                path=filepath,
                                size=stat.st_size,
                                modified=datetime.fromtimestamp(stat.st_mtime),
                                is_dir=False
                            )
                            files.append(file_info)
                            self.scanned_count += 1
                            self.total_size += stat.st_size
                            
                            if callback:
                                callback(filepath, self.scanned_count)
                    except (OSError, PermissionError):
                        continue
        
        except (OSError, PermissionError):
            pass
        
        return files
    
    def get_directory_size(self, directory: str) -> int:
        """Calculate total size of directory"""
        total_size = 0
        try:
            for root, dirs, files in os.walk(directory):
                if self.is_excluded(root):
                    dirs.clear()
                    continue
                
                for filename in files:
                    filepath = os.path.join(root, filename)
                    if not self.is_excluded(filepath):
                        try:
                            total_size += os.path.getsize(filepath)
                        except (OSError, PermissionError):
                            continue
        except (OSError, PermissionError):
            pass
        
        return total_size
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format bytes to human-readable size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.2f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.2f} PB"
