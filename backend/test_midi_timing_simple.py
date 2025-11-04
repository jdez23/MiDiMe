"""
Create a simple test MIDI file with known timing to verify MIDI generation.
"""
from audio_processing.midi_converter import create_drum_midi
import os

def create_test_midi():
    """
    Create a simple test pattern:
    - Kicks on beats 1, 2, 3, 4 (every quarter note) at 120 BPM
    - This should create kicks exactly 0.5 seconds apart
    """

    print("="*80)
    print("SIMPLE MIDI TIMING TEST")
    print("="*80)

    tempo = 120.0  # BPM
    seconds_per_beat = 60 / tempo  # 0.5 seconds at 120 BPM

    # Create kicks at 0s, 0.5s, 1.0s, 1.5s (4 quarter notes)
    test_pattern = {
        'kick': [0.0, 0.5, 1.0, 1.5],
        'snare': [],
        'hihat': []
    }

    print(f"\nTest Pattern:")
    print(f"  Tempo: {tempo} BPM")
    print(f"  Seconds per beat: {seconds_per_beat}")
    print(f"  Kick times (seconds): {test_pattern['kick']}")
    print(f"  Kick times (beats): {[t * (tempo/60) for t in test_pattern['kick']]}")

    # Create MIDI
    output_dir = "storage/processed/midi_output"
    os.makedirs(output_dir, exist_ok=True)
    midi_path = os.path.join(output_dir, "test_simple_120bpm.mid")

    create_drum_midi(
        drum_pattern=test_pattern,
        output_path=midi_path,
        tempo=tempo,
        time_signature=(4, 4),
        velocity=100
    )

    print(f"\n✓ Test MIDI created: {midi_path}")
    print(f"\nExpected result when opened in DAW at 120 BPM:")
    print(f"  - Kick 1: Bar 1, Beat 1.0 (0.0 seconds)")
    print(f"  - Kick 2: Bar 1, Beat 2.0 (0.5 seconds)")
    print(f"  - Kick 3: Bar 1, Beat 3.0 (1.0 seconds)")
    print(f"  - Kick 4: Bar 1, Beat 4.0 (1.5 seconds)")
    print(f"\nIf kicks don't align with the beat grid:")
    print(f"  1. Check DAW tempo is set to 120 BPM")
    print(f"  2. There may be a MIDI time base issue")
    print(f"  3. The conversion formula may need adjustment")

    print("\n" + "="*80)

    # Now create one with the actual drum pattern tempo
    print("\nCreating MIDI with actual drum tempo (167 BPM)...")

    # Sample timing from actual drums
    actual_pattern = {
        'kick': [0.279, 0.627, 0.952, 1.707, 2.368],
        'snare': [],
        'hihat': []
    }

    midi_path_167 = os.path.join(output_dir, "test_actual_167bpm.mid")

    create_drum_midi(
        drum_pattern=actual_pattern,
        output_path=midi_path_167,
        tempo=166.7,
        time_signature=(4, 4),
        velocity=100
    )

    print(f"✓ Actual pattern MIDI created: {midi_path_167}")
    print(f"  Set DAW to: 166.7 BPM")
    print(f"  First kick should be at: {0.279 * (166.7/60):.3f} beats = {0.279:.3f} seconds")

if __name__ == "__main__":
    create_test_midi()
