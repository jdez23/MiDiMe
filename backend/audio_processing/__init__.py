"""
Audio processing package for MiDiMe.

This package contains modules for:
- Stem separation (Spleeter)
- Onset detection (librosa)
- MIDI conversion
- Drum classification
- Audio utilities
- Integrated audio service
"""

from .stem_separator import separate_stems, get_drum_stem, cleanup_stems
from .utils import (
    trim_audio,
    convert_to_wav,
    get_audio_info,
    validate_audio_file
)
from .audio_service import (
    process_audio_snippet,
    get_drum_pattern,
    cleanup_processing_artifacts,
    AudioProcessingResult
)

__all__ = [
    # Stem separation
    'separate_stems',
    'get_drum_stem',
    'cleanup_stems',
    # Audio utilities
    'trim_audio',
    'convert_to_wav',
    'get_audio_info',
    'validate_audio_file',
    # Integrated service (recommended for production use)
    'process_audio_snippet',
    'get_drum_pattern',
    'cleanup_processing_artifacts',
    'AudioProcessingResult'
]
