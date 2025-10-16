"""
Final test with corrected parameters - should detect ~15 kicks.
"""
import librosa
from audio_processing.drum_classifier import classify_drum_pattern

def detect_drums_correctly(audio_path: str):
    """
    Correct drum detection without over-filtering.
    Uses default librosa parameters which work well.
    """
    y, sr = librosa.load(audio_path, sr=None)

    # Default onset detection (works best for drums)
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
    onset_times = librosa.frames_to_time(onset_frames, sr=sr).tolist()

    return onset_times

def main():
    drum_path = "storage/processed/service_test/stems/snippet_307923d3/drums.wav"

    print("="*80)
    print("CORRECTED DRUM DETECTION & CLASSIFICATION")
    print("="*80)
    print(f"\nFile: {drum_path}")
    print(f"User expectation: ~15 kicks\n")

    # Detect onsets
    onset_times = detect_drums_correctly(drum_path)

    print(f"Total onsets detected: {len(onset_times)}")

    # Classify
    drum_pattern = classify_drum_pattern(drum_path, onset_times)

    num_kicks = len(drum_pattern['kick'])
    num_snares = len(drum_pattern['snare'])
    num_hihats = len(drum_pattern['hihat'])

    print(f"\nClassification Results:")
    print(f"  Kicks:   {num_kicks:2d} ({num_kicks/len(onset_times)*100:.1f}%)")
    print(f"  Snares:  {num_snares:2d} ({num_snares/len(onset_times)*100:.1f}%)")
    print(f"  Hi-hats: {num_hihats:2d} ({num_hihats/len(onset_times)*100:.1f}%)")

    print(f"\nAll kick timings:")
    for i, t in enumerate(drum_pattern['kick'], 1):
        print(f"  Kick {i:2d}: {t:6.3f}s")

    print(f"\nAll snare timings:")
    for i, t in enumerate(drum_pattern['snare'], 1):
        print(f"  Snare {i:2d}: {t:6.3f}s")

    print("\n" + "="*80)
    print("RESULT")
    print("="*80)
    print(f"\nDetected {num_kicks} kicks vs your expectation of ~15 kicks")

    if 13 <= num_kicks <= 17:
        print("✓ EXCELLENT MATCH!")
    elif 10 <= num_kicks <= 20:
        print("✓ Good match (within reasonable range)")
    else:
        print("✗ Needs further tuning")

    print("\nThe fix: Use default onset detection WITHOUT filter_weak=True")
    print("         This captures all drum hits including quieter ones.")

if __name__ == "__main__":
    main()
