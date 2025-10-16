"""
Drum classification module.

Classifies detected onsets into drum types (kick, snare, hihat) based on
frequency analysis at each onset point.
"""

import os
import logging
from typing import List, Dict, Tuple
import numpy as np

logger = logging.getLogger(__name__)


# MIDI note numbers for standard drum mapping (General MIDI)
DRUM_MIDI_NOTES = {
    'kick': 36,    # Bass Drum 1 (C1)
    'snare': 38,   # Acoustic Snare (D1)
    'hihat': 42    # Closed Hi-Hat (F#1)
}


def classify_drum_hit(
    y: np.ndarray,
    sr: int,
    onset_sample: int,
    window_size: int = 2048
) -> str:
    """
    Classify a single drum hit based on frequency content.
    
    Uses frequency analysis to determine if a hit is kick, snare, or hihat:
    - Kick: Strong low frequencies (20-100 Hz)
    - Snare: Mid frequencies (150-250 Hz) + high frequencies
    - Hi-hat: Primarily high frequencies (5000+ Hz)
    
    Args:
        y: Audio samples
        sr: Sample rate
        onset_sample: Sample index of the onset
        window_size: Size of analysis window around onset
    
    Returns:
        Drum type: 'kick', 'snare', or 'hihat'
    """
    try:
        import librosa
        
        # Extract a window around the onset
        start_sample = max(0, onset_sample - window_size // 2)
        end_sample = min(len(y), onset_sample + window_size // 2)
        window = y[start_sample:end_sample]
        
        # Compute FFT (frequency spectrum)
        fft = np.fft.rfft(window)
        freqs = np.fft.rfftfreq(len(window), 1/sr)
        magnitudes = np.abs(fft)
        
        # Define frequency bands
        kick_band = (20, 100)       # Sub-bass to bass
        snare_band = (150, 250)     # Mid frequencies
        hihat_band = (5000, 10000)  # High frequencies
        
        # Calculate energy in each band
        kick_energy = np.sum(magnitudes[(freqs >= kick_band[0]) & (freqs < kick_band[1])])
        snare_energy = np.sum(magnitudes[(freqs >= snare_band[0]) & (freqs < snare_band[1])])
        hihat_energy = np.sum(magnitudes[(freqs >= hihat_band[0]) & (freqs < hihat_band[1])])
        
        # Classify based on dominant energy
        energies = {
            'kick': kick_energy,
            'snare': snare_energy,
            'hihat': hihat_energy
        }
        
        drum_type = max(energies, key=energies.get)
        
        return drum_type
        
    except Exception as e:
        logger.warning(f"Classification failed for onset at sample {onset_sample}: {e}")
        # Default to snare if classification fails
        return 'snare'


def classify_drum_pattern(
    audio_path: str,
    onset_times: List[float]
) -> Dict[str, List[float]]:
    """
    Classify all detected onsets into drum types.
    
    Args:
        audio_path: Path to drum audio file
        onset_times: List of onset times in seconds
    
    Returns:
        Dictionary mapping drum types to their onset times:
        {
            'kick': [0.0, 2.0, 4.0, ...],
            'snare': [1.0, 3.0, 5.0, ...],
            'hihat': [0.5, 1.5, 2.5, ...]
        }
    
    Example:
        >>> onsets = detect_onsets("drums.wav")
        >>> pattern = classify_drum_pattern("drums.wav", onsets)
        >>> print(f"Kicks: {len(pattern['kick'])}")
        >>> print(f"Snares: {len(pattern['snare'])}")
        >>> print(f"Hi-hats: {len(pattern['hihat'])}")
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    
    try:
        import librosa
        
        logger.info(f"Classifying {len(onset_times)} onsets...")
        
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Initialize drum pattern dictionary
        drum_pattern = {
            'kick': [],
            'snare': [],
            'hihat': []
        }
        
        # Classify each onset
        for onset_time in onset_times:
            # Convert time to sample index
            onset_sample = int(onset_time * sr)
            
            # Classify the hit
            drum_type = classify_drum_hit(y, sr, onset_sample)
            
            # Add to appropriate list
            drum_pattern[drum_type].append(onset_time)
        
        # Log results
        logger.info(
            f"Classification complete: "
            f"{len(drum_pattern['kick'])} kicks, "
            f"{len(drum_pattern['snare'])} snares, "
            f"{len(drum_pattern['hihat'])} hi-hats"
        )
        
        return drum_pattern
        
    except Exception as e:
        logger.error(f"Drum classification failed: {str(e)}")
        raise RuntimeError(f"Failed to classify drums: {str(e)}") from e


def get_drum_midi_pattern(
    audio_path: str,
    onset_times: List[float]
) -> List[Tuple[float, int]]:
    """
    Get classified drum pattern in MIDI format.
    
    Returns onset times with their corresponding MIDI note numbers.
    
    Args:
        audio_path: Path to drum audio file
        onset_times: List of onset times in seconds
    
    Returns:
        List of (time, midi_note) tuples, sorted by time
        MIDI notes: kick=36, snare=38, hihat=42
    
    Example:
        >>> onsets = detect_onsets("drums.wav")
        >>> midi_pattern = get_drum_midi_pattern("drums.wav", onsets)
        >>> for time, note in midi_pattern:
        ...     print(f"{time:.3f}s - MIDI note {note}")
    """
    # Get classified pattern
    drum_pattern = classify_drum_pattern(audio_path, onset_times)
    
    # Convert to MIDI format
    midi_pattern = []
    
    for drum_type, times in drum_pattern.items():
        midi_note = DRUM_MIDI_NOTES[drum_type]
        for time in times:
            midi_pattern.append((time, midi_note))
    
    # Sort by time
    midi_pattern.sort(key=lambda x: x[0])
    
    logger.info(f"Generated MIDI pattern with {len(midi_pattern)} notes")
    
    return midi_pattern


def get_drum_pattern_summary(drum_pattern: Dict[str, List[float]]) -> dict:
    """
    Get a summary of the drum pattern.
    
    Args:
        drum_pattern: Dictionary of drum types to onset times
    
    Returns:
        Summary dictionary with counts and timing info
    """
    total_hits = sum(len(times) for times in drum_pattern.values())
    
    summary = {
        'total_hits': total_hits,
        'kick_count': len(drum_pattern.get('kick', [])),
        'snare_count': len(drum_pattern.get('snare', [])),
        'hihat_count': len(drum_pattern.get('hihat', [])),
        'kick_percentage': len(drum_pattern.get('kick', [])) / total_hits * 100 if total_hits > 0 else 0,
        'snare_percentage': len(drum_pattern.get('snare', [])) / total_hits * 100 if total_hits > 0 else 0,
        'hihat_percentage': len(drum_pattern.get('hihat', [])) / total_hits * 100 if total_hits > 0 else 0,
    }
    
    return summary
