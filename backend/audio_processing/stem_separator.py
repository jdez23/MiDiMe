"""
Stem separation module using Demucs v4.

Separates audio files into individual stems (drums, bass, vocals, other)
using Meta's Demucs pre-trained model (htdemucs).

The model is loaded once and reused across requests (singleton pattern).
"""

import os
import logging
import shutil
import threading
from typing import Dict
from pathlib import Path

logger = logging.getLogger(__name__)

_model = None
_model_lock = threading.Lock()


def _get_model(model_name: str = "htdemucs", device: str = "cpu"):
    """Load and cache the Demucs model (thread-safe singleton)."""
    global _model
    if _model is not None:
        return _model

    with _model_lock:
        if _model is not None:
            return _model

        import torch
        from demucs.pretrained import get_model

        logger.info(f"Loading Demucs model '{model_name}' (one-time)…")
        model = get_model(model_name)
        model.to(device)
        model.eval()
        _model = model
        logger.info("Demucs model loaded and cached.")
        return _model


def separate_stems(
    audio_path: str,
    output_dir: str,
    model_name: str = "htdemucs",
    device: str = "cpu",
) -> Dict[str, str]:
    """
    Separate an audio file into 4 stems using Demucs.

    The model is loaded once and reused across all subsequent calls.

    Returns:
        Dictionary mapping stem names to file paths.

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
        import torchaudio
        from demucs.apply import apply_model
        from demucs.audio import save_audio

        model = _get_model(model_name, device)

        logger.info(f"Separating stems: {audio_path}")

        wav, sr = torchaudio.load(str(audio_path))
        if wav.dim() == 1:
            wav = wav.unsqueeze(0)

        ref = wav.mean(0)
        wav = (wav - ref.mean()) / ref.std()
        wav = wav.unsqueeze(0).to(device)

        with torch.no_grad():
            sources = apply_model(model, wav, device=device)

        sources = sources * ref.std() + ref.mean()
        sources = sources.squeeze(0)

        audio_stem = Path(audio_path).stem
        stem_dir = os.path.join(output_dir, audio_stem)
        os.makedirs(stem_dir, exist_ok=True)

        stem_paths: Dict[str, str] = {}
        for i, stem_name in enumerate(model.sources):
            out_path = os.path.join(stem_dir, f"{stem_name}.wav")
            save_audio(sources[i], out_path, samplerate=model.samplerate)
            stem_paths[stem_name] = out_path

        logger.info(f"Separated {len(stem_paths)} stems")
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
            logger.info(f"Cleaned up stems: {stem_dir}")
        except OSError as exc:
            logger.error(f"Failed to cleanup stems: {exc}")
            raise
