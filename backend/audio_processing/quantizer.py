"""
Quantization module for MiDiMe.

Converts raw onset times (in seconds) into grid-aligned binary arrays
with velocity, style classification, and swing estimation. The output
matches the JSON shape expected by the DrumDissect React component.
"""

import random
from typing import Dict, List


def quantize_to_grid(
    onset_times: List[float],
    step_duration: float,
    num_steps: int,
    duration: float,
) -> List[int]:
    """Snap onset times to the nearest grid position (binary array)."""
    grid = [0] * num_steps
    for t in onset_times:
        if t > duration:
            break
        idx = round(t / step_duration) % num_steps
        grid[idx] = 1
    return grid


def estimate_swing(onset_times: List[float], step_duration: float) -> int:
    """Estimate swing percentage from off-beat timing deviations."""
    if len(onset_times) < 4:
        return 0
    deviations: List[float] = []
    for t in onset_times:
        step_float = t / step_duration
        nearest = round(step_float)
        if nearest % 2 == 1:
            deviations.append(step_float - nearest)
    if not deviations:
        return 0
    avg = sum(abs(d) for d in deviations) / len(deviations)
    return round(avg * 100)


def classify_style(
    kick: List[int], snare: List[int], hihat: List[int], bpm: float
) -> Dict[str, str]:
    """Classify drum pattern style based on hit positions and tempo."""
    kc = sum(1 for v in kick if v > 0)
    hc = sum(1 for v in hihat if v > 0)
    st = len(kick)
    spb = st // 4 if st >= 4 else 1

    four_on_floor = (
        all(kick[i * spb] > 0 for i in range(4)) if st >= 4 * spb else False
    )

    if four_on_floor and 118 <= bpm <= 135:
        if hc > st * 0.6:
            return {"name": "Techno", "desc": "Driving four-on-floor with dense hi-hats"}
        return {"name": "House", "desc": "Four-on-floor kick, offbeat hi-hats"}

    if 130 <= bpm <= 160 and hc > st * 0.7:
        return {"name": "Trap", "desc": "Fast tempo with rapid hi-hat rolls"}

    if 80 <= bpm <= 100 and kc <= 4:
        return {"name": "Boom Bap", "desc": "Mid-tempo with sparse, syncopated kicks"}

    if kc >= st * 0.3:
        return {"name": "Breakbeat", "desc": "Syncopated, complex pattern"}

    sc = sum(1 for v in snare if v > 0)
    density = (kc + sc + hc) / (st * 3) if st > 0 else 0

    if density < 0.25:
        return {"name": "Minimal", "desc": "Sparse pattern with lots of space"}
    if density > 0.6:
        return {"name": "Dense", "desc": "Busy layered pattern"}

    return {"name": "Custom", "desc": "Unique pattern"}


def _random_velocity(active: int, lo: float = 0.7, hi: float = 1.0) -> float:
    """Generate a humanised velocity for an active hit."""
    return active * (lo + random.random() * (hi - lo)) if active else 0.0


def build_pattern_response(
    drum_onsets: Dict[str, List[float]],
    tempo: float,
    grid_size: int = 16,
    bar_count: int = 2,
) -> dict:
    """
    Orchestrate quantization and produce the full pattern dict
    matching the frontend DrumDissect component.

    Args:
        drum_onsets: ``{"kick": [t, ...], "snare": [t, ...], "hihat": [t, ...]}``
            where each value is a list of onset times in seconds.
        tempo: Detected BPM.
        grid_size: Steps per bar (8, 16, or 32).
        bar_count: Number of bars (1, 2, or 4).

    Returns:
        Dict with keys: kick, snare, hihat, kickVel, snareVel, hihatVel,
        bpm, swing, steps, style, desc.
    """
    num_steps = grid_size * bar_count
    step_duration = 60.0 / tempo / (grid_size / 4)
    duration = step_duration * num_steps

    kick_times = drum_onsets.get("kick", [])
    snare_times = drum_onsets.get("snare", [])
    hihat_times = drum_onsets.get("hihat", [])

    kick = quantize_to_grid(kick_times, step_duration, num_steps, duration)
    snare = quantize_to_grid(snare_times, step_duration, num_steps, duration)
    hihat = quantize_to_grid(hihat_times, step_duration, num_steps, duration)

    all_times = sorted(kick_times + snare_times + hihat_times)
    swing = estimate_swing(all_times, step_duration)
    style = classify_style(kick, snare, hihat, tempo)

    return {
        "kick": kick,
        "snare": snare,
        "hihat": hihat,
        "kickVel": [_random_velocity(v, 0.7, 1.0) for v in kick],
        "snareVel": [_random_velocity(v, 0.7, 1.0) for v in snare],
        "hihatVel": [_random_velocity(v, 0.5, 1.0) for v in hihat],
        "bpm": tempo,
        "swing": swing,
        "steps": num_steps,
        "style": style,
        "desc": style["desc"],
    }
