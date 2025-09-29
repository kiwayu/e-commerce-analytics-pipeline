"""
File monitoring and change detection utilities for incremental processing.
"""

import os
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timezone
from dataclasses import dataclass
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class FileInfo:
    """Information about a file for change detection."""
    
    path: str
    size: int
    modification_time: float
    creation_time: float
    hash_md5: Optional[str] = None
    is_readable: bool = True
    error_message: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'path': self.path,
            'size': self.size,
            'modification_time': self.modification_time,
            'creation_time': self.creation_time,
            'hash_md5': self.hash_md5,
            'is_readable': self.is_readable,
            'error_message': self.error_message
        }
    
    @classmethod
    def from_file(cls, file_path: str, calculate_hash: bool = True) -> 'FileInfo':
        """
        Create FileInfo from a file path.
        
        Args:
            file_path: Path to the file
            calculate_hash: Whether to calculate MD5 hash
            
        Returns:
            FileInfo instance
        """
        try:
            path_obj = Path(file_path)
            stat_info = path_obj.stat()
            
            file_info = cls(
                path=str(path_obj.absolute()),
                size=stat_info.st_size,
                modification_time=stat_info.st_mtime,
                creation_time=stat_info.st_ctime,
                is_readable=os.access(file_path, os.R_OK)
            )
            
            # Calculate hash if requested and file is readable
            if calculate_hash and file_info.is_readable and file_info.size > 0:
                try:
                    file_info.hash_md5 = cls._calculate_file_hash(file_path)
                except Exception as e:
                    logger.warning(f"Could not calculate hash for {file_path}: {e}")
                    file_info.hash_md5 = None
            
            return file_info
            
        except Exception as e:
            logger.error(f"Error getting file info for {file_path}: {e}")
            return cls(
                path=file_path,
                size=0,
                modification_time=0,
                creation_time=0,
                is_readable=False,
                error_message=str(e)
            )
    
    @staticmethod
    def _calculate_file_hash(file_path: str, chunk_size: int = 8192) -> str:
        """Calculate MD5 hash of file."""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    
    def has_changed(self, other: 'FileInfo', tolerance_seconds: float = 1.0) -> bool:
        """
        Check if this file has changed compared to another FileInfo.
        
        Args:
            other: Other FileInfo to compare against
            tolerance_seconds: Tolerance for modification time comparison
            
        Returns:
            True if file has changed
        """
        # Size changed
        if self.size != other.size:
            return True
        
        # Modification time changed (with tolerance)
        if abs(self.modification_time - other.modification_time) > tolerance_seconds:
            return True
        
        # Hash changed (if both have hashes)
        if self.hash_md5 and other.hash_md5 and self.hash_md5 != other.hash_md5:
            return True
        
        return False


