# MiDiMe — Drum Pattern Analyzer

<img width="1311" height="1187" alt="Screenshot 2026-04-04 at 2 33 19 AM" src="https://github.com/user-attachments/assets/02d86062-5cbc-4484-8d61-0d878d368624" />

<img width="1311" height="1138" alt="Screenshot 2026-04-04 at 1 58 07 AM" src="https://github.com/user-attachments/assets/a42cac23-ce0b-4664-9316-c9a2ac9537dc" />

<img width="1311" height="818" alt="Screenshot 2026-04-04 at 2 23 04 AM" src="https://github.com/user-attachments/assets/e33dae92-a129-4c2b-b484-2be8e47e531d" />

## Project Overview

**MiDiMe** is a full-stack web application that helps music producers deconstruct drum patterns from audio. Upload any song, select a region, and the backend isolates the drum stem, detects individual hits, and returns a quantized grid-based pattern — ready to visualize, edit, and export as MIDI.

### Core Value Proposition

- **Visual Learning**: See exactly where kicks, snares, and hi-hats land on a step-sequencer grid
- **Region Selection**: Analyze up to 30-second snippets with draggable waveform handles
- **Preset Library**: Browse reference patterns (Boom Bap, Trap, House, etc.) before uploading
- **MIDI Export**: One-click export of any pattern directly into your DAW
- **Editable Grid**: Click cells to toggle hits and adjust patterns before exporting

---

## Current Status

**Phase**: Full-stack drum analysis MVP

### What Works

- Django backend with Demucs v4 stem separation + frequency-band fallback
- Onset detection, drum classification, and grid quantization pipeline
- React frontend with DrumDissect visualizer, waveform display, and region selector
- Explicit user-driven analysis flow: upload → select region → analyze → view results
- MIDI export of any displayed pattern
- Reference preset browser with editable grid
- Full CORS configuration for local development

### What's Next

- Celery async processing for large files
- Pattern database and similarity search
- Bass and chord analysis
- User accounts and tier-based access

---

## Tech Stack

### Backend

| Component | Technology |
|-----------|-----------|
| Framework | Django 4.2 + Django REST Framework 3.14 |
| Stem Separation | Demucs v4 (`htdemucs`, PyTorch-based) |
| Fallback Analyzer | scipy bandpass filtering (when Demucs unavailable) |
| Onset Detection | librosa 0.10 |
| Audio Utilities | pydub (trimming, format conversion) |
| Quantization | Custom `quantizer.py` (onset → grid alignment) |
| MIDI Generation | MIDIUtil 1.2.1 |
| CORS | django-cors-headers |
| Database | SQLite (dev), PostgreSQL (planned for prod) |

### Frontend

| Component | Technology |
|-----------|-----------|
| Framework | React 19 with functional components and hooks |
| HTTP Client | Axios |
| Styling | Tailwind CSS + custom `visualizer-theme.css` |
| Waveform | HTML5 Canvas (`waveform.js`) |
| State | React `useState` / `useRef` (no external state library) |
| MIDI Export | Client-side `exportMidi.js` |

---

## Project Structure

```
MiDiMe/
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── config/
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/
│   │   ├── views.py              # FileUpload, HealthCheck, AudioAnalyze views
│   │   ├── serializers.py        # Request validation (file, grid, region)
│   │   └── urls.py               # /api/upload, /api/health, /api/analyze
│   ├── audio_processing/
│   │   ├── stem_separator.py     # Demucs v4 stem separation
│   │   ├── band_analyzer.py      # Frequency-band fallback (no Demucs needed)
│   │   ├── quantizer.py          # Onset times → grid-aligned pattern
│   │   ├── onset_detector.py     # librosa onset detection
│   │   ├── drum_classifier.py    # Frequency-based kick/snare/hihat classification
│   │   ├── utils.py              # Audio trimming, format helpers
│   │   └── audio_service.py      # Legacy orchestration service
│   └── storage/                  # Temporary upload/processed files
│       ├── uploads/
│       └── processed/
│
├── frontend/
│   ├── package.json
│   ├── tailwind.config.js
│   ├── public/
│   │   └── index.html
│   └── src/
│       ├── App.js
│       ├── index.css
│       ├── visualizer-theme.css  # Full custom theme (transport, grid, cards)
│       ├── components/
│       │   ├── DrumDissect.jsx   # Main visualizer (waveform, grid, presets)
│       │   ├── FileUpload.jsx    # Legacy upload component
│       │   └── LoadingSpinner.jsx
│       ├── audio/
│       │   ├── drumAnalysis.js   # Pattern utilities (tileArray, etc.)
│       │   ├── exportMidi.js     # MIDI file generation + download
│       │   ├── waveform.js       # Canvas waveform rendering
│       │   └── sliceBuffer.js    # AudioBuffer region slicing
│       ├── data/
│       │   └── presets.js        # Reference drum patterns (Boom Bap, Trap, etc.)
│       └── services/
│           └── api.js            # Axios client (analyzeAudio, health check)
│
├── README.md
└── claude.md
```

