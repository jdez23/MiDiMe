"""
Onset detection module using librosa.

This module detects the timing of drum hits (onsets) in audio files.
An onset is a point in time where a musical note or drum hit begins.
"""

import os
import logging
from typing import List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


def detect_onsets(
    audio_path: str,
    hop_length: int = 512,
    backtrack: bool = False,
    onset_threshold: float = 0.3
) -> List[float]:
    """
    Detect onset times (drum hits) in an audio file.

    Uses librosa's onset detection with optimized parameters for drums.

    Args:
        audio_path: Path to the audio file (preferably drum stem)
        hop_length: Number of samples between frames (lower = more precision, slower)
        backtrack: Whether to backtrack detected onsets to previous local minimum
                   (default: False for better kick detection)
        onset_threshold: Threshold for onset detection (0.0-1.0, lower = more sensitive)
    
    Returns:
        List of onset times in seconds, sorted chronologically
    
    Raises:
        FileNotFoundError: If audio_path doesn't exist
        RuntimeError: If onset detection fails
        ImportError: If librosa is not installed
    
    Example:
        >>> onsets = detect_onsets("drums.wav")
        >>> print(f"Found {len(onsets)} drum hits")
        >>> print(f"First hit at: {onsets[0]:.3f} seconds")
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        import librosa
        
        logger.info(f"Detecting onsets in: {audio_path}")
        
        # Load audio file
        # sr=None preserves original sample rate
        y, sr = librosa.load(audio_path, sr=None)
        
        logger.info(f"Loaded audio: {len(y)} samples at {sr} Hz ({len(y)/sr:.2f}s)")
        
        # Detect onset frames
        onset_frames = librosa.onset.onset_detect(
            y=y,
            sr=sr,
            hop_length=hop_length,
            backtrack=backtrack,
            units='frames'
        )
        
        # Convert frames to time (seconds)
        onset_times = librosa.frames_to_time(
            onset_frames,
            sr=sr,
            hop_length=hop_length
        )
        
        # Convert to regular Python list
        onset_times_list = onset_times.tolist()
        
        logger.info(f"Detected {len(onset_times_list)} onsets")
        
        return onset_times_list
        
    except ImportError as e:
        logger.error("librosa is not installed. Install with: pip install librosa")
        raise ImportError(
            "librosa is not installed. Run: pip install librosa"
        ) from e
    
    except Exception as e:
        logger.error(f"Onset detection failed: {str(e)}")
        raise RuntimeError(f"Failed to detect onsets: {str(e)}") from e


def detect_onsets_with_strength(
    audio_path: str,
    hop_length: int = 512
) -> List[Tuple[float, float]]:
    """
    Detect onsets with their strength (loudness).
    
    Returns both the time and the strength/energy of each onset.
    Useful for filtering weak hits or velocity information.
    
    Args:
        audio_path: Path to the audio file
        hop_length: Number of samples between frames
    
    Returns:
        List of tuples: [(time1, strength1), (time2, strength2), ...]
        Times are in seconds, strengths are normalized 0.0-1.0
    
    Example:
        >>> onsets = detect_onsets_with_strength("drums.wav")
        >>> for time, strength in onsets:
        ...     print(f"{time:.3f}s - strength: {strength:.2f}")
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        import librosa
        
        logger.info(f"Detecting onsets with strength: {audio_path}")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Get onset strength envelope
        onset_env = librosa.onset.onset_strength(
            y=y,
            sr=sr,
            hop_length=hop_length
        )

        # Detect onset frames
        # Using default librosa parameters which work well for drums
        onset_frames = librosa.onset.onset_detect(
            onset_envelope=onset_env,
            sr=sr,
            hop_length=hop_length,
            backtrack=True,
            units='frames'
        )
        
        # Convert frames to times
        onset_times = librosa.frames_to_time(
            onset_frames,
            sr=sr,
            hop_length=hop_length
        )
        
        # Get strength at each onset
        onset_strengths = onset_env[onset_frames]
        
        # Normalize strengths to 0-1 range
        if len(onset_strengths) > 0:
            max_strength = onset_strengths.max()
            if max_strength > 0:
                onset_strengths = onset_strengths / max_strength
        
        # Combine times and strengths
        onsets_with_strength = list(zip(
            onset_times.tolist(),
            onset_strengths.tolist()
        ))
        
        logger.info(f"Detected {len(onsets_with_strength)} onsets with strength")
        
        return onsets_with_strength
        
    except Exception as e:
        logger.error(f"Onset detection with strength failed: {str(e)}")
        raise RuntimeError(f"Failed to detect onsets: {str(e)}") from e


