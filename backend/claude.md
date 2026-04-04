# Backend — Django Audio Analysis API

## Running

```bash
cd backend
python manage.py runserver 0.0.0.0:8000
```

Settings are in `config/settings.py`. CORS is configured for `localhost:3000`.

## Project Layout

- `config/` — Django settings, root URLs, WSGI
- `api/` — REST endpoints (views, serializers, URLs)
- `audio_processing/` — All audio analysis logic (no Django dependencies)
- `storage/` — Temporary files (uploads/ and processed/). Gitignored.

## API Endpoints

| Method | Path | View | Purpose |
|--------|------|------|---------|
| GET | `/api/health` | `HealthCheckView` | Liveness check |
| POST | `/api/upload` | `FileUploadView` | Simple file upload |
| POST | `/api/analyze` | `AudioAnalyzeView` | Drum pattern analysis |

## Audio Processing Modules

### `stem_separator.py`
Demucs v4 stem separation. Exports `separate_stems(audio_path, output_dir)`. Returns dict of stem paths `{ "drums": "...", "bass": "...", ... }`.

### `band_analyzer.py`
Lightweight fallback when Demucs is unavailable. Uses scipy Butterworth bandpass filters to isolate frequency bands:
- Kick: 20–200 Hz
- Snare: 200–2000 Hz
- Hi-hat: 5000–16000 Hz

Exports `analyze_by_frequency_bands(audio_path)` and `get_tempo_from_audio(audio_path)`.

### `quantizer.py`
Converts raw onset times (seconds) into grid-aligned binary arrays. This is the bridge between backend analysis and frontend display.

Key function: `build_pattern_response(drum_onsets, tempo, grid_size, bar_count)` returns the pattern object that matches what `DrumDissect.jsx` expects.

### `onset_detector.py`
librosa-based onset detection. Used after stem separation to find hit times.

### `drum_classifier.py`
Classifies detected onsets into kick/snare/hihat by analyzing frequency content at each onset time.

### `utils.py`
Audio trimming with pydub. `trim_audio(input_path, output_path, start_sec, end_sec)`. Validates duration between 1–300 seconds.

## Analysis Flow in `AudioAnalyzeView.post()`

1. Validate request via `AudioAnalyzeSerializer`
2. Save uploaded file to `storage/uploads/`
3. Optionally trim to `start_time`–`end_time`
4. `_classify_drums()`: try Demucs pipeline, catch ImportError → band_analyzer fallback
5. `_get_tempo()`: librosa beat tracking
6. `build_pattern_response()`: quantize to grid
7. Return JSON with pattern data
8. `_cleanup()` in finally block

## Dependencies

All in `requirements.txt`. Key ones:
- `demucs` — stem separation (pulls in PyTorch)
- `librosa` — onset detection, tempo estimation
- `scipy` — bandpass filtering for fallback analyzer
- `pydub` — audio trimming (requires FFmpeg)
- `MIDIUtil` — MIDI file generation
