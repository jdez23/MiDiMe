# MiDiMe — Project Guide

## What This Project Is

MiDiMe is a full-stack drum pattern analyzer. Users upload audio, select a region, and the backend separates the drum stem, detects onsets, and returns a quantized grid pattern that the frontend visualizes.

## Architecture

- **Backend**: Django 4.2 + DRF. Runs on port 8000.
- **Frontend**: React 19 + Tailwind CSS. Runs on port 3000.
- **No shared code** between frontend and backend. They communicate via REST API only.

## The Analysis Pipeline

```
POST /api/analyze (multipart: audio_file, grid_size, bar_count, start_time, end_time)
    → AudioAnalyzeSerializer validates
    → AudioAnalyzeView.post() orchestrates:
        1. Save temp file
        2. Optional trim (pydub)
        3. Drum classification:
           - Primary: Demucs stem separation → onset detection → classify
           - Fallback: scipy bandpass filtering → onset detection
        4. Tempo estimation (librosa)
        5. Quantization (quantizer.py → grid arrays + velocities + swing + style)
    → Response: { status, analysis_id, method, pattern: { kick, snare, hihat, *Vel, bpm, swing, steps, style, desc } }
    → Cleanup temp files
```

## Frontend Data Flow

The frontend component `DrumDissect.jsx` is the main UI. It manages:
- Preset patterns (browsable reference library)
- File upload and AudioBuffer decoding
- Waveform rendering (canvas) with region selection
- Explicit "Analyze Selection" button → calls `api.analyzeAudio()`
- Pattern grid (editable step sequencer)
- Info cards (Style, BPM, Swing, Density)
- MIDI export

Analysis is NOT automatic. The user must click "Analyze Selection" after uploading and choosing a region.

## Key Conventions

- **Python**: PEP 8. Use type hints for function signatures.
- **React**: Functional components only. Hooks for state. No class components.
- **CSS**: Custom properties defined in `visualizer-theme.css`. Tailwind for utilities. The theme uses a warm cream/ink palette.
- **API client**: All backend calls go through `frontend/src/services/api.js`. Never call axios directly from components.
- **Temporary files**: Backend saves uploads to `storage/uploads/`, processed files to `storage/processed/`. Always clean up in a `finally` block.

## Common Tasks

### Adding a new API endpoint
1. Add serializer in `backend/api/serializers.py`
2. Add view in `backend/api/views.py`
3. Add URL in `backend/api/urls.py`

### Adding a new audio processing module
1. Create module in `backend/audio_processing/`
2. Export from `backend/audio_processing/__init__.py`
3. Call from the appropriate view

### Modifying the drum grid UI
1. Edit `frontend/src/components/DrumDissect.jsx`
2. Style changes go in `frontend/src/visualizer-theme.css`
3. Pattern data shape: `{ kick, snare, hihat, kickVel, snareVel, hihatVel, bpm, swing, steps, style: { name, desc }, desc }`

## Things to Watch Out For

- The `DrumDissect` component is large (~780 lines). State is managed with many `useState` / `useRef` hooks. Be careful with effect dependencies.
- `uploadedFileRef` is a ref (not state) so it doesn't trigger re-renders. This is intentional — we need the File object for re-analysis but don't want renders on assignment.
- Region drag updates `regionStart`/`regionEnd` on every mouse move. Don't put expensive operations in effects that depend on these.
- Demucs requires PyTorch. The `_classify_drums` method in views.py catches ImportError and falls back to `band_analyzer.py` automatically.
- pydub requires FFmpeg on the system PATH for non-wav formats.
