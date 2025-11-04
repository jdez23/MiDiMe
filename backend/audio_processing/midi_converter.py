"""
MIDI Converter - Convert drum patterns to MIDI files.

Converts classified drum patterns (onset times) into standard MIDI format
that can be imported into any DAW (Logic, FL Studio, Ableton, etc.).
"""
import logging
from typing import Dict, List, Optional
from midiutil import MIDIFile

logger = logging.getLogger(__name__)


# General MIDI drum mapping (standard across all DAWs)
DRUM_MIDI_NOTES = {
    'kick': 36,    # Bass Drum 1 (C1)
    'snare': 38,   # Acoustic Snare (D1)
    'hihat': 42,   # Closed Hi-Hat (F#1)
}


def create_drum_midi(
    drum_pattern: Dict[str, List[float]],
    output_path: str,
    tempo: float = 120.0,
    time_signature: tuple = (4, 4),
    velocity: int = 100
) -> str:
    """
    Create a MIDI file from a classified drum pattern.

    Args:
        drum_pattern: Dictionary with 'kick', 'snare', 'hihat' keys containing
                      lists of onset times in seconds
        output_path: Path where the MIDI file should be saved
        tempo: BPM (beats per minute)
        time_signature: Tuple of (numerator, denominator), e.g., (4, 4)
        velocity: MIDI velocity (0-127), default 100

    Returns:
        Path to the created MIDI file

    Example:
        >>> pattern = {
        ...     'kick': [0.0, 0.5, 1.0, 1.5],
        ...     'snare': [0.25, 0.75, 1.25],
        ...     'hihat': [0.0, 0.125, 0.25, 0.375, 0.5]
        ... }
        >>> midi_path = create_drum_midi(pattern, 'output.mid', tempo=128)
    """
    try:
        # Create MIDI file with 1 track
        midi = MIDIFile(1)

        # Track 0, time 0
        track = 0
        channel = 9  # Channel 10 (0-indexed as 9) is the standard MIDI drum channel
        time = 0

        # Add track name and tempo
        midi.addTrackName(track, time, "Drums")
        midi.addTempo(track, time, tempo)

        # Add time signature
        midi.addTimeSignature(
            track, time,
            time_signature[0],  # numerator
            time_signature[1],  # denominator
            24,  # MIDI clocks per tick
            8    # 32nd notes per quarter note
        )

        # Add drum hits for each type
        for drum_type, onset_times in drum_pattern.items():
            if drum_type not in DRUM_MIDI_NOTES:
                logger.warning(f"Unknown drum type '{drum_type}', skipping")
                continue

            midi_note = DRUM_MIDI_NOTES[drum_type]

            for onset_time in onset_times:
                # Convert seconds to beats (quarters)
                # beats = seconds * (tempo / 60)
                beat_time = onset_time * (tempo / 60.0)

                # Add note: track, channel, pitch, time (beats), duration (beats), velocity
                midi.addNote(
                    track,
                    channel,
                    midi_note,
                    beat_time,
                    0.25,  # Duration: quarter note
                    velocity
                )

        # Write MIDI file
        with open(output_path, 'wb') as output_file:
            midi.writeFile(output_file)

        logger.info(f"MIDI file created: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to create MIDI file: {str(e)}")
        raise RuntimeError(f"MIDI conversion failed: {str(e)}") from e


def create_drum_midi_with_velocity(
    drum_pattern: Dict[str, List[tuple]],
    output_path: str,
    tempo: float = 120.0,
    time_signature: tuple = (4, 4)
) -> str:
    """
    Create a MIDI file from a drum pattern with velocity information.

    Args:
        drum_pattern: Dictionary with 'kick', 'snare', 'hihat' keys containing
                      lists of (onset_time, velocity) tuples
        output_path: Path where the MIDI file should be saved
        tempo: BPM (beats per minute)
        time_signature: Tuple of (numerator, denominator)

    Returns:
        Path to the created MIDI file

    Example:
        >>> pattern = {
        ...     'kick': [(0.0, 120), (0.5, 100), (1.0, 115)],
        ...     'snare': [(0.25, 90), (0.75, 95)],
        ...     'hihat': [(0.0, 70), (0.125, 65), (0.25, 75)]
        ... }
        >>> midi_path = create_drum_midi_with_velocity(pattern, 'output.mid', tempo=128)
    """
    try:
        midi = MIDIFile(1)
        track = 0
        channel = 9
        time = 0

        midi.addTrackName(track, time, "Drums")
        midi.addTempo(track, time, tempo)
        midi.addTimeSignature(track, time, time_signature[0], time_signature[1], 24, 8)

        for drum_type, onset_data in drum_pattern.items():
            if drum_type not in DRUM_MIDI_NOTES:
                logger.warning(f"Unknown drum type '{drum_type}', skipping")
                continue

            midi_note = DRUM_MIDI_NOTES[drum_type]

            for onset_time, velocity in onset_data:
                beat_time = onset_time * (tempo / 60.0)

                # Ensure velocity is in valid range (0-127)
                velocity = max(0, min(127, int(velocity)))

                midi.addNote(track, channel, midi_note, beat_time, 0.25, velocity)

        with open(output_path, 'wb') as output_file:
            midi.writeFile(output_file)

        logger.info(f"MIDI file with velocity created: {output_path}")
        return output_path

    except Exception as e:
        logger.error(f"Failed to create MIDI file with velocity: {str(e)}")
        raise RuntimeError(f"MIDI conversion failed: {str(e)}") from e


def get_midi_metadata(drum_pattern: Dict[str, List[float]], tempo: float) -> dict:
    """
    Get metadata about the drum pattern for JSON response.

    Args:
        drum_pattern: Classified drum pattern
        tempo: BPM

    Returns:
        Dictionary with pattern statistics
    """
    total_hits = sum(len(hits) for hits in drum_pattern.values())

    metadata = {
        'total_hits': total_hits,
        'kick_count': len(drum_pattern.get('kick', [])),
        'snare_count': len(drum_pattern.get('snare', [])),
        'hihat_count': len(drum_pattern.get('hihat', [])),
        'tempo_bpm': tempo,
        'midi_mapping': DRUM_MIDI_NOTES
    }

    return metadata


def convert_pattern_to_json(drum_pattern: Dict[str, List[float]], tempo: float) -> dict:
    """
    Convert drum pattern to JSON format for frontend display.

    Args:
        drum_pattern: Classified drum pattern
        tempo: BPM

    Returns:
        JSON-serializable dictionary with MIDI data
    """
    return {
        'midi_data': {
            'kick': drum_pattern.get('kick', []),
            'snare': drum_pattern.get('snare', []),
            'hihat': drum_pattern.get('hihat', [])
        },
        'tempo': tempo,
        'time_signature': '4/4',
        'metadata': get_midi_metadata(drum_pattern, tempo)
    }
