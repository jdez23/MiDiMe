# Music Pattern Analyzer (MiDiMe)

## 🎵 Project Overview

**Music Pattern Analyzer** is a web application designed to help music producers deconstruct and understand the musical elements of their favorite songs. By uploading audio files and selecting specific sections, users can visualize drum patterns, melodic structures, and other musical elements in a format that's easy to recreate in their DAW (Digital Audio Workstation).

### The Problem We're Solving
Producers often hear amazing patterns in songs but struggle to identify exactly when each element hits. Traditional transcription is time-consuming and requires advanced ear training. This tool uses AI-powered audio analysis to automatically detect and visualize these patterns.

### Core Value Proposition
- **Visual Learning**: See exactly where snares, kicks, and hi-hats hit in a piano roll format
- **Quick Analysis**: Analyze 15-30 second snippets instead of entire songs
- **DAW-Ready**: Future MIDI export lets you drop patterns directly into Logic, FL Studio, or Ableton
- **Genre Learning**: Understand how different genres structure their rhythmic elements

---

## 🎯 Current Status

**Phase**: MVP Development - Drum Pattern Analysis
**Target Launch**: 8 weeks from project start
**Current Focus**: Phase 1 - Foundation Setup

### Recent Progress (October 13, 2025)
✅ **Phase 1 COMPLETE - Full Stack File Upload Working!**

**Django Backend:**
- Django 4.2.7 with Django REST Framework configured
- `/api/upload` endpoint with file validation (MP3, WAV, FLAC, M4A, OGG)
- `/api/health` endpoint for health checks
- CORS configured for React frontend
- File size validation (max 50MB)
- Server running at `http://localhost:8000`

**React Frontend:**
- React 19.2.0 with Tailwind CSS 3.3.0
- Beautiful drag-and-drop file upload UI
- Real-time upload progress tracking
- Client-side and server-side validation
- Error handling with clear messages
- Server running at `http://localhost:3000`

📋 **Next Up (Phase 2):**
- Install and configure Spleeter for stem separation
- Implement audio trimming functionality
- Add librosa for onset detection

---

## 🏗️ Architecture

### High-Level Flow
```
User uploads audio → Selects 15-30s snippet → Chooses instrument (drums) 
→ Backend separates stems → Detects onsets → Converts to MIDI data 
→ Frontend displays visual piano roll
```

### Tech Stack

