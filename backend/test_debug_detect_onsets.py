"""
Debug to understand why detect_onsets() returns fewer onsets than direct librosa call.
"""
import librosa
from audio_processing.onset_detector import detect_onsets

drum_path = "storage/processed/service_test/stems/snippet_307923d3/drums.wav"

print("Method 1: Using audio_processing.detect_onsets()")
onsets1 = detect_onsets(drum_path)
print(f"  Onsets detected: {len(onsets1)}")
print(f"  First 10: {[f'{t:.3f}' for t in onsets1[:10]]}")

print("\nMethod 2: Direct librosa call (no backtrack)")
y, sr = librosa.load(drum_path, sr=None)
onset_frames = librosa.onset.onset_detect(y=y, sr=sr, units='frames')
onsets2 = librosa.frames_to_time(onset_frames, sr=sr).tolist()
print(f"  Onsets detected: {len(onsets2)}")
print(f"  First 10: {[f'{t:.3f}' for t in onsets2[:10]]}")

print("\nMethod 3: Direct librosa call (WITH backtrack - like detect_onsets)")
onset_frames3 = librosa.onset.onset_detect(y=y, sr=sr, units='frames', backtrack=True)
onsets3 = librosa.frames_to_time(onset_frames3, sr=sr).tolist()
print(f"  Onsets detected: {len(onsets3)}")
print(f"  First 10: {[f'{t:.3f}' for t in onsets3[:10]]}")

print("\nMethod 1 == Method 3?", onsets1 == onsets3)
