"""
Disk analyzer - Analyze disk usage and find large files
"""
import os
from typing import List, Dict, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
from utils.scanner import Scanner, FileInfo


@dataclass
class LargestItem:
    """Information about a large file or folder"""
    path: str
    size: int
    is_directory: bool


@dataclass
class DiskItem:
    """Disk item for tree view"""
    path: str
    name: str
    size: int
    is_dir: bool
    item_count: int
    percentage: float = 0.0
    children: List['DiskItem'] = field(default_factory=list)


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
    """Analyze disk usage"""
    
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
    
    def build_directory_tree(self, directory: str, progress_callback=None, 
                           min_size: int = 0, max_depth: int = None) -> DiskItem:
        """
        Build a hierarchical tree of directory contents with sizes
        
        Args:
            directory: Root directory to analyze
            progress_callback: Optional callback(message, current, total)
            min_size: Minimum size in bytes to include (0 = all)
            max_depth: Maximum depth to scan (None = unlimited)
        
        Returns:
            DiskItem representing the root with all children
        """
        def calculate_dir_size(path: str, current_depth: int = 0) -> Tuple[int, int, List[DiskItem]]:
            """Calculate directory size and build children list"""
            if max_depth is not None and current_depth >= max_depth:
                return 0, 0, []
            
            total_size = 0
            item_count = 0
            children = []
            
            try:
                entries = os.listdir(path)
            except (OSError, PermissionError):
                return 0, 0, []
            
            if progress_callback:
                progress_callback(f"Scanning: {path}", 0, len(entries))
            
            for idx, entry in enumerate(entries):
                entry_path = os.path.join(path, entry)
                
                if progress_callback:
                    progress_callback(f"Scanning: {entry}", idx + 1, len(entries))
                
                try:
                    if os.path.isfile(entry_path):
                        size = os.path.getsize(entry_path)
                        if size >= min_size:
                            child = DiskItem(
                                path=entry_path,
                                name=entry,
                                size=size,
                                is_dir=False,
                                item_count=1
                            )
                            children.append(child)
                            total_size += size
                            item_count += 1
                    
                    elif os.path.isdir(entry_path):
                        dir_size, dir_items, dir_children = calculate_dir_size(
                            entry_path, current_depth + 1
                        )
                        
                        if dir_size >= min_size or dir_children:
                            child = DiskItem(
                                path=entry_path,
                                name=entry,
                                size=dir_size,
                                is_dir=True,
                                item_count=dir_items,
                                children=dir_children
                            )
                            children.append(child)
                            total_size += dir_size
                            item_count += dir_items
                
                except (OSError, PermissionError):
                    continue
            
            # Sort children by size (largest first)
            children.sort(key=lambda x: x.size, reverse=True)
            
            # Calculate percentages
            if total_size > 0:
                for child in children:
                    child.percentage = (child.size / total_size) * 100
            
            return total_size, item_count, children
        
        # Build the tree
        root_size, root_items, root_children = calculate_dir_size(directory)
        
        root = DiskItem(
            path=directory,
            name=os.path.basename(directory) or directory,
            size=root_size,
            is_dir=True,
            item_count=root_items,
            percentage=100.0,
            children=root_children
        )
        
        return root
    
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
