"""
Analyze all detected onsets to see if kicks are being misclassified.
"""
from audio_processing.onset_detector import analyze_drum_pattern
from audio_processing.drum_classifier import classify_drum_pattern
import numpy as np
import librosa

def analyze_all_onsets():
    drum_path = "storage/processed/service_test/stems/snippet_307923d3/drums.wav"

    print("="*80)
    print("DETAILED ONSET ANALYSIS")
    print("="*80)

    # Detect all onsets without filtering
    pattern = analyze_drum_pattern(drum_path, filter_weak=False)
    drum_pattern = classify_drum_pattern(drum_path, pattern['onset_times'])

    print(f"\nFile: {drum_path}")
    print(f"Duration: {pattern['duration_seconds']:.2f} seconds")
    print(f"Total onsets: {pattern['num_hits']}")
    print(f"Tempo: {pattern['tempo_bpm']:.1f} BPM")

    # Load audio for additional analysis
    y, sr = librosa.load(drum_path, sr=None)

    print(f"\n{'Time':>8} | {'Classification':>12} | {'Low Hz':>10} | {'Mid Hz':>10} | {'High Hz':>10}")
    print("-"*80)

    # Analyze each onset
    for i, onset_time in enumerate(pattern['onset_times']):
        onset_sample = int(onset_time * sr)

        # Extract 50ms window around onset
        window_samples = int(0.05 * sr)
        start_sample = max(0, onset_sample - window_samples // 2)
        end_sample = min(len(y), onset_sample + window_samples // 2)
        window = y[start_sample:end_sample]

        # FFT analysis
        fft = np.fft.rfft(window)
        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(window), 1/sr)

        # Energy in different bands
        kick_energy = np.sum(magnitudes[(freqs >= 20) & (freqs < 100)])
        snare_energy = np.sum(magnitudes[(freqs >= 150) & (freqs < 250)])
        hihat_energy = np.sum(magnitudes[(freqs >= 5000) & (freqs < 10000)])
        total_energy = np.sum(magnitudes)

        # Determine classification
        if onset_time in drum_pattern['kick']:
            classification = "KICK"
        elif onset_time in drum_pattern['snare']:
            classification = "SNARE"
        else:
            classification = "HI-HAT"

        # Show percentages
        kick_pct = (kick_energy / total_energy * 100) if total_energy > 0 else 0
        snare_pct = (snare_energy / total_energy * 100) if total_energy > 0 else 0
        hihat_pct = (hihat_energy / total_energy * 100) if total_energy > 0 else 0

        print(f"{onset_time:7.3f}s | {classification:>12} | {kick_pct:8.1f}% | {snare_pct:8.1f}% | {hihat_pct:8.1f}%")

    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print(f"Kicks detected:   {len(drum_pattern['kick'])}")
    print(f"Snares detected:  {len(drum_pattern['snare'])}")
    print(f"Hi-hats detected: {len(drum_pattern['hihat'])}")
    print("\nYou reported hearing ~15 kicks.")
    print("We only detected 6 kicks.")
    print("\nPossible issues:")
    print("1. Kicks being misclassified as hi-hats (check onsets with >20% low freq)")
    print("2. Kicks not being detected as onsets at all (onset detection too aggressive)")
    print("3. Classification threshold needs adjustment")

if __name__ == "__main__":
    analyze_all_onsets()