#### Backend
- **Framework**: Django 4.x with Django REST Framework
- **Audio Separation**: Spleeter (Facebook's pre-trained model)
- **Audio Analysis**: librosa for onset detection and audio manipulation
- **Audio Utilities**: pydub for trimming and format conversion
- **Task Queue**: Celery (post-MVP for async processing)
- **Database**: PostgreSQL (for caching results)
- **Storage**: Temporary local storage (will migrate to S3 for production)

#### Frontend
- **Framework**: React 18+ with functional components and hooks
- **Waveform Display**: wavesurfer.js
- **Visualization**: HTML5 Canvas or Tone.js for piano roll display
- **State Management**: React Context API (Redux if needed later)
- **HTTP Client**: Axios
- **Styling**: Tailwind CSS

#### DevOps
- **Backend Hosting**: Railway / Render / DigitalOcean
- **Frontend Hosting**: Vercel / Netlify
- **Version Control**: Git / GitHub

---

## 📁 Project Structure

```
music-pattern-analyzer/
├── backend/
│   ├── manage.py
│   ├── config/                      # Django settings
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/                         # REST API endpoints
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── tests.py
│   ├── audio_processing/            # Audio analysis logic
│   │   ├── stem_separator.py       # Spleeter integration
│   │   ├── onset_detector.py       # librosa onset detection
│   │   ├── midi_converter.py       # Convert onsets to MIDI
│   │   ├── drum_classifier.py      # Classify kick/snare/hihat
│   │   └── utils.py
│   ├── storage/                     # Temporary file storage
│   │   ├── uploads/
│   │   └── processed/
│   └── requirements.txt
│
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── FileUpload.jsx
│   │   │   ├── WaveformDisplay.jsx
│   │   │   ├── InstrumentSelector.jsx
│   │   │   ├── PianoRoll.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── services/
│   │   │   └── api.js              # API calls to backend
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/                            # Documentation
│   ├── API.md                       # API endpoint documentation
│   ├── ARCHITECTURE.md              # System architecture details
│   └── ROADMAP.md                   # Development roadmap
│
├── .clinerules                      # Claude Code guidelines
├── README.md                        # This file
└── .gitignore
```

---

## 🔌 API Endpoints

### MVP Endpoints

#### POST `/api/analyze`
Analyzes an audio snippet and returns MIDI pattern data.

**Request**:
```json
{
  "audio_file": "<file>",
  "start_time": 30.5,
  "end_time": 45.5,
  "instrument": "drums"
}
```

**Response**:
```json
{
  "status": "success",
  "duration": 15.0,
  "midi_data": {
    "kick": [0.0, 2.0, 4.0, 6.0, 8.0],
    "snare": [1.0, 3.0, 5.0, 7.0, 9.0],
    "hihat": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, ...]
  },
  "tempo": 120,
  "time_signature": "4/4"
}
```

#### GET `/api/health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-13T10:30:00Z"
}
```

---

## 🎨 User Workflow

1. **Upload**: User uploads an audio file (MP3, WAV, etc.)
2. **Visualize**: Waveform displays the full song
3. **Select**: User drags to select a 15-30 second snippet
4. **Choose**: User selects which instrument to analyze (drums for MVP)
5. **Analyze**: Click "Analyze" button, loading indicator appears
6. **View**: Piano roll visualization shows the pattern with time-aligned hits
7. **Learn**: User can now recreate the pattern in their DAW

---

## 🧪 Data Flow Details

### Audio Processing Pipeline

1. **Upload & Validation**
   - Validate file format (MP3, WAV, FLAC)
   - Check file size (limit: 50MB for MVP)
   - Save to temporary storage

2. **Snippet Extraction**
   - Use librosa or pydub to extract the user-selected time range
   - Convert to standard format (44.1kHz, stereo)

3. **Stem Separation (Spleeter)**
   - Input: trimmed audio file
   - Process: Spleeter 4-stem model (drums, bass, vocals, other)
   - Output: isolated drum track as WAV file

4. **Onset Detection (librosa)**
   - Input: isolated drum track
   - Process: `librosa.onset.onset_detect()` with optimized parameters
   - Output: array of timestamps where drum hits occur

5. **Drum Classification**
   - Analyze frequency content at each onset
   - Low frequencies (20-100Hz) → Kick drum
   - Mid frequencies (150-250Hz) → Snare
   - High frequencies (5000Hz+) → Hi-hat
   - Output: classified hits with timestamps

6. **MIDI Formatting**
   - Convert timestamps to MIDI note numbers
   - Standard mapping: Kick=36, Snare=38, Hi-hat=42
   - Create JSON structure for frontend rendering

7. **Response**
   - Return MIDI data to frontend
   - Clean up temporary files

---

## 🚀 Development Phases

### Phase 1: Foundation Setup (Week 1) ✅ COMPLETE
- [x] Initialize Django project with DRF
- [x] Create React app with Tailwind CSS
- [x] Implement file upload endpoint
- [x] Build file upload UI with drag-and-drop
- [x] Test full file transfer flow frontend-to-backend
- [x] Add validation and error handling

### Phase 2: Audio Processing Backend (Week 2)
- [ ] Install and configure Spleeter
- [ ] Implement audio trimming
- [ ] Create stem separation service
- [ ] Test with sample audio files

### Phase 3: Waveform & Selection UI (Week 3)
- [ ] Integrate wavesurfer.js
- [ ] Add time range selection
- [ ] Create instrument selector
- [ ] Connect UI to API

### Phase 4: Drum Detection & MIDI (Week 4-5)
- [ ] Implement onset detection
- [ ] Add drum classification logic
- [ ] Convert to MIDI format
- [ ] Fine-tune accuracy

### Phase 5: Visualization (Week 6)
- [ ] Build piano roll component
- [ ] Add playback sync
- [ ] Polish UI/UX

### Phase 6: Testing & Polish (Week 7)
- [ ] Test with various songs
- [ ] Bug fixes and optimization
- [ ] Error handling

### Phase 7: MVP Launch (Week 8)
- [ ] Deploy to production
- [ ] Gather user feedback
- [ ] Plan next features

---

## 🔮 Future Features (Post-MVP)

### Phase 8: Bass Analysis
- Detect bass guitar and synth bass patterns
- Show pitch information alongside timing

### Phase 9: Melodic Instruments
- Guitar, piano, synth lead detection
- Chord progression analysis

### Phase 10: MIDI Export
- Download actual MIDI files
- DAW-specific formatting (FL Studio, Logic, Ableton)

### Phase 11: Premium Features
- Full stem downloads
- Genre-specific pattern library
- Collaboration features
- Pattern comparison across songs

---

## 🛠️ Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use type hints
- **JavaScript/React**: ESLint + Prettier, functional components only
- **Naming**: Clear, descriptive variable names

### Testing Strategy
- Unit tests for audio processing functions
- Integration tests for API endpoints
- Manual testing with diverse music genres

### Performance Considerations
- Process audio asynchronously (Celery for production)
- Cache processed results to avoid re-processing
- Optimize onset detection parameters for speed vs accuracy
- Limit snippet length to 30 seconds max

### Security
- Validate file types and sizes
- Sanitize user inputs
- Rate limit API endpoints
- Auto-delete uploaded files after 1 hour

---

## 📚 Key Learning Resources

- **Spleeter Documentation**: https://github.com/deezer/spleeter
- **librosa Documentation**: https://librosa.org/doc/latest/index.html
- **Music Information Retrieval**: https://musicinformationretrieval.com/
- **MIDI Standard**: https://www.midi.org/specifications

---

## 🐛 Known Issues / Limitations

### Current (MVP)
- Drum classification accuracy varies by genre (electronic drums work better than acoustic)
- Processing time: ~10-30 seconds per snippet
- Only supports drums (no melodic instruments yet)
- No user accounts or saving functionality

### Technical Debt
- Synchronous processing (should be async with Celery)
- Local file storage (should use cloud storage)
- No caching layer yet
- Limited error handling

---

## 💡 Key Design Decisions

### Why 15-30 Second Snippets?
- Reduces processing time significantly
- Users typically want to learn specific sections, not entire songs
- Keeps scope manageable for MVP
- Easier to visualize in a single view

### Why Drums First?
- Drums are easier to detect than melodic instruments
- Most producers start with drum patterns when making beats
- Clear, distinct hits are easier to classify
- Validates the core concept before expanding

### Why Visual MIDI Before Export?
- Faster to implement for MVP
- Tests if the core value proposition works
- Users can manually input patterns if they want
- MIDI export adds complexity (file formats, DAW compatibility)

---

## 📧 Contact

Project Creator: Jesse Hernandez 
Questions/Feedback: jessemhernandez123@gmail.com

---

**Last Updated**: October 13, 2025  
**Version**: 0.1.0 (MVP Development)