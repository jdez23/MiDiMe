"""
Audio processing package for MiDiMe.

Modules:
- stem_separator: Demucs-based stem separation
- onset_detector: librosa onset detection
- drum_classifier: frequency-based kick/snare/hihat classification
- midi_converter: MIDI file and JSON generation
- band_analyzer: frequency-band fallback (no Demucs required)
- quantizer: onset-to-grid conversion for frontend
- audio_service: high-level orchestration
- utils: trim, convert, validate
"""

from .stem_separator import separate_stems, get_drum_stem, cleanup_stems
from .utils import (
    trim_audio,
    convert_to_wav,
    get_audio_info,
    validate_audio_file,
)
from .audio_service import (
    process_audio_snippet,
    get_drum_pattern,
    cleanup_processing_artifacts,
    AudioProcessingResult,
)
from .quantizer import build_pattern_response
from .band_analyzer import analyze_by_frequency_bands, get_tempo_from_audio

__all__ = [
    # Stem separation
    "separate_stems",
    "get_drum_stem",
    "cleanup_stems",
    # Audio utilities
    "trim_audio",
    "convert_to_wav",
    "get_audio_info",
    "validate_audio_file",
    # Integrated service
    "process_audio_snippet",
    "get_drum_pattern",
    "cleanup_processing_artifacts",
    "AudioProcessingResult",
    # Quantizer
    "build_pattern_response",
    # Band analyzer fallback
    "analyze_by_frequency_bands",
    "get_tempo_from_audio",
]
