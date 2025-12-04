"""
Duplicate file finder using hash-based content comparison
Efficiently detects files with identical content
"""
import os
import hashlib
from typing import Dict, List, Tuple
from dataclasses import dataclass
from collections import defaultdict
from utils.scanner import FileInfo, Scanner



@dataclass
class DuplicateGroup:
    """Group of duplicate files"""
    hash: str
    files: List[FileInfo]
    total_size: int
    
    def get_wasted_space(self) -> int:
        """Calculate wasted space (size of all duplicates except one)"""
        if len(self.files) <= 1:
            return 0
        return self.total_size - self.files[0].size


class DuplicateFinder:
    """Find duplicate files based on content hash"""
    
    def __init__(self, excluded_paths: List[str] = None, min_size: int = 0):
        """
        Initialize duplicate finder
        
        Args:
            excluded_paths: Paths to exclude from scanning
            min_size: Minimum file size to consider (bytes)
        """
        self.scanner = Scanner(excluded_paths)
        self.min_size = min_size
        self.duplicates = {}
        self.scanned_files = 0
        self.total_wasted_space = 0
    
    def calculate_hash(self, filepath: str, chunk_size: int = 8192) -> str:
        """
        Calculate SHA256 hash of file content
        
        Args:
            filepath: Path to file
            chunk_size: Size of chunks to read
        
        Returns:
            Hexadecimal hash string
        """
        sha256 = hashlib.sha256()
        try:
            with open(filepath, 'rb') as f:
                while True:
                    chunk = f.read(chunk_size)
                    if not chunk:
                        break
                    sha256.update(chunk)
            return sha256.hexdigest()
        except (OSError, PermissionError):
            return None
    
    def find_duplicates(
        self,
        directories: List[str],
        callback=None
    ) -> Dict[str, DuplicateGroup]:
        """
        Find duplicate files in given directories
        
        Args:
            directories: List of directories to scan
            callback: Progress callback(current_file, count)
        
        Returns:
            Dictionary mapping hash to DuplicateGroup
        """
        # First pass: Group files by size (quick filter)
        size_groups = defaultdict(list)
        
        for directory in directories:
            if not os.path.exists(directory):
                continue
            
            files = self.scanner.scan_directory(directory, recursive=True)
            
            for file_info in files:
                if file_info.size >= self.min_size:
                    size_groups[file_info.size].append(file_info)
        
        # Second pass: Calculate hashes only for files with same size
        hash_groups = defaultdict(list)
        self.scanned_files = 0
        
        for size, files in size_groups.items():
            if len(files) < 2:
                # Skip files with unique size
                continue
            
            for file_info in files:
                file_hash = self.calculate_hash(file_info.path)
                if file_hash:
                    hash_groups[file_hash].append(file_info)
                    self.scanned_files += 1
                    
                    if callback:
                        callback(file_info.path, self.scanned_files)
        
        # Third pass: Keep only actual duplicates (hash appears multiple times)
        self.duplicates = {}
        self.total_wasted_space = 0
        
        for file_hash, files in hash_groups.items():
            if len(files) > 1:
                # Sort by modification date (keep oldest first)
                files.sort(key=lambda f: f.modified)
                
                total_size = sum(f.size for f in files)
                group = DuplicateGroup(
                    hash=file_hash,
                    files=files,
                    total_size=total_size
                )
                self.duplicates[file_hash] = group
                self.total_wasted_space += group.get_wasted_space()
        
        return self.duplicates
    
    def get_statistics(self) -> Dict[str, any]:
        """Get duplicate statistics"""
        total_duplicates = sum(len(group.files) - 1 for group in self.duplicates.values())
        total_groups = len(self.duplicates)
        
        return {
            'total_groups': total_groups,
            'total_duplicate_files': total_duplicates,
            'wasted_space_bytes': self.total_wasted_space,
            'wasted_space_formatted': Scanner.format_size(self.total_wasted_space),
            'scanned_files': self.scanned_files
        }
    
    def get_suggestions(self, group: DuplicateGroup) -> List[Tuple[FileInfo, str]]:
        """
        Get suggestions on which files to keep/delete
        
        Returns:
            List of (FileInfo, suggestion) tuples
            suggestion can be: 'keep_original', 'delete_duplicate'
        """
        suggestions = []
        
        for i, file_info in enumerate(group.files):
            if i == 0:
                # Keep the oldest file (first in sorted list)
                suggestions.append((file_info, 'keep_original'))
            else:
                suggestions.append((file_info, 'delete_duplicate'))
        
        return suggestions
