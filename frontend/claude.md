# Frontend — React Drum Visualizer

## Running

```bash
cd frontend
npm install
npm start
```

Runs on `http://localhost:3000`. API calls go to `http://localhost:8000` (configured in `src/services/api.js` via `REACT_APP_API_URL` env var).

## Key Files

### `src/components/DrumDissect.jsx`
The main component. Handles everything: file upload, waveform display, region selection, preset browsing, backend analysis, pattern grid, and MIDI export. ~780 lines.

**State highlights:**
- `audioBuffer` — decoded AudioBuffer (null when no file loaded)
- `currentPattern` — the active pattern object (from preset or backend)
- `regionStart` / `regionEnd` — selected region in seconds (max 30s)
- `gridSize` / `barCount` — analysis parameters (8/16/32 steps, 1/2/4 bars)
- `loading` / `error` — UI state for the analysis request

**Important refs:**
- `uploadedFileRef` — holds the File object for re-analysis (ref, not state, to avoid re-renders)
- `audioCtxRef` — Web Audio AudioContext (created once)
- `draggingRef` — tracks which region handle is being dragged

### `src/services/api.js`
Axios-based API client. All backend communication goes through here.

Key methods:
- `api.analyzeAudio(file, gridSize, barCount, startTime, endTime)` — POST to `/api/analyze`
- `api.isBackendAvailable()` — cached health check
- `api.checkHealth()` — raw health check

### `src/audio/`
- `drumAnalysis.js` — `tileArray()` for repeating pattern arrays to fill grid
- `exportMidi.js` — `buildDrumPatternMidi()` + `downloadBlob()` for MIDI export
- `waveform.js` — `drawWaveform(canvas, audioBuffer)` renders waveform to canvas
- `sliceBuffer.js` — `sliceAudioBuffer()` for copying a region of an AudioBuffer

### `src/data/presets.js`
Reference drum patterns (Boom Bap, Trap, House, etc.). Each preset has kick/snare/hihat arrays, velocity arrays, bpm, swing, genre, and description.

### `src/visualizer-theme.css`
Full custom theme. Uses CSS custom properties:
- `--cream`, `--cream-dark`, `--cream-deep` — background tones
- `--ink`, `--ink-soft`, `--ink-whisper` — text/border tones
- `--kick`, `--snare`, `--hihat` — instrument accent colors

Key class groups: `.drop-zone-*`, `.transport-*`, `.waveform-*`, `.region-*`, `.grid-*`, `.info-card`, `.preset-*`, `.controls-row`, `.analyze-btn`, `.export-btn`

## Pattern Data Shape

Every pattern (preset or backend-returned) must have this shape:

```javascript
{
  kick: [1, 0, 0, 0, ...],      // binary array, length = steps
  snare: [0, 0, 0, 0, ...],
  hihat: [1, 1, 1, 1, ...],
  kickVel: [0.9, 0, 0, 0, ...], // velocity 0.0–1.0
  snareVel: [0, 0, 0, 0, ...],
  hihatVel: [0.7, 0.5, ...],
  bpm: 90,
  swing: 12,                     // percentage
  steps: 32,                     // gridSize * barCount
  style: { name: "Hip Hop", desc: "..." },
  desc: "..."
}
```

## User Flow

1. Default screen shows preset buttons + info cards + pattern grid
2. Upload file → waveform + region selector appear; cards/grid clear
3. Adjust region handles, pick grid/bars
4. Click "Analyze Selection" → loading overlay → backend processes
5. Results populate cards and grid
6. Edit grid cells by clicking
7. Export MIDI

## Conventions

- No client-side audio analysis. All analysis goes through the backend.
- The analysis is explicit — only triggered by the "Analyze Selection" button, never automatic.
- Presets populate `currentPattern` directly. Backend results also set `currentPattern`.
- When `currentPattern` is null (after upload, before analysis), info cards and grid are hidden.
