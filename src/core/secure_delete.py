"""
Secure file deletion with multiple overwrite passes
Implements DOD 5220.22-M and Gutmann methods
"""
import os
import random
from typing import Callable, Optional


class SecureDelete:
    """Secure file deletion with multiple overwrite passes"""
    
    # Gutmann patterns (simplified - using key patterns)
    GUTMANN_PATTERNS = [
        b'\x55' * 512,  # Pattern 1
        b'\xAA' * 512,  # Pattern 2
        b'\x92\x49\x24' * 171,  # Pattern 3
        b'\x49\x24\x92' * 171,  # Pattern 4
        b'\x24\x92\x49' * 171,  # Pattern 5
        b'\x00' * 512,  # Pattern 6
        b'\x11' * 512,  # Pattern 7
        b'\x22' * 512,  # Pattern 8
        b'\x33' * 512,  # Pattern 9
        b'\x44' * 512,  # Pattern 10
        b'\x55' * 512,  # Pattern 11
        b'\x66' * 512,  # Pattern 12
        b'\x77' * 512,  # Pattern 13
        b'\x88' * 512,  # Pattern 14
        b'\x99' * 512,  # Pattern 15
        b'\xAA' * 512,  # Pattern 16
        b'\xBB' * 512,  # Pattern 17
        b'\xCC' * 512,  # Pattern 18
        b'\xDD' * 512,  # Pattern 19
        b'\xEE' * 512,  # Pattern 20
        b'\xFF' * 512,  # Pattern 21
    ]
    
    def __init__(self):
        """Initialize secure delete"""
        pass
    
    def _overwrite_file(
        self,
        filepath: str,
        pattern: bytes,
        callback: Optional[Callable[[int, int], None]] = None
    ) -> bool:
        """
        Overwrite file with specific pattern
        
        Args:
            filepath: Path to file
            pattern: Byte pattern to write
            callback: Progress callback(current_byte, total_bytes)
        
        Returns:
            True if successful
        """
        try:
            file_size = os.path.getsize(filepath)
            
            with open(filepath, 'rb+') as f:
                bytes_written = 0
                chunk_size = len(pattern)
                
                while bytes_written < file_size:
                    remaining = file_size - bytes_written
                    write_size = min(chunk_size, remaining)
                    
                    f.write(pattern[:write_size])
                    bytes_written += write_size
                    
                    if callback:
                        callback(bytes_written, file_size)
                
                # Flush to disk
                f.flush()
                os.fsync(f.fileno())
            
            return True
        
        except (OSError, PermissionError):
            return False
    
    def _random_pattern(self, size: int = 512) -> bytes:
        """Generate random byte pattern"""
        return bytes(random.randint(0, 255) for _ in range(size))
    
    def secure_delete_file(
        self,
        filepath: str,
        passes: int = 3,
        callback: Optional[Callable[[int, int, str], None]] = None
    ) -> bool:
        """
        Securely delete file with multiple overwrite passes
        
        Args:
            filepath: Path to file to delete
            passes: Number of overwrite passes (1, 3, 7, or 35 for Gutmann)
            callback: Progress callback(current_pass, total_passes, status)
        
        Returns:
            True if file was successfully deleted
        """
        if not os.path.exists(filepath) or not os.path.isfile(filepath):
            return False
        
        try:
            file_size = os.path.getsize(filepath)
            
            # Determine patterns based on passes
            if passes == 1:
                patterns = [self._random_pattern()]
            elif passes == 3:
                # DOD 5220.22-M standard
                patterns = [
                    b'\x00' * 512,  # Pass 1: zeros
                    b'\xFF' * 512,  # Pass 2: ones
                    self._random_pattern()  # Pass 3: random
                ]
            elif passes == 7:
                # Extended DOD
                patterns = [
                    self._random_pattern(),
                    self._random_pattern(),
                    b'\x00' * 512,
                    b'\xFF' * 512,
                    self._random_pattern(),
                    self._random_pattern(),
                    self._random_pattern()
                ]
            elif passes == 35:
                # Gutmann method (simplified)
                patterns = (
                    [self._random_pattern() for _ in range(4)] +
                    self.GUTMANN_PATTERNS +
                    [self._random_pattern() for _ in range(10)]
                )
            else:
                # Default to 3 passes
                patterns = [self._random_pattern() for _ in range(passes)]
            
            # Perform overwrite passes
            for i, pattern in enumerate(patterns):
                if callback:
                    callback(i + 1, len(patterns), f"Overwriting pass {i + 1}/{len(patterns)}")
                
                success = self._overwrite_file(filepath, pattern)
                if not success:
                    return False
            
            # Rename file to random name before deletion
            directory = os.path.dirname(filepath)
            random_name = ''.join(random.choices('0123456789abcdef', k=16))
            new_path = os.path.join(directory, random_name)
            
            try:
                os.rename(filepath, new_path)
                filepath = new_path
            except OSError:
                pass  # Continue with original name if rename fails
            
            # Finally delete the file
            os.remove(filepath)
            
            if callback:
                callback(len(patterns), len(patterns), "File deleted")
            
            return True
        
        except (OSError, PermissionError) as e:
            if callback:
                callback(0, passes, f"Error: {str(e)}")
            return False
    
    def secure_delete_folder(
        self,
        folderpath: str,
        passes: int = 3,
        callback: Optional[Callable[[str, int, int], None]] = None
    ) -> bool:
        """
        Securely delete all files in folder
        
        Args:
            folderpath: Path to folder
            passes: Number of overwrite passes
            callback: Progress callback(current_file, file_index, total_files)
        
        Returns:
            True if all files were deleted
        """
        if not os.path.exists(folderpath) or not os.path.isdir(folderpath):
            return False
        
        # Collect all files
        all_files = []
        for root, dirs, files in os.walk(folderpath):
            for filename in files:
                all_files.append(os.path.join(root, filename))
        
        total_files = len(all_files)
        success_count = 0
        
        # Delete each file
        for i, filepath in enumerate(all_files):
            if callback:
                callback(filepath, i + 1, total_files)
            
            if self.secure_delete_file(filepath, passes):
                success_count += 1
        
        # Remove empty directories
        try:
            for root, dirs, files in os.walk(folderpath, topdown=False):
                for dirname in dirs:
                    dirpath = os.path.join(root, dirname)
                    try:
                        os.rmdir(dirpath)
                    except OSError:
                        pass
            
            # Remove root folder
            os.rmdir(folderpath)
        except OSError:
            pass
        
        return success_count == total_files