class FileMonitor:
    """
    Monitors files for changes and provides incremental processing capabilities.
    """
    
    def __init__(self, input_directory: str, file_patterns: List[str] = None):
        """
        Initialize file monitor.
        
        Args:
            input_directory: Directory to monitor
            file_patterns: List of glob patterns to match files (default: ['*.csv'])
        """
        self.input_directory = Path(input_directory)
        self.file_patterns = file_patterns or ['*.csv']
        
        if not self.input_directory.exists():
            logger.warning(f"Input directory does not exist: {input_directory}")
    
    def scan_files(self, calculate_hashes: bool = False) -> List[FileInfo]:
        """
        Scan directory for files matching patterns.
        
        Args:
            calculate_hashes: Whether to calculate file hashes
            
        Returns:
            List of FileInfo objects
        """
        files = []
        
        if not self.input_directory.exists():
            logger.warning(f"Directory does not exist: {self.input_directory}")
            return files
        
        for pattern in self.file_patterns:
            try:
                matching_files = list(self.input_directory.glob(pattern))
                
                for file_path in matching_files:
                    if file_path.is_file():
                        file_info = FileInfo.from_file(str(file_path), calculate_hashes)
                        files.append(file_info)
                        
            except Exception as e:
                logger.error(f"Error scanning files with pattern {pattern}: {e}")
        
        logger.info(f"Found {len(files)} files in {self.input_directory}")
        return files
    
    def get_new_and_changed_files(
        self, 
        current_files: List[FileInfo], 
        previous_files: Dict[str, FileInfo],
        tolerance_seconds: float = 1.0
    ) -> Tuple[List[FileInfo], List[FileInfo], List[str]]:
        """
        Compare current files with previous scan to find changes.
        
        Args:
            current_files: Current file scan results
            previous_files: Previous file scan results (dict by path)
            tolerance_seconds: Tolerance for modification time comparison
            
        Returns:
            Tuple of (new_files, changed_files, deleted_files)
        """
        new_files = []
        changed_files = []
        deleted_files = []
        
        current_paths = {f.path for f in current_files}
        previous_paths = set(previous_files.keys())
        
        # Find new files
        for file_info in current_files:
            if file_info.path not in previous_paths:
                new_files.append(file_info)
                logger.debug(f"New file detected: {file_info.path}")
        
        # Find changed files
        for file_info in current_files:
            if file_info.path in previous_paths:
                previous_info = previous_files[file_info.path]
                if file_info.has_changed(previous_info, tolerance_seconds):
                    changed_files.append(file_info)
                    logger.debug(f"Changed file detected: {file_info.path}")
        
        # Find deleted files
        for path in previous_paths:
            if path not in current_paths:
                deleted_files.append(path)
                logger.debug(f"Deleted file detected: {path}")
        
        logger.info(
            f"File changes detected - New: {len(new_files)}, "
            f"Changed: {len(changed_files)}, Deleted: {len(deleted_files)}"
        )
        
        return new_files, changed_files, deleted_files
    
    def filter_processable_files(
        self, 
        files: List[FileInfo], 
        min_size: int = 1,
        max_size: Optional[int] = None,
        age_limit_hours: Optional[float] = None
    ) -> List[FileInfo]:
        """
        Filter files based on processing criteria.
        
        Args:
            files: List of files to filter
            min_size: Minimum file size in bytes
            max_size: Maximum file size in bytes (None for no limit)
            age_limit_hours: Maximum file age in hours (None for no limit)
            
        Returns:
            Filtered list of files
        """
        filtered_files = []
        current_time = datetime.now(timezone.utc).timestamp()
        
        for file_info in files:
            # Skip if file has errors
            if not file_info.is_readable:
                logger.warning(f"Skipping unreadable file: {file_info.path}")
                continue
            
            # Check size limits
            if file_info.size < min_size:
                logger.debug(f"Skipping file too small: {file_info.path} ({file_info.size} bytes)")
                continue
            
            if max_size and file_info.size > max_size:
                logger.warning(f"Skipping file too large: {file_info.path} ({file_info.size} bytes)")
                continue
            
            # Check age limit
            if age_limit_hours:
                file_age_hours = (current_time - file_info.modification_time) / 3600
                if file_age_hours > age_limit_hours:
                    logger.debug(f"Skipping old file: {file_info.path} ({file_age_hours:.1f} hours old)")
                    continue
            
            filtered_files.append(file_info)
        
        logger.info(f"Filtered {len(filtered_files)} processable files from {len(files)} total")
        return filtered_files
    
    def sort_files_by_priority(
        self, 
        files: List[FileInfo], 
        priority_mode: str = 'oldest_first'
    ) -> List[FileInfo]:
        """
        Sort files by processing priority.
        
        Args:
            files: List of files to sort
            priority_mode: Sorting mode ('oldest_first', 'newest_first', 'smallest_first', 'largest_first')
            
        Returns:
            Sorted list of files
        """
        if priority_mode == 'oldest_first':
            sorted_files = sorted(files, key=lambda f: f.modification_time)
        elif priority_mode == 'newest_first':
            sorted_files = sorted(files, key=lambda f: f.modification_time, reverse=True)
        elif priority_mode == 'smallest_first':
            sorted_files = sorted(files, key=lambda f: f.size)
        elif priority_mode == 'largest_first':
            sorted_files = sorted(files, key=lambda f: f.size, reverse=True)
        else:
            logger.warning(f"Unknown priority mode: {priority_mode}, using oldest_first")
            sorted_files = sorted(files, key=lambda f: f.modification_time)
        
        logger.debug(f"Sorted {len(files)} files by {priority_mode}")
        return sorted_files
    
    def get_file_statistics(self, files: List[FileInfo]) -> Dict[str, Any]:
        """
        Get statistics about a list of files.
        
        Args:
            files: List of files to analyze
            
        Returns:
            Dictionary with file statistics
        """
        if not files:
            return {
                'total_files': 0,
                'total_size_bytes': 0,
                'avg_size_bytes': 0,
                'min_size_bytes': 0,
                'max_size_bytes': 0,
                'oldest_file': None,
                'newest_file': None
            }
        
        sizes = [f.size for f in files]
        mod_times = [f.modification_time for f in files]
        
        oldest_file = min(files, key=lambda f: f.modification_time)
        newest_file = max(files, key=lambda f: f.modification_time)
        
        return {
            'total_files': len(files),
            'total_size_bytes': sum(sizes),
            'avg_size_bytes': sum(sizes) // len(sizes),
            'min_size_bytes': min(sizes),
            'max_size_bytes': max(sizes),
            'oldest_file': {
                'path': oldest_file.path,
                'modification_time': oldest_file.modification_time,
                'age_hours': (datetime.now(timezone.utc).timestamp() - oldest_file.modification_time) / 3600
            },
            'newest_file': {
                'path': newest_file.path,
                'modification_time': newest_file.modification_time,
                'age_hours': (datetime.now(timezone.utc).timestamp() - newest_file.modification_time) / 3600
            }
        }


