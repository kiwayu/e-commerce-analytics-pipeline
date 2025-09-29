"""
Checkpoint management for tracking processed files and maintaining state.
"""

import os
import json
import logging
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger(__name__)


@dataclass
class FileCheckpoint:
    """Represents a checkpoint entry for a processed file."""
    
    file_path: str
    file_size: int
    modification_time: float
    processing_time: float
    file_hash: str
    record_count: int
    status: str  # 'processed', 'failed', 'processing'
    error_message: Optional[str] = None
    batch_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileCheckpoint':
        """Create from dictionary."""
        return cls(**data)
    
    def is_changed(self, current_size: int, current_mtime: float, current_hash: str) -> bool:
        """Check if file has changed since last processing."""
        return (
            self.file_size != current_size or
            abs(self.modification_time - current_mtime) > 1.0 or  # 1 second tolerance
            self.file_hash != current_hash
        )


class CheckpointManager:
    """
    Manages checkpointing for incremental file processing.
    
    Tracks processed files, their metadata, and processing status to enable
    incremental loading and recovery from failures.
    """
    
    def __init__(self, checkpoint_dir: str, job_name: str = "file_ingestion"):
        self.checkpoint_dir = Path(checkpoint_dir)
        self.job_name = job_name
        self.checkpoint_file = self.checkpoint_dir / f"{job_name}_checkpoint.json"
        self.backup_file = self.checkpoint_dir / f"{job_name}_checkpoint_backup.json"
        
        # Ensure checkpoint directory exists
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory checkpoint state
        self._checkpoints: Dict[str, FileCheckpoint] = {}
        self._load_checkpoints()
    
    def _load_checkpoints(self):
        """Load checkpoints from persistent storage."""
        try:
            if self.checkpoint_file.exists():
                with open(self.checkpoint_file, 'r') as f:
                    data = json.load(f)
                    self._checkpoints = {
                        path: FileCheckpoint.from_dict(checkpoint_data)
                        for path, checkpoint_data in data.get('checkpoints', {}).items()
                    }
                logger.info(f"Loaded {len(self._checkpoints)} checkpoints from {self.checkpoint_file}")
            else:
                logger.info("No existing checkpoint file found, starting fresh")
                
        except Exception as e:
            logger.error(f"Error loading checkpoints: {e}")
            
            # Try to load from backup
            if self.backup_file.exists():
                try:
                    with open(self.backup_file, 'r') as f:
                        data = json.load(f)
                        self._checkpoints = {
                            path: FileCheckpoint.from_dict(checkpoint_data)
                            for path, checkpoint_data in data.get('checkpoints', {}).items()
                        }
                    logger.info(f"Restored from backup: {len(self._checkpoints)} checkpoints")
                except Exception as backup_error:
                    logger.error(f"Error loading backup checkpoints: {backup_error}")
                    self._checkpoints = {}
            else:
                self._checkpoints = {}
    
    def _save_checkpoints(self):
        """Save checkpoints to persistent storage."""
        try:
            # Create backup of current checkpoint file
            if self.checkpoint_file.exists():
                self.checkpoint_file.replace(self.backup_file)
            
            # Save current state
            checkpoint_data = {
                'job_name': self.job_name,
                'last_updated': datetime.now(timezone.utc).isoformat(),
                'checkpoints': {
                    path: checkpoint.to_dict()
                    for path, checkpoint in self._checkpoints.items()
                }
            }
            
            # Write to temporary file first, then rename for atomic operation
            temp_file = self.checkpoint_file.with_suffix('.tmp')
            with open(temp_file, 'w') as f:
                json.dump(checkpoint_data, f, indent=2)
            
            temp_file.replace(self.checkpoint_file)
            logger.debug(f"Saved {len(self._checkpoints)} checkpoints to {self.checkpoint_file}")
            
        except Exception as e:
            logger.error(f"Error saving checkpoints: {e}")
            raise
    
    def calculate_file_hash(self, file_path: str, chunk_size: int = 8192) -> str:
        """
        Calculate MD5 hash of file for change detection.
        
        Args:
            file_path: Path to the file
            chunk_size: Size of chunks to read for hashing
            
        Returns:
            MD5 hash as hex string
        """
        hash_md5 = hashlib.md5()
        try:
            with open(file_path, "rb") as f:
                for chunk in iter(lambda: f.read(chunk_size), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Could not calculate hash for {file_path}: {e}")
            return ""
    
    def get_files_to_process(self, input_dir: str, file_pattern: str = "*.csv") -> List[str]:
        """
        Get list of files that need to be processed based on checkpoint state.
        
        Args:
            input_dir: Directory to scan for files
            file_pattern: Glob pattern for file matching
            
        Returns:
            List of file paths that need processing
        """
        input_path = Path(input_dir)
        if not input_path.exists():
            logger.warning(f"Input directory does not exist: {input_dir}")
            return []
        
        all_files = list(input_path.glob(file_pattern))
        files_to_process = []
        
        for file_path in all_files:
            try:
                if not file_path.is_file():
                    continue
                
                file_str = str(file_path)
                file_stat = file_path.stat()
                current_size = file_stat.st_size
                current_mtime = file_stat.st_mtime
                
                # Skip empty files
                if current_size == 0:
                    logger.debug(f"Skipping empty file: {file_str}")
                    continue
                
                # Check if file exists in checkpoints
                if file_str in self._checkpoints:
                    checkpoint = self._checkpoints[file_str]
                    
                    # Skip if already processed successfully and unchanged
                    if checkpoint.status == 'processed':
                        current_hash = self.calculate_file_hash(file_str)
                        if not checkpoint.is_changed(current_size, current_mtime, current_hash):
                            logger.debug(f"File unchanged, skipping: {file_str}")
                            continue
                        else:
                            logger.info(f"File changed, will reprocess: {file_str}")
                    
                    # Retry failed files
                    elif checkpoint.status == 'failed':
                        logger.info(f"Retrying previously failed file: {file_str}")
                    
                    # Skip files currently being processed (unless stale)
                    elif checkpoint.status == 'processing':
                        processing_age = datetime.now(timezone.utc).timestamp() - checkpoint.processing_time
                        if processing_age < 3600:  # 1 hour timeout
                            logger.debug(f"File currently being processed, skipping: {file_str}")
                            continue
                        else:
                            logger.warning(f"Stale processing state, will retry: {file_str}")
                
                files_to_process.append(file_str)
                
            except Exception as e:
                logger.error(f"Error checking file {file_path}: {e}")
                continue
        
        logger.info(f"Found {len(files_to_process)} files to process out of {len(all_files)} total files")
        return files_to_process
    
    def mark_file_processing(self, file_path: str, batch_id: str):
        """
        Mark a file as currently being processed.
        
        Args:
            file_path: Path to the file being processed
            batch_id: Batch ID for tracking
        """
        try:
            file_stat = Path(file_path).stat()
            file_hash = self.calculate_file_hash(file_path)
            
            checkpoint = FileCheckpoint(
                file_path=file_path,
                file_size=file_stat.st_size,
                modification_time=file_stat.st_mtime,
                processing_time=datetime.now(timezone.utc).timestamp(),
                file_hash=file_hash,
                record_count=0,
                status='processing',
                batch_id=batch_id
            )
            
            self._checkpoints[file_path] = checkpoint
            self._save_checkpoints()
            
            logger.debug(f"Marked file as processing: {file_path}")
            
        except Exception as e:
            logger.error(f"Error marking file as processing {file_path}: {e}")
            raise
    
    def mark_file_processed(self, file_path: str, record_count: int, batch_id: str):
        """
        Mark a file as successfully processed.
        
        Args:
            file_path: Path to the processed file
            record_count: Number of records processed
            batch_id: Batch ID for tracking
        """
        try:
            if file_path in self._checkpoints:
                checkpoint = self._checkpoints[file_path]
                checkpoint.status = 'processed'
                checkpoint.record_count = record_count
                checkpoint.error_message = None
                checkpoint.processing_time = datetime.now(timezone.utc).timestamp()
            else:
                # Create new checkpoint if it doesn't exist
                file_stat = Path(file_path).stat()
                file_hash = self.calculate_file_hash(file_path)
                
                checkpoint = FileCheckpoint(
                    file_path=file_path,
                    file_size=file_stat.st_size,
                    modification_time=file_stat.st_mtime,
                    processing_time=datetime.now(timezone.utc).timestamp(),
                    file_hash=file_hash,
                    record_count=record_count,
                    status='processed',
                    batch_id=batch_id
                )
                
                self._checkpoints[file_path] = checkpoint
            
            self._save_checkpoints()
            logger.info(f"Marked file as processed: {file_path} ({record_count} records)")
            
        except Exception as e:
            logger.error(f"Error marking file as processed {file_path}: {e}")
            raise
    
    def mark_file_failed(self, file_path: str, error_message: str, batch_id: str):
        """
        Mark a file as failed to process.
        
        Args:
            file_path: Path to the failed file
            error_message: Error description
            batch_id: Batch ID for tracking
        """
        try:
            if file_path in self._checkpoints:
                checkpoint = self._checkpoints[file_path]
                checkpoint.status = 'failed'
                checkpoint.error_message = error_message
                checkpoint.processing_time = datetime.now(timezone.utc).timestamp()
            else:
                # Create new checkpoint for failed file
                try:
                    file_stat = Path(file_path).stat()
                    file_hash = self.calculate_file_hash(file_path)
                except:
                    file_stat = None
                    file_hash = ""
                
                checkpoint = FileCheckpoint(
                    file_path=file_path,
                    file_size=file_stat.st_size if file_stat else 0,
                    modification_time=file_stat.st_mtime if file_stat else 0,
                    processing_time=datetime.now(timezone.utc).timestamp(),
                    file_hash=file_hash,
                    record_count=0,
                    status='failed',
                    error_message=error_message,
                    batch_id=batch_id
                )
                
                self._checkpoints[file_path] = checkpoint
            
            self._save_checkpoints()
            logger.error(f"Marked file as failed: {file_path} - {error_message}")
            
        except Exception as e:
            logger.error(f"Error marking file as failed {file_path}: {e}")
            raise
    
    def get_checkpoint_stats(self) -> Dict[str, Any]:
        """Get statistics about current checkpoint state."""
        total_files = len(self._checkpoints)
        processed_count = sum(1 for cp in self._checkpoints.values() if cp.status == 'processed')
        failed_count = sum(1 for cp in self._checkpoints.values() if cp.status == 'failed')
        processing_count = sum(1 for cp in self._checkpoints.values() if cp.status == 'processing')
        total_records = sum(cp.record_count for cp in self._checkpoints.values() if cp.status == 'processed')
        
        return {
            'total_files': total_files,
            'processed_files': processed_count,
            'failed_files': failed_count,
            'processing_files': processing_count,
            'total_records_processed': total_records,
            'success_rate': processed_count / total_files if total_files > 0 else 0.0,
            'checkpoint_file': str(self.checkpoint_file),
            'last_checkpoint_size': len(self._checkpoints)
        }
    
    def get_failed_files(self) -> List[Dict[str, Any]]:
        """Get list of files that failed processing."""
        failed_files = []
        for file_path, checkpoint in self._checkpoints.items():
            if checkpoint.status == 'failed':
                failed_files.append({
                    'file_path': file_path,
                    'error_message': checkpoint.error_message,
                    'processing_time': checkpoint.processing_time,
                    'batch_id': checkpoint.batch_id
                })
        return failed_files
    
    def reset_failed_files(self):
        """Reset failed files to allow reprocessing."""
        reset_count = 0
        for checkpoint in self._checkpoints.values():
            if checkpoint.status == 'failed':
                checkpoint.status = 'processing'
                checkpoint.error_message = None
                reset_count += 1
        
        if reset_count > 0:
            self._save_checkpoints()
            logger.info(f"Reset {reset_count} failed files for reprocessing")
    
    def cleanup_old_checkpoints(self, retention_days: int = 30):
        """
        Remove checkpoints for files that no longer exist or are very old.
        
        Args:
            retention_days: Number of days to retain checkpoints
        """
        current_time = datetime.now(timezone.utc).timestamp()
        retention_seconds = retention_days * 24 * 3600
        
        files_to_remove = []
        
        for file_path, checkpoint in self._checkpoints.items():
            # Remove if file no longer exists
            if not Path(file_path).exists():
                files_to_remove.append(file_path)
                continue
            
            # Remove if very old and processed
            if (checkpoint.status == 'processed' and 
                (current_time - checkpoint.processing_time) > retention_seconds):
                files_to_remove.append(file_path)
        
        for file_path in files_to_remove:
            del self._checkpoints[file_path]
        
        if files_to_remove:
            self._save_checkpoints()
            logger.info(f"Cleaned up {len(files_to_remove)} old checkpoint entries")
    
    def export_checkpoints(self, export_path: str):
        """Export checkpoints to a file for backup or analysis."""
        try:
            export_data = {
                'job_name': self.job_name,
                'export_time': datetime.now(timezone.utc).isoformat(),
                'stats': self.get_checkpoint_stats(),
                'checkpoints': {
                    path: checkpoint.to_dict()
                    for path, checkpoint in self._checkpoints.items()
                }
            }
            
            with open(export_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            logger.info(f"Exported {len(self._checkpoints)} checkpoints to {export_path}")
            
        except Exception as e:
            logger.error(f"Error exporting checkpoints: {e}")
            raise
