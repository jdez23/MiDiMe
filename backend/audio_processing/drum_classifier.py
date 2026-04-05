"""
Drum classification module.

Classifies detected onsets into drum types (kick, snare, hihat) based on
frequency analysis at each onset point.

Optimised to accept pre-loaded audio arrays to avoid redundant disk I/O.
"""

import os
import logging
from typing import List, Dict

import numpy as np

logger = logging.getLogger(__name__)

_ANALYSIS_SR = 22050

DRUM_MIDI_NOTES = {
    "kick": 36,
    "snare": 38,
    "hihat": 42,
}


def classify_drum_hit(
    y: np.ndarray,
    sr: int,
    onset_sample: int,
    window_size: int = 2048,
) -> str:
    """
    Classify a single drum hit by frequency content.

    - Kick:  dominant energy 20-100 Hz
    - Snare: dominant energy 150-250 Hz
    - Hi-hat: dominant energy 5000-10000 Hz
    """
    start = max(0, onset_sample - window_size // 2)
    end = min(len(y), onset_sample + window_size // 2)
    window = y[start:end]

    fft = np.fft.rfft(window)
    freqs = np.fft.rfftfreq(len(window), 1 / sr)
    magnitudes = np.abs(fft)

    energies = {
        "kick":  np.sum(magnitudes[(freqs >= 20)  & (freqs < 100)]),
        "snare": np.sum(magnitudes[(freqs >= 150) & (freqs < 250)]),
        "hihat": np.sum(magnitudes[(freqs >= 5000) & (freqs < 10000)]),
    }

    return max(energies, key=energies.get)


def classify_drum_pattern(
    audio_path: str,
    onset_times: List[float],
    y: np.ndarray = None,
    sr: int = None,
) -> Dict[str, List[float]]:
    """
    Classify all detected onsets into drum types.

    Pass *y*/*sr* to skip loading from disk.
    """
    if y is None or sr is None:
        import librosa
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        y, sr = librosa.load(audio_path, sr=_ANALYSIS_SR, mono=True)

    drum_pattern: Dict[str, List[float]] = {"kick": [], "snare": [], "hihat": []}

    for onset_time in onset_times:
        onset_sample = int(onset_time * sr)
        drum_type = classify_drum_hit(y, sr, onset_sample)
        drum_pattern[drum_type].append(onset_time)

    logger.info(
        f"Classified: {len(drum_pattern['kick'])} kicks, "
        f"{len(drum_pattern['snare'])} snares, "
        f"{len(drum_pattern['hihat'])} hi-hats"
    )

    return drum_pattern
