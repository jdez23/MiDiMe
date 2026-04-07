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


def _backbeat_score(snare: List[int]) -> float:
    """Fraction of snare hits landing on beat 2 or 4 (classic backbeat)."""
    st = len(snare)
    if st < 4:
        return 0.0
    spb = st // 4
    sc = sum(1 for v in snare if v > 0)
    if sc == 0:
        return 0.0
    on_backbeat = sum(
        1 for beat in (1, 3)  # 0-indexed beats 1 and 3 = musical beats 2 and 4
        if beat * spb < st and snare[beat * spb] > 0
    )
    return on_backbeat / max(sc, 1)


def _kick_syncopation(kick: List[int]) -> float:
    """Fraction of kick hits that land off the downbeat."""
    st = len(kick)
    if st < 4:
        return 0.0
    spb = st // 4
    kc = sum(1 for v in kick if v > 0)
    if kc == 0:
        return 0.0
    on_downbeat = sum(
        1 for i, v in enumerate(kick)
        if v > 0 and i % spb == 0
    )
    return 1.0 - (on_downbeat / kc)


def _hihat_regularity(hihat: List[int]) -> float:
    """
    0 = perfectly regular (straight 8ths), 1 = highly irregular.
    Computed as normalised variance of the inter-hit intervals.
    """
    positions = [i for i, v in enumerate(hihat) if v > 0]
    if len(positions) < 2:
        return 0.0
    intervals = [positions[i + 1] - positions[i] for i in range(len(positions) - 1)]
    mean = sum(intervals) / len(intervals)
    variance = sum((x - mean) ** 2 for x in intervals) / len(intervals)
    # Normalise by mean^2 to get coefficient of variation squared
    return min(1.0, variance / (mean ** 2 + 1e-6))


def classify_style(
    kick: List[int], snare: List[int], hihat: List[int], bpm: float
) -> Dict[str, str]:
    """
    Classify drum pattern style using a weighted scoring system.

    Each style scores against extracted musical features. The highest-scoring
    style wins. This replaces the brittle if/elif decision tree.
    """
    st = len(kick)
    if st == 0:
        return {"name": "Custom", "desc": "Unique pattern"}

    spb = st // 4 if st >= 4 else 1
    kc = sum(1 for v in kick if v > 0)
    sc = sum(1 for v in snare if v > 0)
    hc = sum(1 for v in hihat if v > 0)
    density = (kc + sc + hc) / (st * 3) if st > 0 else 0

    four_on_floor = (
        sum(1 for i in range(4) if i * spb < st and kick[i * spb] > 0) == 4
    ) if st >= 4 * spb else False

    hihat_density = hc / st if st > 0 else 0
    backbeat = _backbeat_score(snare)
    syncopation = _kick_syncopation(kick)
    irregularity = _hihat_regularity(hihat)

    scores: Dict[str, float] = {}

    # Techno: four-on-floor, 118-145 BPM, dense hihats
    scores["Techno"] = (
        (2.0 if four_on_floor else 0)
        + (1.5 if 118 <= bpm <= 145 else 0)
        + (1.0 if hihat_density > 0.5 else 0)
    )

    # House: four-on-floor, 115-135 BPM, moderate hihats, some backbeat
    scores["House"] = (
        (2.0 if four_on_floor else 0)
        + (1.5 if 115 <= bpm <= 135 else 0)
        + (0.5 if 0.2 < hihat_density <= 0.6 else 0)
        + (0.5 if backbeat > 0 else 0)
    )

    # Trap: fast BPM, very dense irregular hihats
    scores["Trap"] = (
        (1.5 if 120 <= bpm <= 170 else 0)
        + (2.0 if hihat_density > 0.65 else 0)
        + (1.0 if irregularity > 0.3 else 0)
        + (0.5 if syncopation > 0.3 else 0)
    )

    # Boom Bap: mid tempo, sparse kicks, strong backbeat
    scores["Boom Bap"] = (
        (1.5 if 75 <= bpm <= 105 else 0)
        + (1.5 if kc <= 4 else 0)
        + (1.5 if backbeat > 0.4 else 0)
        + (0.5 if syncopation > 0.2 else 0)
    )

    # Funk: syncopated kick, backbeat snare, moderate tempo
    scores["Funk"] = (
        (2.0 if syncopation > 0.5 else 0)
        + (1.5 if backbeat > 0.4 else 0)
        + (1.0 if 85 <= bpm <= 120 else 0)
        + (0.5 if 0.2 < hihat_density < 0.7 else 0)
    )

    # Rock: strong backbeat, moderate-fast tempo, regular hihats
    scores["Rock"] = (
        (2.0 if backbeat > 0.6 else 0)
        + (1.0 if 100 <= bpm <= 160 else 0)
        + (1.0 if irregularity < 0.2 else 0)
        + (0.5 if four_on_floor else 0)
    )

    # Breakbeat: complex kick pattern, syncopated
    scores["Breakbeat"] = (
        (2.0 if kc >= st * 0.3 else 0)
        + (1.5 if syncopation > 0.4 else 0)
        + (1.0 if 90 <= bpm <= 145 else 0)
    )

    # Minimal: very sparse
    scores["Minimal"] = 3.0 if density < 0.2 else (1.5 if density < 0.3 else 0)

    # Dense: very busy
    scores["Dense"] = 3.0 if density > 0.65 else (1.5 if density > 0.5 else 0)

    # Custom: fallback — scores 0.5 always so it only wins if everything else is 0
    scores["Custom"] = 0.5

    best = max(scores, key=scores.get)

    descriptions = {
        "Techno":    "Driving four-on-floor with dense hi-hats",
        "House":     "Four-on-floor kick, offbeat hi-hats",
        "Trap":      "Fast tempo with rapid hi-hat rolls",
        "Boom Bap":  "Mid-tempo with sparse, syncopated kicks",
        "Funk":      "Syncopated groove with strong backbeat",
        "Rock":      "Steady backbeat with driving rhythm",
        "Breakbeat": "Syncopated, complex kick pattern",
        "Minimal":   "Sparse pattern with lots of space",
        "Dense":     "Busy, layered pattern",
        "Custom":    "Unique pattern",
    }

    return {"name": best, "desc": descriptions[best]}


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
