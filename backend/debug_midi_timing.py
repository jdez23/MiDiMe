"""
Debug MIDI timing alignment issues.
"""
from audio_processing.onset_detector import analyze_drum_pattern
from audio_processing.drum_classifier import classify_drum_pattern
import librosa

def debug_timing():
    drum_path = "storage/processed/service_test/stems/snippet_307923d3/drums.wav"

    print("="*80)
    print("MIDI TIMING DEBUG")
    print("="*80)

    # Get audio info
    y, sr = librosa.load(drum_path, sr=None)
    duration = len(y) / sr

    print(f"\nAudio Info:")
    print(f"  Duration: {duration:.2f} seconds")
    print(f"  Sample rate: {sr} Hz")
    print(f"  Total samples: {len(y)}")

    # Get tempo
    tempo_est, _ = librosa.beat.beat_track(y=y, sr=sr)
    tempo = float(tempo_est)

    # Get onsets directly
    onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
    onset_times = librosa.frames_to_time(onset_frames, sr=sr).tolist()

    print(f"\nTempo Detection:")
    print(f"  Detected tempo: {tempo:.2f} BPM")
    print(f"  Beats per second: {tempo/60:.2f}")
    print(f"  Seconds per beat: {60/tempo:.3f}")

    # Just use first few onsets as "kicks" for timing test
    drum_pattern = {'kick': onset_times[:5], 'snare': [], 'hihat': []}

    # Show first few kicks with timing info
    print(f"\nFirst 5 Kick Timings:")
    print(f"  {'Time (s)':>10} | {'Beat':>10} | {'Bar:Beat':>10} | {'Sample':>12}")
    print(f"  {'-'*10} | {'-'*10} | {'-'*10} | {'-'*12}")

    for i, kick_time in enumerate(drum_pattern['kick'][:5]):
        # Convert to beats
        beat = kick_time * (tempo / 60.0)

        # Convert to bar:beat notation (assuming 4/4)
        bar = int(beat // 4) + 1
        beat_in_bar = (beat % 4) + 1

        # Convert to sample
        sample = int(kick_time * sr)

        print(f"  {kick_time:10.3f} | {beat:10.2f} | {bar}:{beat_in_bar:.2f} | {sample:12d}")

    print(f"\nMIDI Time Calculation:")
    print(f"  Formula: beat_time = onset_time_seconds * (tempo / 60)")
    print(f"  Example for first kick at {drum_pattern['kick'][0]:.3f}s:")
    kick_time = drum_pattern['kick'][0]
    beat_time = kick_time * (tempo / 60.0)
    print(f"    {kick_time:.3f} * ({tempo:.2f} / 60) = {beat_time:.3f} beats")

    print(f"\nPotential Issues:")
    print(f"  1. MIDI uses beats (quarter notes) as time unit")
    print(f"  2. Our onset times are in seconds")
    print(f"  3. Conversion: seconds → beats requires accurate tempo")
    print(f"  4. DAW playback tempo must match detected tempo ({tempo:.1f} BPM)")

    print(f"\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)
    print(f"\nWhen you open the MIDI in your DAW:")
    print(f"  • Set the DAW project tempo to: {tempo:.1f} BPM")
    print(f"  • Set time signature to: 4/4")
    print(f"  • The first kick should appear at: beat {drum_pattern['kick'][0] * (tempo/60):.2f}")
    print(f"  • In bar:beat notation: bar 1, beat {(drum_pattern['kick'][0] * (tempo/60) % 4) + 1:.2f}")

    print(f"\nIf timing is still wrong, the issue could be:")
    print(f"  1. Tempo detection is inaccurate ({tempo:.1f} BPM may be wrong)")
    print(f"  2. DAW tempo doesn't match MIDI file tempo")
    print(f"  3. MIDI time calculation needs offset adjustment")

if __name__ == "__main__":
    debug_timing()
