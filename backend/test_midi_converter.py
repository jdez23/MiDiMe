"""
Test MIDI converter with real drum pattern data.
"""
from audio_processing.onset_detector import analyze_drum_pattern
from audio_processing.drum_classifier import classify_drum_pattern
from audio_processing.midi_converter import (
    create_drum_midi,
    convert_pattern_to_json,
    get_midi_metadata
)
import os

def test_midi_conversion():
    drum_path = "storage/processed/service_test/stems/snippet_307923d3/drums.wav"

    print("="*80)
    print("MIDI CONVERTER TEST")
    print("="*80)

    # Analyze drum pattern
    print(f"\n1. Analyzing drum audio: {drum_path}")
    pattern_analysis = analyze_drum_pattern(drum_path)
    print(f"   Detected {pattern_analysis['num_hits']} onsets at {pattern_analysis['tempo_bpm']:.1f} BPM")

    # Classify drums
    print(f"\n2. Classifying drum hits...")
    drum_pattern = classify_drum_pattern(drum_path, pattern_analysis['onset_times'])

    num_kicks = len(drum_pattern['kick'])
    num_snares = len(drum_pattern['snare'])
    num_hihats = len(drum_pattern['hihat'])

    print(f"   Kicks:   {num_kicks}")
    print(f"   Snares:  {num_snares}")
    print(f"   Hi-hats: {num_hihats}")

    # Create MIDI file
    print(f"\n3. Converting to MIDI format...")
    output_dir = "storage/processed/midi_output"
    os.makedirs(output_dir, exist_ok=True)

    midi_path = os.path.join(output_dir, "drum_pattern.mid")

    create_drum_midi(
        drum_pattern=drum_pattern,
        output_path=midi_path,
        tempo=pattern_analysis['tempo_bpm'],
        time_signature=(4, 4),
        velocity=100
    )

    print(f"   ✓ MIDI file created: {midi_path}")

    # Get metadata
    print(f"\n4. MIDI Metadata:")
    metadata = get_midi_metadata(drum_pattern, pattern_analysis['tempo_bpm'])
    for key, value in metadata.items():
        print(f"   {key}: {value}")

    # Convert to JSON for API response
    print(f"\n5. JSON Response Format:")
    json_data = convert_pattern_to_json(drum_pattern, pattern_analysis['tempo_bpm'])
    print(f"   Tempo: {json_data['tempo']} BPM")
    print(f"   Time Signature: {json_data['time_signature']}")
    print(f"   Total Hits: {json_data['metadata']['total_hits']}")
    print(f"   MIDI Mapping: {json_data['metadata']['midi_mapping']}")

    # File size check
    file_size = os.path.getsize(midi_path)
    print(f"\n6. File Info:")
    print(f"   Size: {file_size} bytes ({file_size/1024:.2f} KB)")
    print(f"   Path: {os.path.abspath(midi_path)}")

    print("\n" + "="*80)
    print("TEST COMPLETE")
    print("="*80)
    print(f"\n✓ MIDI file successfully created!")
    print(f"✓ You can now import '{midi_path}' into any DAW")
    print(f"✓ Standard General MIDI drum mapping used")
    print(f"\nNext steps:")
    print("  1. Open the MIDI file in Logic/FL Studio/Ableton to verify")
    print("  2. Check that kicks, snares, and hi-hats are on correct MIDI notes")
    print("  3. Verify timing matches the original audio")

if __name__ == "__main__":
    test_midi_conversion()
