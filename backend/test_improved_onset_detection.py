"""
Test improved onset detection specifically for drums.
"""
import numpy as np
import librosa
from audio_processing.drum_classifier import classify_drum_pattern

def detect_drum_onsets_improved(audio_path: str):
    """
    Improved onset detection optimized for drum sounds.
    """
    y, sr = librosa.load(audio_path, sr=None)

    # Try multiple onset detection methods
    methods = []

    # Method 1: Default (energy-based)
    onset_frames_default = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        units='frames'
    )
    methods.append(('Default', librosa.frames_to_time(onset_frames_default, sr=sr)))

    # Method 2: Percussive separation (best for drums)
    y_harmonic, y_percussive = librosa.effects.hpss(y)
    onset_frames_perc = librosa.onset.onset_detect(
        y=y_percussive,
        sr=sr,
        units='frames'
    )
    methods.append(('Percussive', librosa.frames_to_time(onset_frames_perc, sr=sr)))

    # Method 3: Lower delta threshold (more sensitive)
    onset_frames_sensitive = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        delta=0.02,  # Lower threshold = more onsets
        units='frames'
    )
    methods.append(('Sensitive', librosa.frames_to_time(onset_frames_sensitive, sr=sr)))

    # Method 4: Complex domain onset detection
    onset_frames_complex = librosa.onset.onset_detect(
        y=y,
        sr=sr,
        onset_envelope=librosa.onset.onset_strength(y=y, sr=sr, aggregate=np.median),
        units='frames'
    )
    methods.append(('Complex', librosa.frames_to_time(onset_frames_complex, sr=sr)))

    return methods

def test_all_methods():
    drum_path = "storage/processed/service_test/stems/snippet_307923d3/drums.wav"

    print("="*80)
    print("COMPARING ONSET DETECTION METHODS FOR DRUMS")
    print("="*80)
    print(f"\nFile: {drum_path}")
    print(f"Expected: ~15 kicks based on user feedback\n")

    methods = detect_drum_onsets_improved(drum_path)

    for method_name, onset_times in methods:
        onset_list = onset_times.tolist()

        print(f"\n{method_name} Method:")
        print(f"  Total onsets detected: {len(onset_list)}")

        # Classify the onsets
        drum_pattern = classify_drum_pattern(drum_path, onset_list)
        num_kicks = len(drum_pattern['kick'])
        num_snares = len(drum_pattern['snare'])
        num_hihats = len(drum_pattern['hihat'])

        print(f"  Kicks:   {num_kicks:2d} ({num_kicks/len(onset_list)*100:.1f}%)")
        print(f"  Snares:  {num_snares:2d} ({num_snares/len(onset_list)*100:.1f}%)")
        print(f"  Hi-hats: {num_hihats:2d} ({num_hihats/len(onset_list)*100:.1f}%)")

        # Show first 10 kick timings
        if num_kicks > 0:
            print(f"  Kick timings: ", end='')
            for t in drum_pattern['kick'][:10]:
                print(f"{t:.2f}s ", end='')
            if num_kicks > 10:
                print(f"... ({num_kicks-10} more)")
            else:
                print()

    print("\n" + "="*80)
    print("RECOMMENDATION")
    print("="*80)
    print("\nWhich method detected closest to 15 kicks?")
    print("That's the method we should use for production.")

if __name__ == "__main__":
    test_all_methods()