def filter_weak_onsets(
    onsets_with_strength: List[Tuple[float, float]],
    min_strength: float = 0.3
) -> List[float]:
    """
    Filter out weak onsets based on strength threshold.
    
    Useful for removing false positives or very quiet hits.
    
    Args:
        onsets_with_strength: List of (time, strength) tuples
        min_strength: Minimum strength threshold (0.0-1.0)
    
    Returns:
        List of onset times that meet the strength threshold
    
    Example:
        >>> onsets = detect_onsets_with_strength("drums.wav")
        >>> strong_onsets = filter_weak_onsets(onsets, min_strength=0.5)
        >>> print(f"Filtered {len(onsets)} → {len(strong_onsets)} onsets")
    """
    filtered = [time for time, strength in onsets_with_strength if strength >= min_strength]
    
    logger.info(
        f"Filtered onsets: {len(onsets_with_strength)} → {len(filtered)} "
        f"(threshold: {min_strength})"
    )
    
    return filtered


def get_tempo(audio_path: str) -> float:
    """
    Estimate the tempo (BPM) of an audio file.
    
    Args:
        audio_path: Path to the audio file
    
    Returns:
        Estimated tempo in beats per minute (BPM)
    
    Example:
        >>> tempo = get_tempo("drums.wav")
        >>> print(f"Tempo: {tempo:.1f} BPM")
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        import librosa
        
        logger.info(f"Estimating tempo: {audio_path}")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Estimate tempo
        tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
        
        # Convert numpy type to Python float
        tempo = float(tempo)
        
        logger.info(f"Estimated tempo: {tempo:.1f} BPM")
        
        return tempo
        
    except Exception as e:
        logger.error(f"Tempo estimation failed: {str(e)}")
        raise RuntimeError(f"Failed to estimate tempo: {str(e)}") from e


def analyze_drum_pattern(
    audio_path: str,
    filter_weak: bool = False,
    min_strength: float = 0.1
) -> dict:
    """
    Complete drum pattern analysis.

    Detects onsets, estimates tempo, and returns comprehensive data.

    Args:
        audio_path: Path to drum audio file
        filter_weak: Whether to filter weak onsets (default: False to capture all hits)
        min_strength: Minimum strength threshold if filtering (lowered to 0.1 from 0.3)
    
    Returns:
        Dictionary containing:
        {
            'onset_times': List[float],
            'num_hits': int,
            'tempo_bpm': float,
            'duration_seconds': float,
            'hit_density': float  # hits per second
        }
    
    Example:
        >>> pattern = analyze_drum_pattern("drums.wav")
        >>> print(f"Found {pattern['num_hits']} hits at {pattern['tempo_bpm']:.0f} BPM")
    """
    try:
        import librosa
        
        logger.info(f"Analyzing drum pattern: {audio_path}")
        
        # Get audio duration
        y, sr = librosa.load(audio_path, sr=None)
        duration = len(y) / sr

        # Use simple onset detection for better results
        # The detect_onsets() function works better than detect_onsets_with_strength()
        # for capturing all drum hits including kicks
        onset_times = detect_onsets(audio_path)
        
        # Estimate tempo
        tempo = get_tempo(audio_path)
        
        # Calculate hit density
        hit_density = len(onset_times) / duration if duration > 0 else 0
        
        result = {
            'onset_times': onset_times,
            'num_hits': len(onset_times),
            'tempo_bpm': tempo,
            'duration_seconds': duration,
            'hit_density': hit_density
        }
        
        logger.info(
            f"Analysis complete: {result['num_hits']} hits, "
            f"{result['tempo_bpm']:.0f} BPM, "
            f"{result['hit_density']:.1f} hits/sec"
        )
        
        return result
        
    except Exception as e:
        logger.error(f"Drum pattern analysis failed: {str(e)}")
        raise RuntimeError(f"Failed to analyze drum pattern: {str(e)}") from e
