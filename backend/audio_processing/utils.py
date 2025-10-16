"""
Audio processing utilities for MiDiMe.

This module provides utility functions for audio manipulation including
trimming, format conversion, and validation.
"""

import os
import logging
from typing import Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


def trim_audio(
    audio_path: str,
    output_path: str,
    start_time_seconds: float,
    end_time_seconds: float,
    format: str = "wav"
) -> str:
    """
    Trim an audio file to a specific time range.
    
    Args:
        audio_path: Path to the input audio file
        output_path: Path where trimmed audio will be saved
        start_time_seconds: Start time in seconds
        end_time_seconds: End time in seconds
        format: Output audio format (default: "wav")
    
    Returns:
        Path to the trimmed audio file
    
    Raises:
        FileNotFoundError: If audio_path doesn't exist
        ValueError: If time range is invalid
        RuntimeError: If trimming fails
        ImportError: If pydub is not installed
    """
    # Validate input file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Validate time range
    if start_time_seconds < 0:
        raise ValueError("Start time cannot be negative")
    
    if end_time_seconds <= start_time_seconds:
        raise ValueError("End time must be greater than start time")
    
    duration_seconds = end_time_seconds - start_time_seconds
    
    # Validate duration (15-90 seconds for MiDiMe)
    if duration_seconds < 15:
        raise ValueError(
            f"Duration too short: {duration_seconds:.1f}s. Minimum is 15 seconds."
        )
    
    if duration_seconds > 90:
        raise ValueError(
            f"Duration too long: {duration_seconds:.1f}s. Maximum is 90 seconds."
        )
    
    try:
        from pydub import AudioSegment
        
        logger.info(
            f"Trimming audio: {audio_path} "
            f"[{start_time_seconds:.2f}s - {end_time_seconds:.2f}s]"
        )
        
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Get audio duration
        audio_duration_ms = len(audio)
        audio_duration_seconds = audio_duration_ms / 1000.0
        
        # Validate end time doesn't exceed audio duration
        if end_time_seconds > audio_duration_seconds:
            raise ValueError(
                f"End time {end_time_seconds:.1f}s exceeds audio duration "
                f"{audio_duration_seconds:.1f}s"
            )
        
        # Convert seconds to milliseconds for pydub
        start_time_ms = int(start_time_seconds * 1000)
        end_time_ms = int(end_time_seconds * 1000)
        
        # Extract the segment
        trimmed_audio = audio[start_time_ms:end_time_ms]
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Export trimmed audio
        trimmed_audio.export(output_path, format=format)
        
        trimmed_duration = len(trimmed_audio) / 1000.0
        logger.info(
            f"Audio trimmed successfully: {output_path} "
            f"(duration: {trimmed_duration:.2f}s)"
        )
        
        return output_path
        
    except ImportError as e:
        logger.error("pydub is not installed. Install with: pip install pydub")
        raise ImportError(
            "pydub is not installed. Run: pip install pydub"
        ) from e
    
    except Exception as e:
        logger.error(f"Audio trimming failed: {str(e)}")
        raise RuntimeError(f"Failed to trim audio: {str(e)}") from e


def convert_to_wav(
    audio_path: str,
    output_path: Optional[str] = None,
    sample_rate: int = 44100,
    channels: int = 2
) -> str:
    """
    Convert an audio file to WAV format.
    
    Args:
        audio_path: Path to the input audio file
        output_path: Path for output WAV file (optional)
        sample_rate: Target sample rate in Hz (default: 44100)
        channels: Number of audio channels (default: 2 for stereo)
    
    Returns:
        Path to the converted WAV file
    
    Raises:
        FileNotFoundError: If audio_path doesn't exist
        RuntimeError: If conversion fails
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Generate output path if not provided
    if output_path is None:
        path_obj = Path(audio_path)
        output_path = str(path_obj.with_suffix('.wav'))
    
    try:
        from pydub import AudioSegment
        
        logger.info(f"Converting to WAV: {audio_path}")
        
        # Load audio file (pydub handles various formats)
        audio = AudioSegment.from_file(audio_path)
        
        # Set sample rate and channels
        audio = audio.set_frame_rate(sample_rate)
        audio = audio.set_channels(channels)
        
        # Export as WAV
        audio.export(output_path, format="wav")
        
        logger.info(f"Converted to WAV: {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"WAV conversion failed: {str(e)}")
        raise RuntimeError(f"Failed to convert to WAV: {str(e)}") from e


def get_audio_info(audio_path: str) -> dict:
    """
    Get information about an audio file.
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        Dictionary containing audio information:
        {
            'duration_seconds': float,
            'sample_rate': int,
            'channels': int,
            'format': str,
            'file_size_mb': float
        }
    
    Raises:
        FileNotFoundError: If audio_path doesn't exist
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        from pydub import AudioSegment
        
        # Load audio file
        audio = AudioSegment.from_file(audio_path)
        
        # Get file size
        file_size_bytes = os.path.getsize(audio_path)
        file_size_mb = file_size_bytes / (1024 * 1024)
        
        # Get file format from extension
        file_format = Path(audio_path).suffix.lstrip('.')
        
        return {
            'duration_seconds': len(audio) / 1000.0,
            'sample_rate': audio.frame_rate,
            'channels': audio.channels,
            'format': file_format,
            'file_size_mb': round(file_size_mb, 2)
        }
        
    except Exception as e:
        logger.error(f"Failed to get audio info: {str(e)}")
        raise RuntimeError(f"Failed to get audio info: {str(e)}") from e


def validate_audio_file(
    audio_path: str,
    max_size_mb: int = 50,
    allowed_formats: Optional[list] = None
) -> Tuple[bool, str]:
    """
    Validate an audio file for processing.
    
    Args:
        audio_path: Path to the audio file
        max_size_mb: Maximum file size in MB (default: 50)
        allowed_formats: List of allowed formats (default: common audio formats)
    
    Returns:
        Tuple of (is_valid, error_message)
        If valid: (True, "")
        If invalid: (False, "Error description")
    """
    if allowed_formats is None:
        allowed_formats = ['mp3', 'wav', 'flac', 'm4a', 'ogg']
    
    # Check if file exists
    if not os.path.exists(audio_path):
        return False, f"File not found: {audio_path}"
    
    # Check file extension
    file_ext = Path(audio_path).suffix.lstrip('.').lower()
    if file_ext not in allowed_formats:
        return False, (
            f"Unsupported format: .{file_ext}. "
            f"Allowed formats: {', '.join(allowed_formats)}"
        )
    
    # Check file size
    file_size_bytes = os.path.getsize(audio_path)
    file_size_mb = file_size_bytes / (1024 * 1024)
    
    if file_size_mb > max_size_mb:
        return False, (
            f"File too large: {file_size_mb:.2f} MB. "
            f"Maximum size: {max_size_mb} MB"
        )
    
    # Try to load the audio file to verify it's valid
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_path)
        
        # Check if audio has content
        if len(audio) == 0:
            return False, "Audio file is empty"
        
        return True, ""
        
    except Exception as e:
        return False, f"Invalid audio file: {str(e)}"
