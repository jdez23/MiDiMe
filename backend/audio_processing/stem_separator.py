"""
Stem separation module using Spleeter.

This module provides functionality to separate audio files into individual stems
(drums, bass, vocals, other) using the Spleeter pre-trained model.
"""

import os
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def separate_stems(
    audio_path: str,
    output_dir: str,
    model: str = "spleeter:4stems",
    codec: str = "wav",
    bitrate: str = "128k"
) -> Dict[str, str]:
    """
    Separate an audio file into 4 stems using Spleeter.
    
    Args:
        audio_path: Path to the input audio file
        output_dir: Directory where separated stems will be saved
        model: Spleeter model to use (default: "spleeter:4stems")
        codec: Output audio codec (default: "wav")
        bitrate: Output bitrate for compressed formats (default: "128k")
    
    Returns:
        Dictionary mapping stem names to their file paths:
        {
            'drums': '/path/to/drums.wav',
            'bass': '/path/to/bass.wav',
            'vocals': '/path/to/vocals.wav',
            'other': '/path/to/other.wav'
        }
    
    Raises:
        FileNotFoundError: If audio_path doesn't exist
        RuntimeError: If Spleeter separation fails
        ImportError: If Spleeter is not installed
    """
    # Validate input file exists
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    try:
        from spleeter.separator import Separator
        logger.info(f"Separating stems for: {audio_path}")
        
        # Initialize Spleeter separator
        separator = Separator(model)
        
        # Perform separation
        # Spleeter expects the output directory and will create subdirectories
        separator.separate_to_file(
            audio_path,
            output_dir,
            codec=codec,
            bitrate=bitrate
        )
        
        # Determine output paths
        # Spleeter creates a subdirectory named after the input file (without extension)
        audio_filename = Path(audio_path).stem
        stem_dir = os.path.join(output_dir, audio_filename)
        
        # Map stem names to their file paths
        stem_paths = {
            'drums': os.path.join(stem_dir, f'drums.{codec}'),
            'bass': os.path.join(stem_dir, f'bass.{codec}'),
            'vocals': os.path.join(stem_dir, f'vocals.{codec}'),
            'other': os.path.join(stem_dir, f'other.{codec}')
        }
        
        # Verify all stems were created
        for stem_name, stem_path in stem_paths.items():
            if not os.path.exists(stem_path):
                logger.warning(f"Stem file not found: {stem_path}")
                raise RuntimeError(f"Failed to generate {stem_name} stem")
        
        logger.info(f"Successfully separated {len(stem_paths)} stems")
        return stem_paths
        
    except ImportError as e:
        logger.error("Spleeter is not installed. Install with: pip install spleeter")
        raise ImportError(
            "Spleeter is not installed. Run: pip install spleeter"
        ) from e
    
    except Exception as e:
        logger.error(f"Stem separation failed: {str(e)}")
        raise RuntimeError(f"Failed to separate stems: {str(e)}") from e


def get_drum_stem(audio_path: str, output_dir: str) -> str:
    """
    Extract only the drum stem from an audio file.
    
    Convenience function that runs full separation but only returns the drums path.
    
    Args:
        audio_path: Path to the input audio file
        output_dir: Directory where separated stems will be saved
    
    Returns:
        Path to the drum stem WAV file
    
    Raises:
        FileNotFoundError: If audio_path doesn't exist
        RuntimeError: If separation fails
    """
    stem_paths = separate_stems(audio_path, output_dir)
    return stem_paths['drums']


def cleanup_stems(stem_dir: str) -> None:
    """
    Delete separated stem files to free up disk space.
    
    Args:
        stem_dir: Directory containing separated stems
    
    Raises:
        OSError: If deletion fails
    """
    import shutil
    
    if os.path.exists(stem_dir):
        try:
            shutil.rmtree(stem_dir)
            logger.info(f"Cleaned up stems directory: {stem_dir}")
        except OSError as e:
            logger.error(f"Failed to cleanup stems: {str(e)}")
            raise
