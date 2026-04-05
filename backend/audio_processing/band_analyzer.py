"""
Frequency-band drum analysis fallback for MiDiMe.

When Demucs is unavailable, this module approximates drum classification
by bandpass-filtering the audio into kick / snare / hi-hat frequency
ranges and running onset detection on each band independently.

Audio is loaded once and reused across all three bands.
"""

import logging
from typing import Dict, List, Tuple

import numpy as np

logger = logging.getLogger(__name__)

BANDS: Dict[str, Tuple[int, int]] = {
    "kick":  (40,   150),
    "snare": (150,  1500),
    "hihat": (5000, 16000),
}

_ANALYSIS_SR = 22050


def _bandpass(y: np.ndarray, sr: int, lo: int, hi: int) -> np.ndarray:
    """Apply a Butterworth bandpass filter."""
    from scipy.signal import butter, sosfilt

    nyq = sr / 2.0
    lo_norm = max(lo / nyq, 0.001)
    hi_norm = min(hi / nyq, 0.999)
    sos = butter(4, [lo_norm, hi_norm], btype="band", output="sos")
    return sosfilt(sos, y)


def _detect_onsets(y: np.ndarray, sr: int) -> List[float]:
    """Run librosa onset detection and return times in seconds."""
    import librosa

    onset_frames = librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=512, backtrack=False, units="frames"
    )
    return librosa.frames_to_time(onset_frames, sr=sr, hop_length=512).tolist()


def analyze_by_frequency_bands(
    audio_path: str,
) -> Dict[str, List[float]]:
    """
    Classify drum onsets using frequency-band filtering.

    Audio is loaded once at a fixed sample rate for efficiency.

    Returns ``{"kick": [t, ...], "snare": [t, ...], "hihat": [t, ...]}``
    """
    import librosa

    logger.info(f"Band-analyzer fallback for: {audio_path}")
    y, sr = librosa.load(audio_path, sr=_ANALYSIS_SR, mono=True)

    result: Dict[str, List[float]] = {}
    for name, (lo, hi) in BANDS.items():
        filtered = _bandpass(y, sr, lo, hi)
        result[name] = _detect_onsets(filtered, sr)
        logger.info(f"  {name}: {len(result[name])} onsets")

    return result


def get_tempo_from_audio(audio_path: str, y: np.ndarray = None, sr: int = None) -> float:
    """
    Estimate BPM using librosa beat tracker.

    If *y* and *sr* are provided, skips loading from disk.
    """
    import librosa

    if y is None or sr is None:
        y, sr = librosa.load(audio_path, sr=_ANALYSIS_SR, mono=True)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    bpm = float(np.squeeze(tempo))
    while bpm < 70:
        bpm *= 2
    while bpm > 180:
        bpm /= 2
    return round(bpm, 1)
