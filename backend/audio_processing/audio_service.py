"""
Integrated audio processing service for MiDiMe.

This module provides a high-level service that orchestrates the complete
audio processing workflow: validation → trimming → stem separation → cleanup.
"""

import os
import logging
import uuid
from typing import Dict, Optional
from pathlib import Path

from .utils import trim_audio, validate_audio_file, get_audio_info
from .stem_separator import separate_stems, cleanup_stems

logger = logging.getLogger(__name__)


class AudioProcessingResult:
    """Result object containing paths and metadata from audio processing."""
    
    def __init__(
        self,
        success: bool,
        stem_paths: Optional[Dict[str, str]] = None,
        metadata: Optional[dict] = None,
        error: Optional[str] = None
    ):
        self.success = success
        self.stem_paths = stem_paths or {}
        self.metadata = metadata or {}
        self.error = error
    
    def to_dict(self) -> dict:
        """Convert result to dictionary format."""
        return {
            'success': self.success,
            'stem_paths': self.stem_paths,
            'metadata': self.metadata,
            'error': self.error
        }


def process_audio_snippet(
    audio_path: str,
    start_time_seconds: float,
    end_time_seconds: float,
    output_base_dir: str,
    extract_stems: bool = True,
    cleanup_after: bool = True
) -> AudioProcessingResult:
    """
    Process an audio snippet through the complete workflow.
    
    This is the main entry point for audio processing. It handles:
    1. Validation
    2. Trimming to user-selected time range
    3. Stem separation (optional)
    4. Cleanup of temporary files (optional)
    
    Args:
        audio_path: Path to the uploaded audio file
        start_time_seconds: Start time of snippet in seconds
        end_time_seconds: End time of snippet in seconds
        output_base_dir: Base directory for output files
        extract_stems: Whether to extract stems (default: True)
        cleanup_after: Whether to cleanup temporary files (default: True)
    
    Returns:
        AudioProcessingResult containing stem paths and metadata
    
    Example:
        >>> result = process_audio_snippet(
        ...     "uploads/song.mp3",
        ...     30.5,
        ...     45.5,
        ...     "storage/processed"
        ... )
        >>> if result.success:
        ...     print(f"Drums: {result.stem_paths['drums']}")
    """
    temp_files = []  # Track temporary files for cleanup
    
    try:
        # Step 1: Validate audio file
        logger.info(f"Processing audio snippet: {audio_path}")
        is_valid, error_msg = validate_audio_file(audio_path)
        
        if not is_valid:
            return AudioProcessingResult(
                success=False,
                error=f"Validation failed: {error_msg}"
            )
        
        # Get original audio info
        original_info = get_audio_info(audio_path)
        logger.info(
            f"Original audio: {original_info['duration_seconds']:.2f}s, "
            f"{original_info['format']}, {original_info['file_size_mb']} MB"
        )
        
        # Step 2: Trim audio to selected snippet
        logger.info(f"Trimming audio: {start_time_seconds:.2f}s - {end_time_seconds:.2f}s")
        
        # Generate unique filename for trimmed audio
        snippet_id = str(uuid.uuid4())[:8]
        trimmed_dir = os.path.join(output_base_dir, "trimmed")
        os.makedirs(trimmed_dir, exist_ok=True)
        
        trimmed_path = os.path.join(trimmed_dir, f"snippet_{snippet_id}.wav")
        
        try:
            trimmed_path = trim_audio(
                audio_path,
                trimmed_path,
                start_time_seconds,
                end_time_seconds,
                format="wav"
            )
            temp_files.append(trimmed_path)
            
        except ValueError as e:
            return AudioProcessingResult(
                success=False,
                error=f"Trimming failed: {str(e)}"
            )
        
        # Get trimmed audio info
        trimmed_info = get_audio_info(trimmed_path)
        snippet_duration = trimmed_info['duration_seconds']
        logger.info(f"Trimmed snippet: {snippet_duration:.2f}s")
        
        # Step 3: Extract stems (if requested)
        stem_paths = {}
        
        if extract_stems:
            logger.info("Extracting stems...")
            stems_dir = os.path.join(output_base_dir, "stems")
            os.makedirs(stems_dir, exist_ok=True)
            
            try:
                stem_paths = separate_stems(
                    trimmed_path,
                    stems_dir,
                    model="spleeter:4stems",
                    codec="wav"
                )
                
                logger.info(f"Successfully extracted {len(stem_paths)} stems")
                
            except Exception as e:
                return AudioProcessingResult(
                    success=False,
                    error=f"Stem separation failed: {str(e)}"
                )
        
        # Step 4: Prepare metadata
        metadata = {
            'snippet_id': snippet_id,
            'original_file': Path(audio_path).name,
            'original_duration_seconds': original_info['duration_seconds'],
            'snippet_duration_seconds': snippet_duration,
            'start_time': start_time_seconds,
            'end_time': end_time_seconds,
            'sample_rate': trimmed_info['sample_rate'],
            'channels': trimmed_info['channels'],
            'stems_extracted': extract_stems,
            'num_stems': len(stem_paths)
        }
        
        # Step 5: Cleanup temporary files (if requested)
        if cleanup_after:
            logger.info("Cleaning up temporary files...")
            
            # Remove trimmed file
            if os.path.exists(trimmed_path):
                try:
                    os.remove(trimmed_path)
                    logger.info(f"Removed temporary file: {trimmed_path}")
                except OSError as e:
                    logger.warning(f"Failed to remove {trimmed_path}: {e}")
        
        # Return successful result
        return AudioProcessingResult(
            success=True,
            stem_paths=stem_paths,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Audio processing failed: {str(e)}")
        
        # Cleanup on error
        if cleanup_after:
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except OSError:
                        pass
        
        return AudioProcessingResult(
            success=False,
            error=f"Processing error: {str(e)}"
        )


def get_drum_pattern(
    audio_path: str,
    start_time_seconds: float,
    end_time_seconds: float,
    output_base_dir: str
) -> AudioProcessingResult:
    """
    Convenience function to extract only the drum stem.
    
    This is a simplified wrapper around process_audio_snippet() that
    focuses on drum extraction for the MVP.
    
    Args:
        audio_path: Path to the uploaded audio file
        start_time_seconds: Start time of snippet
        end_time_seconds: End time of snippet
        output_base_dir: Base directory for output files
    
    Returns:
        AudioProcessingResult with drum stem path
    """
    logger.info("Extracting drum pattern...")
    
    result = process_audio_snippet(
        audio_path,
        start_time_seconds,
        end_time_seconds,
        output_base_dir,
        extract_stems=True,
        cleanup_after=True
    )
    
    if result.success and 'drums' in result.stem_paths:
        logger.info(f"Drum stem extracted: {result.stem_paths['drums']}")
    
    return result


def cleanup_processing_artifacts(output_base_dir: str) -> None:
    """
    Clean up all temporary processing artifacts.
    
    Args:
        output_base_dir: Base directory containing processing artifacts
    """
    import shutil
    
    directories_to_clean = [
        os.path.join(output_base_dir, "trimmed"),
        os.path.join(output_base_dir, "stems")
    ]
    
    for directory in directories_to_clean:
        if os.path.exists(directory):
            try:
                shutil.rmtree(directory)
                logger.info(f"Cleaned up directory: {directory}")
            except OSError as e:
                logger.warning(f"Failed to cleanup {directory}: {e}")
