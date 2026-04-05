"""
Onset detection module using librosa.

Detects the timing of drum hits (onsets) in audio files.
Optimised to accept pre-loaded audio arrays so callers can avoid
redundant disk reads.
"""

import os
import logging
from typing import List, Tuple, Optional

import numpy as np

logger = logging.getLogger(__name__)

_ANALYSIS_SR = 22050


def detect_onsets(
    audio_path: str = None,
    y: np.ndarray = None,
    sr: int = None,
    hop_length: int = 512,
    backtrack: bool = False,
) -> List[float]:
    """
    Detect onset times in an audio file or pre-loaded array.

    Pass *y* and *sr* to skip loading from disk.
    """
    import librosa

    if y is None or sr is None:
        if audio_path is None:
            raise ValueError("Provide audio_path or (y, sr)")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"Audio file not found: {audio_path}")
        y, sr = librosa.load(audio_path, sr=_ANALYSIS_SR, mono=True)

    onset_frames = librosa.onset.onset_detect(
        y=y, sr=sr, hop_length=hop_length, backtrack=backtrack, units="frames"
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)
    return onset_times.tolist()


def detect_onsets_with_strength(
    audio_path: str = None,
    y: np.ndarray = None,
    sr: int = None,
    hop_length: int = 512,
) -> List[Tuple[float, float]]:
    """Detect onsets with their normalised strength (0-1)."""
    import librosa

    if y is None or sr is None:
        if audio_path is None:
            raise ValueError("Provide audio_path or (y, sr)")
        y, sr = librosa.load(audio_path, sr=_ANALYSIS_SR, mono=True)

    onset_env = librosa.onset.onset_strength(y=y, sr=sr, hop_length=hop_length)
    onset_frames = librosa.onset.onset_detect(
        onset_envelope=onset_env, sr=sr, hop_length=hop_length,
        backtrack=True, units="frames",
    )
    onset_times = librosa.frames_to_time(onset_frames, sr=sr, hop_length=hop_length)
    onset_strengths = onset_env[onset_frames]

    if len(onset_strengths) > 0:
        mx = onset_strengths.max()
        if mx > 0:
            onset_strengths = onset_strengths / mx

    return list(zip(onset_times.tolist(), onset_strengths.tolist()))


def filter_weak_onsets(
    onsets_with_strength: List[Tuple[float, float]],
    min_strength: float = 0.3,
) -> List[float]:
    """Filter out weak onsets below a strength threshold."""
    filtered = [t for t, s in onsets_with_strength if s >= min_strength]
    logger.info(f"Filtered onsets: {len(onsets_with_strength)} → {len(filtered)}")
    return filtered


def get_tempo(
    audio_path: str = None,
    y: np.ndarray = None,
    sr: int = None,
) -> float:
    """Estimate BPM. Pass *y*/*sr* to skip disk I/O."""
    import librosa

    if y is None or sr is None:
        if audio_path is None:
            raise ValueError("Provide audio_path or (y, sr)")
        y, sr = librosa.load(audio_path, sr=_ANALYSIS_SR, mono=True)

    tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
    return float(np.squeeze(tempo))


def analyze_drum_pattern(
    audio_path: str,
    y: np.ndarray = None,
    sr: int = None,
) -> dict:
    """
    Complete drum pattern analysis.

    Loads audio once and reuses for onset detection and tempo estimation.
    """
    import librosa

    if y is None or sr is None:
        y, sr = librosa.load(audio_path, sr=_ANALYSIS_SR, mono=True)

    duration = len(y) / sr
    onset_times = detect_onsets(y=y, sr=sr)
    tempo = get_tempo(y=y, sr=sr)
    hit_density = len(onset_times) / duration if duration > 0 else 0

    logger.info(
        f"Analysis: {len(onset_times)} hits, {tempo:.0f} BPM, "
        f"{hit_density:.1f} hits/sec"
    )

    return {
        "onset_times": onset_times,
        "num_hits": len(onset_times),
        "tempo_bpm": tempo,
        "duration_seconds": duration,
        "hit_density": hit_density,
    }
