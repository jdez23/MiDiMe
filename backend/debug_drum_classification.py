"""
Debug script to analyze drum classification issues.
Prints detailed frequency analysis for each detected onset.
"""
import numpy as np
import librosa
from audio_processing.onset_detector import detect_onsets
from audio_processing.drum_classifier import classify_drum_hit

def analyze_onset_frequencies(audio_path: str, onset_times: list, window_ms: int = 50):
    """
    Detailed frequency analysis for each onset.
    """
    y, sr = librosa.load(audio_path, sr=None)

    print(f"\n{'='*80}")
    print(f"Audio: {audio_path}")
    print(f"Sample rate: {sr} Hz")
    print(f"Duration: {len(y)/sr:.2f} seconds")
    print(f"Total onsets detected: {len(onset_times)}")
    print(f"{'='*80}\n")

    window_samples = int(window_ms * sr / 1000)

    for i, onset_time in enumerate(onset_times):
        onset_sample = int(onset_time * sr)
        start_sample = max(0, onset_sample - window_samples // 2)
        end_sample = min(len(y), onset_sample + window_samples // 2)

        # Extract window around onset
        window = y[start_sample:end_sample]

        # Compute FFT
        fft = np.fft.rfft(window)
        magnitudes = np.abs(fft)
        freqs = np.fft.rfftfreq(len(window), 1/sr)

        # Analyze frequency bands
        kick_mask = (freqs >= 20) & (freqs < 100)
        snare_mask = (freqs >= 150) & (freqs < 250)
        hihat_mask = (freqs >= 5000) & (freqs < 10000)

        kick_energy = np.sum(magnitudes[kick_mask])
        snare_energy = np.sum(magnitudes[snare_mask])
        hihat_energy = np.sum(magnitudes[hihat_mask])

        # Additional analysis
        total_energy = np.sum(magnitudes)
        spectral_centroid = np.sum(freqs * magnitudes) / np.sum(magnitudes)
        max_freq_idx = np.argmax(magnitudes)
        dominant_freq = freqs[max_freq_idx]

        # Wider hi-hat band
        hihat_wide_mask = (freqs >= 3000) & (freqs < 15000)
        hihat_wide_energy = np.sum(magnitudes[hihat_wide_mask])

        print(f"Onset #{i+1} at {onset_time:.3f}s:")
        print(f"  Classification: {classify_drum_hit(y, sr, onset_sample)}")
        print(f"  Dominant frequency: {dominant_freq:.1f} Hz")
        print(f"  Spectral centroid: {spectral_centroid:.1f} Hz")
        print(f"  Total energy: {total_energy:.2e}")
        print(f"  Energy by band:")
        print(f"    Kick (20-100 Hz):      {kick_energy:.2e} ({kick_energy/total_energy*100:.1f}%)")
        print(f"    Snare (150-250 Hz):    {snare_energy:.2e} ({snare_energy/total_energy*100:.1f}%)")
        print(f"    Hi-hat (5-10 kHz):     {hihat_energy:.2e} ({hihat_energy/total_energy*100:.1f}%)")
        print(f"    Hi-hat wide (3-15 kHz): {hihat_wide_energy:.2e} ({hihat_wide_energy/total_energy*100:.1f}%)")
        print(f"{'-'*80}\n")

if __name__ == "__main__":
    # Use the drum stem from previous test
    drum_path = "storage/processed/service_test/stems/snippet_307923d3/drums.wav"

    print("Detecting onsets...")
    onset_times = detect_onsets(drum_path)

    print(f"\nAnalyzing {len(onset_times)} onsets with detailed frequency breakdown...")
    analyze_onset_frequencies(drum_path, onset_times, window_ms=50)

    print("\n" + "="*80)
    print("ANALYSIS COMPLETE")
    print("="*80)
    print("\nReview the frequency energy percentages above.")
    print("If hi-hats exist but show low energy in the 5-10kHz band,")
    print("we may need to:")
    print("  1. Widen the hi-hat frequency range")
    print("  2. Use spectral centroid as additional feature")
    print("  3. Adjust window size")
    print("  4. Use different energy weighting")
