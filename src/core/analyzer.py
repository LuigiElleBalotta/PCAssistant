"""
Disk space analyzer
Analyze disk usage and identify large files/folders
"""
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict
from utils.scanner import Scanner, FileInfo



@dataclass
class DiskAnalysis:
    """Disk analysis results"""
    total_size: int
    file_count: int
    folder_count: int
    largest_files: List[FileInfo]
    largest_folders: List[Tuple[str, int]]
    file_type_distribution: Dict[str, int]


class DiskAnalyzer:
    """Analyze disk space usage"""
    
    def __init__(self, excluded_paths: List[str] = None):
        """Initialize disk analyzer"""
        self.scanner = Scanner(excluded_paths)
    
    def analyze_directory(self, path: str, top_n: int = 10) -> DiskAnalysis:
        """
        Analyze disk usage for a directory
        
        Args:
            path: Directory path to analyze
            top_n: Number of top items to return
        
        Returns:
            DiskAnalysis object
        """
        # Scan all files
        files = self.scanner.scan_directory(path, recursive=True)
        
        # Calculate folder sizes
        folder_sizes = defaultdict(int)
        file_types = defaultdict(int)
        folder_count = 0
        
        for file_info in files:
            # Add to folder size
            folder = os.path.dirname(file_info.path)
            folder_sizes[folder] += file_info.size
            
            # Track file types
            ext = os.path.splitext(file_info.path)[1].lower()
            if ext:
                file_types[ext] += file_info.size
            else:
                file_types['[no extension]'] += file_info.size
        
        # Count unique folders
        folder_count = len(folder_sizes)
        
        # Get largest files
        largest_files = sorted(files, key=lambda f: f.size, reverse=True)[:top_n]
        
        # Get largest folders
        largest_folders = sorted(
            folder_sizes.items(),
            key=lambda item: item[1],
            reverse=True
        )[:top_n]
        
        return DiskAnalysis(
            total_size=sum(f.size for f in files),
            file_count=len(files),
            folder_count=folder_count,
            largest_files=largest_files,
            largest_folders=largest_folders,
            file_type_distribution=dict(file_types)
        )
    
    def get_file_type_distribution(self, path: str) -> Dict[str, int]:
        """
        Get file type distribution by size
        
        Args:
            path: Directory path
        
        Returns:
            Dictionary mapping extension to total size
        """
        files = self.scanner.scan_directory(path, recursive=True)
        file_types = defaultdict(int)
        
        for file_info in files:
            ext = os.path.splitext(file_info.path)[1].lower()
            if ext:
                file_types[ext] += file_info.size
            else:
                file_types['[no extension]'] += file_info.size
        
        # Sort by size
        return dict(sorted(file_types.items(), key=lambda item: item[1], reverse=True))
    
    def find_large_files(self, path: str, min_size_mb: int = 100, top_n: int = 50) -> List[FileInfo]:
        """
        Find large files above a certain size
        
        Args:
            path: Directory path
            min_size_mb: Minimum file size in MB
            top_n: Maximum number of files to return
        
        Returns:
            List of FileInfo objects
        """
        min_size_bytes = min_size_mb * 1024 * 1024
        files = self.scanner.scan_directory(path, recursive=True)
        
        # Filter by size
        large_files = [f for f in files if f.size >= min_size_bytes]
        
        # Sort by size
        large_files.sort(key=lambda f: f.size, reverse=True)
        
        return large_files[:top_n]
