"""
Drum classification module.

Classifies detected onsets into drum types (kick, snare, hihat) based on
frequency analysis at each onset point.

Uses wider frequency bands and energy-ratio heuristics to improve accuracy
over the previous narrow single-band approach.

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

# Minimum absolute magnitude threshold for hihat to avoid classifying bleed-through
_HIHAT_MIN_ENERGY_FRACTION = 0.08


def _band_energy(magnitudes: np.ndarray, freqs: np.ndarray, lo: float, hi: float) -> float:
    """Sum magnitude in a frequency band."""
    mask = (freqs >= lo) & (freqs < hi)
    return float(np.sum(magnitudes[mask]))


def classify_drum_hit(
    y: np.ndarray,
    sr: int,
    onset_sample: int,
    window_size: int = 2048,
) -> str:
    """
    Classify a single drum hit using energy ratios across frequency bands.

    Decision logic:
    - Hi-hat: high-frequency energy (5k–16k Hz) dominates AND exceeds a minimum
      fraction of total energy (filters bleed-through noise).
    - Kick: strong sub-bass energy (20–150 Hz) that is ≥1.5× the mid energy
      (150–800 Hz), indicating a true low-frequency transient.
    - Snare: has both a body component (150–300 Hz) AND a noise component
      (2k–8k Hz), or if neither kick nor hihat criteria are met.
    """
    start = max(0, onset_sample - window_size // 2)
    end = min(len(y), onset_sample + window_size // 2)
    window = y[start:end]
    if len(window) == 0:
        return "snare"

    fft = np.fft.rfft(window)
    freqs = np.fft.rfftfreq(len(window), 1 / sr)
    magnitudes = np.abs(fft)

    total_energy = float(np.sum(magnitudes)) or 1.0

    sub_bass   = _band_energy(magnitudes, freqs, 20,   150)   # kick body
    mid_low    = _band_energy(magnitudes, freqs, 150,  800)   # kick/snare body overlap
    snare_body = _band_energy(magnitudes, freqs, 150,  300)   # snare fundamental
    snare_snap = _band_energy(magnitudes, freqs, 2000, 8000)  # snare noise / crack
    hihat_e    = _band_energy(magnitudes, freqs, 5000, 16000) # hihat / cymbal

    hihat_frac = hihat_e / total_energy

    # Hi-hat: dominant high-frequency content above minimum fraction
    if hihat_frac >= _HIHAT_MIN_ENERGY_FRACTION and hihat_e >= mid_low and hihat_e >= sub_bass:
        return "hihat"

    # Kick: strong sub-bass relative to mids
    if sub_bass >= 1.5 * mid_low and sub_bass > snare_snap:
        return "kick"

    # Snare: has both body and snap (or is the fallback)
    # Even without strong snap, anything not classified as kick/hihat is snare
    return "snare"


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