class IncrementalFileProcessor:
    """
    Coordinates file monitoring with checkpoint management for incremental processing.
    """
    
    def __init__(
        self, 
        input_directory: str,
        checkpoint_manager,  # CheckpointManager instance
        file_patterns: List[str] = None,
        processing_config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize incremental file processor.
        
        Args:
            input_directory: Directory containing files to process
            checkpoint_manager: CheckpointManager instance
            file_patterns: File patterns to match
            processing_config: Configuration for file processing
        """
        self.file_monitor = FileMonitor(input_directory, file_patterns)
        self.checkpoint_manager = checkpoint_manager
        
        # Default processing configuration
        default_config = {
            'min_file_size': 1,
            'max_file_size': None,
            'age_limit_hours': None,
            'priority_mode': 'oldest_first',
            'calculate_hashes': True,
            'max_files_per_batch': 100
        }
        
        self.config = {**default_config, **(processing_config or {})}
    
    def get_files_to_process(self) -> List[str]:
        """
        Get list of files that need to be processed based on file monitoring and checkpoints.
        
        Returns:
            List of file paths to process
        """
        logger.info("Scanning for files to process...")
        
        # Scan current files
        current_files = self.file_monitor.scan_files(
            calculate_hashes=self.config['calculate_hashes']
        )
        
        # Filter processable files
        processable_files = self.file_monitor.filter_processable_files(
            current_files,
            min_size=self.config['min_file_size'],
            max_size=self.config['max_file_size'],
            age_limit_hours=self.config['age_limit_hours']
        )
        
        # Sort by priority
        sorted_files = self.file_monitor.sort_files_by_priority(
            processable_files,
            self.config['priority_mode']
        )
        
        # Use checkpoint manager to filter out already processed files
        file_paths = [f.path for f in sorted_files]
        files_to_process = self.checkpoint_manager.get_files_to_process(
            self.file_monitor.input_directory,
            "*.csv"  # This will be overridden by file_paths
        )
        
        # Intersection of files found by monitor and checkpoint manager
        final_files = [f for f in file_paths if f in files_to_process or f not in [cp.file_path for cp in self.checkpoint_manager._checkpoints.values() if cp.status == 'processed']]
        
        # Limit batch size
        if self.config['max_files_per_batch']:
            final_files = final_files[:self.config['max_files_per_batch']]
        
        # Log statistics
        stats = self.file_monitor.get_file_statistics(
            [f for f in sorted_files if f.path in final_files]
        )
        
        logger.info(f"Selected {len(final_files)} files for processing")
        logger.info(f"Total size: {stats.get('total_size_bytes', 0)} bytes")
        
        return final_files
    
    def validate_file_for_processing(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that a file is ready for processing.
        
        Args:
            file_path: Path to the file to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            path_obj = Path(file_path)
            
            # Check if file exists
            if not path_obj.exists():
                return False, "File does not exist"
            
            # Check if it's a file (not directory)
            if not path_obj.is_file():
                return False, "Path is not a file"
            
            # Check if file is readable
            if not os.access(file_path, os.R_OK):
                return False, "File is not readable"
            
            # Check file size
            file_size = path_obj.stat().st_size
            if file_size == 0:
                return False, "File is empty"
            
            if self.config['max_file_size'] and file_size > self.config['max_file_size']:
                return False, f"File too large: {file_size} bytes"
            
            # Try to open file to ensure it's not locked
            try:
                with open(file_path, 'r') as f:
                    f.read(1)  # Read first character
            except Exception as e:
                return False, f"Cannot read file: {str(e)}"
            
            return True, None
            
        except Exception as e:
            return False, f"Validation error: {str(e)}"