---

## API Endpoints

### `GET /api/health`

Health check.

**Response**: `{ "status": "healthy", "timestamp": "..." }`

### `POST /api/analyze`

Analyze an audio file for drum patterns.

**Request** (multipart/form-data):

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `audio_file` | File | Yes | — | Audio file (mp3, wav, flac, m4a, ogg). Max 50MB |
| `grid_size` | int | No | 16 | Steps per bar (8, 16, or 32) |
| `bar_count` | int | No | 2 | Number of bars (1, 2, or 4) |
| `start_time` | float | No | — | Region start in seconds |
| `end_time` | float | No | — | Region end in seconds |

**Response**:
```json
{
  "status": "success",
  "analysis_id": "uuid",
  "method": "demucs",
  "pattern": {
    "kick": [1, 0, 0, 0, 1, 0, 0, 0, ...],
    "snare": [0, 0, 0, 0, 0, 0, 0, 0, ...],
    "hihat": [1, 1, 1, 1, 1, 1, 1, 1, ...],
    "kickVel": [0.9, 0, 0, 0, 0.85, 0, ...],
    "snareVel": [0, 0, 0, 0, 0, 0, 0, 0, ...],
    "hihatVel": [0.7, 0.5, 0.7, 0.5, ...],
    "bpm": 90,
    "swing": 12,
    "steps": 32,
    "style": { "name": "Hip Hop", "desc": "..." },
    "desc": "..."
  }
}
```

### `POST /api/upload`

Simple file upload (returns filename and size).

---

## Analysis Pipeline

```
Audio file uploaded
    ↓
Optional trim (start_time / end_time via pydub)
    ↓
Drum classification (try Demucs stem separation first)
    ├── Success: isolate drum stem → onset detection → classify hits
    └── Fallback: frequency-band filtering (scipy bandpass → onset detection)
    ↓
Tempo estimation (librosa beat tracking)
    ↓
Quantization (snap onsets to grid, compute velocities, swing, style)
    ↓
JSON response (grid arrays matching frontend DrumDissect format)
    ↓
Cleanup (delete temp files)
```

---

## User Flow

1. **Browse presets** — default screen shows reference patterns with info cards and editable grid
2. **Upload audio** — drag-and-drop or file picker (wav, mp3, aiff, flac)
3. **Waveform appears** — full track rendered on canvas with playback controls
4. **Select region** — drag handles to choose up to 30 seconds (min 1 second)
5. **Configure** — pick grid size (8/16/32 steps) and bar count (1/2/4 bars)
6. **Analyze** — click "Analyze Selection" to send region to backend
7. **View results** — info cards (Style, BPM, Swing, Density) and pattern grid populate
8. **Edit** — click grid cells to toggle hits on/off
9. **Export** — download as MIDI file

---

## Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- FFmpeg (for pydub audio conversion)

### Backend

```bash
cd backend
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 0.0.0.0:8000
```

### Frontend

```bash
cd frontend
npm install
npm start
```

The frontend runs on `http://localhost:3000` and proxies API calls to `http://localhost:8000`.

---

## Development Notes

### Code Style

- **Python**: PEP 8, type hints where helpful
- **React**: Functional components, hooks only, no class components
- **CSS**: Custom properties via `visualizer-theme.css`, Tailwind for utilities

### Key Design Decisions

- **Demucs over Spleeter**: Spleeter (TensorFlow 1.x) is unmaintained. Demucs v4 (PyTorch) produces higher-quality stems and is actively developed by Meta.
- **Frequency-band fallback**: When Demucs/PyTorch isn't available, scipy bandpass filters isolate kick (20-200Hz), snare (200-2000Hz), and hi-hat (5000-16000Hz) bands for onset detection. Lower quality but zero heavy dependencies.
- **Backend-only analysis**: All audio analysis runs server-side. The frontend sends the raw file and receives structured grid data — no client-side DSP.
- **Explicit analysis trigger**: Upload and region selection don't trigger analysis. The user must click "Analyze Selection" to send the request.

---

**Last Updated**: April 4, 2026
**Version**: 0.3.0 (Full-stack drum analysis MVP)
