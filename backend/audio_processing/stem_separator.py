"""
Stem separation module using Demucs v4.

Separates audio files into individual stems (drums, bass, vocals, other)
using Meta's Demucs pre-trained model (htdemucs).
"""

import os
import logging
import shutil
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)


def separate_stems(
    audio_path: str,
    output_dir: str,
    model_name: str = "htdemucs",
    device: str = "cpu",
) -> Dict[str, str]:
    """
    Separate an audio file into 4 stems using Demucs.

    Args:
        audio_path: Path to the input audio file.
        output_dir: Directory where separated stems will be saved.
        model_name: Demucs model to use (default: "htdemucs").
        device: Torch device string, e.g. "cpu" or "cuda".

    Returns:
        Dictionary mapping stem names to file paths::

            {"drums": "/.../drums.wav", "bass": "...", "vocals": "...", "other": "..."}

    Raises:
        FileNotFoundError: If *audio_path* doesn't exist.
        ImportError: If Demucs / torch is not installed.
        RuntimeError: If separation fails.
    """
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    os.makedirs(output_dir, exist_ok=True)

    try:
        import torch
        from demucs.api import Separator

        logger.info(f"Separating stems with Demucs ({model_name}): {audio_path}")

        separator = Separator(model=model_name, device=device)
        _, separated = separator.separate_audio_file(Path(audio_path))

        audio_stem = Path(audio_path).stem
        stem_dir = os.path.join(output_dir, audio_stem)
        os.makedirs(stem_dir, exist_ok=True)

        import torchaudio

        stem_paths: Dict[str, str] = {}
        for stem_name, waveform in separated.items():
            out_path = os.path.join(stem_dir, f"{stem_name}.wav")
            torchaudio.save(out_path, waveform.cpu(), separator.samplerate)
            stem_paths[stem_name] = out_path

        logger.info(f"Successfully separated {len(stem_paths)} stems")
        return stem_paths

    except ImportError as exc:
        logger.error("Demucs is not installed. Install with: pip install demucs")
        raise ImportError(
            "Demucs is not installed. Run: pip install demucs"
        ) from exc

    except Exception as exc:
        logger.error(f"Stem separation failed: {exc}")
        raise RuntimeError(f"Failed to separate stems: {exc}") from exc


def get_drum_stem(audio_path: str, output_dir: str) -> str:
    """Extract only the drum stem from an audio file."""
    stem_paths = separate_stems(audio_path, output_dir)
    return stem_paths["drums"]


def cleanup_stems(stem_dir: str) -> None:
    """Delete separated stem files to free disk space."""
    if os.path.exists(stem_dir):
        try:
            shutil.rmtree(stem_dir)
            logger.info(f"Cleaned up stems directory: {stem_dir}")
        except OSError as exc:
            logger.error(f"Failed to cleanup stems: {exc}")
            raise
