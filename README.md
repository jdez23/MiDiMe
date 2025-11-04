# Music Pattern Analyzer (MiDiMe)

## 🎵 Project Overview

**MiDiMe (Music Pattern Analyzer)** is a web application designed to help music producers deconstruct, understand, and discover musical patterns. By uploading audio clips and analyzing specific sections, users can visualize drum patterns, chord progressions, and melodic structures - then discover similar patterns across thousands of other songs in our community database.

### The Problem We're Solving
Producers often hear amazing patterns in songs but struggle to identify exactly when each element hits. Traditional transcription is time-consuming and requires advanced ear training. This tool uses AI-powered audio analysis to automatically detect and visualize these patterns - and helps you discover similar patterns across other songs.

### Core Value Proposition
- **Visual Learning**: See exactly where snares, kicks, and hi-hats hit in a piano roll format
- **Pattern Discovery**: Find similar drum grooves, chord progressions, and melodies across our database
- **Quick Analysis**: Analyze 15-90 second snippets instead of entire songs
- **DAW-Ready**: Export MIDI patterns directly into Logic, FL Studio, or Ableton
- **Network Effects**: Every upload makes pattern discovery smarter for everyone

### The Big Picture
We're not just analyzing songs - we're building the world's largest musical pattern graph. Every upload contributes to a database that helps producers discover hidden musical connections.

---

## 🎯 Current Status

**Phase**: MVP Development - Drum Pattern Analysis + Database Foundation
**Target Launch**: 12 weeks from project start
**Current Focus**: Phase 5 - Drum Detection & MIDI

### Recent Progress (November 3, 2025)

✅ **Phase 1 COMPLETE - Full Stack File Upload Working!**
- Django 4.2.7 with Django REST Framework
- React 19.2.0 with Tailwind CSS 3.3.0
- File upload endpoint with drag-and-drop UI
- Full validation and error handling

✅ **Phase 2 PARTIAL - Audio Processing Backend**
- ✅ Spleeter 2.4.2 installed (4-stem separation: drums/bass/vocals/other)
- ✅ FFmpeg 8.0 for audio codec support
- ✅ Audio trimming with pydub (15-90 second validation)
- ✅ Integrated audio service (trim → separate → process)
- ⏳ Chromaprint fingerprinting (pending)
- ⏳ Celery async processing (pending)

✅ **Phase 5 PARTIAL - Drum Detection & MIDI**
- ✅ Onset detection with librosa 0.11.0
- ✅ Frequency-based drum classification (kick/snare/hihat)
- ✅ MIDI conversion with MIDIUtil 1.2.1
- ✅ Fixed onset detection parameters:
  - Changed `backtrack=False` for better kick detection
  - Changed `filter_weak=False` to capture all hits
  - Lowered `min_strength=0.1` for better sensitivity
- ✅ Test results: 18 kicks, 4 snares, 15 hi-hats per 15s @ 167 BPM
- ⚠️ MIDI timing alignment verification in progress

📋 **Next Up:**
- Verify MIDI timing alignment with audio
- Create integrated `/api/analyze` endpoint
- Implement database schema (songs, patterns tables)
- Add pattern fingerprinting for similarity search

---

## 🏗️ Architecture

### High-Level Flow
```
User uploads audio (15-90s snippet) 
    ↓
Audio fingerprinting (detect duplicates)
    ↓
Stem separation (Spleeter: drums, bass, vocals, other)
    ↓
Pattern extraction (drums, bass, chords, melody)
    ↓
Pattern fingerprinting (create mathematical vectors)
    ↓
Database storage (patterns + fingerprints)
    ↓
Visual piano roll display
    ↓
Similarity search (find similar patterns across database)
```

### Tech Stack

#### Backend
- **Framework**: Django 4.x with Django REST Framework
- **Audio Separation**: Spleeter (Facebook's pre-trained model)
- **Audio Analysis**: librosa for onset detection and audio manipulation
- **Audio Fingerprinting**: Chromaprint/AcoustID for duplicate detection
- **Audio Utilities**: pydub for trimming and format conversion
- **Task Queue**: Celery for async processing
- **Database**: PostgreSQL for structured data + pattern storage
- **Vector Search**: FAISS (or Pinecone) for similarity search at scale
- **Caching**: Redis for performance
- **Storage**: Temporary local storage (audio files deleted after processing)

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
│   │   ├── permissions.py          # NEW: Tier-based access control
│   │   └── tests.py
│   ├── audio_processing/            # Audio analysis logic
│   │   ├── stem_separator.py       # Spleeter integration
│   │   ├── onset_detector.py       # librosa onset detection
│   │   ├── midi_converter.py       # Convert onsets to MIDI
│   │   ├── drum_classifier.py      # Classify kick/snare/hihat
│   │   ├── fingerprinting.py       # NEW: Create pattern vectors
│   │   ├── duplicate_detection.py  # NEW: Audio fingerprint matching
│   │   └── utils.py
│   ├── similarity/                  # NEW: Pattern similarity
│   │   ├── search.py               # Pattern similarity search
│   │   ├── vector_index.py         # FAISS/vector database
│   │   └── ranking.py              # Result ranking algorithms
│   ├── models.py                    # Database models
│   ├── tasks.py                     # Celery async tasks
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
│   │   │   ├── SimilaritySearch.jsx    # NEW: Search similar patterns
│   │   │   ├── ResultsGrid.jsx         # NEW: Display search results
│   │   │   └── LoadingSpinner.jsx
│   │   ├── services/
│   │   │   └── api.js                  # API calls to backend
│   │   ├── utils/
│   │   ├── App.jsx
│   │   └── index.js
│   ├── package.json
│   └── tailwind.config.js
│
├── docs/                            # Documentation
│   ├── API.md                       # API endpoint documentation
│   ├── ARCHITECTURE.md              # System architecture details
│   ├── PATTERN_FINGERPRINTING.md   # NEW: Algorithm details
│   └── ROADMAP.md                   # Development roadmap
│
├── .clinerules                      # Claude Code guidelines
├── README.md                        # This file
└── .gitignore
```

---

## 🗄️ Database Schema

### Core Tables

**songs**
```sql
CREATE TABLE songs (
    song_id VARCHAR(36) PRIMARY KEY,
    source_song_id VARCHAR(36),      -- NEW: Groups sections from same song
    audio_fingerprint TEXT,          -- NEW: For duplicate detection
    section_label VARCHAR(20),       -- NEW: intro/verse/chorus/bridge
    user_id VARCHAR(36),
    upload_date TIMESTAMP,
    duration INTEGER,                -- in seconds
    tempo FLOAT,
    detected_key VARCHAR(10),
    detected_genre VARCHAR(50),
    file_hash VARCHAR(64),
    privacy_setting VARCHAR(10),     -- NEW: public/private
    INDEX(user_id),
    INDEX(source_song_id),
    INDEX(audio_fingerprint)
);
```

**patterns** (NEW)
```sql
CREATE TABLE patterns (
    pattern_id VARCHAR(36) PRIMARY KEY,
    song_id VARCHAR(36),
    instrument_type VARCHAR(20),     -- drums/bass/chords/melody
    midi_data JSON,                  -- Actual note/hit data
    tempo FLOAT,
    key_signature VARCHAR(10),
    fingerprint BLOB,                -- Vector representation (60-100 dims)
    quality_score FLOAT,             -- Pattern extraction confidence
    created_at TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(song_id),
    INDEX(song_id),
    INDEX(instrument_type)
);
```

**pattern_similarities** (NEW - optional, pre-computed)
```sql
CREATE TABLE pattern_similarities (
    similarity_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pattern_id_1 VARCHAR(36),
    pattern_id_2 VARCHAR(36),
    similarity_score FLOAT,          -- 0.0 to 1.0
    instrument_type VARCHAR(20),
    computed_at TIMESTAMP,
    INDEX(pattern_id_1),
    INDEX(similarity_score DESC)
);
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
  "song_id": "uuid",
  "source_song_id": "uuid",
  "section": "chorus",
  "duration": 15.0,
  "midi_data": {
    "kick": [0.0, 2.0, 4.0, 6.0, 8.0],
    "snare": [1.0, 3.0, 5.0, 7.0, 9.0],
    "hihat": [0.5, 1.0, 1.5, 2.0, 2.5, 3.0, ...]
  },
  "tempo": 120,
  "time_signature": "4/4",
  "duplicate_detected": false
}
```

#### POST `/api/search/similar` (NEW)
Search for similar patterns in the database.

**Request**:
```json
{
  "song_id": "uuid",
  "instrument": "drums",
  "min_similarity": 0.7,
  "limit": 20,
  "filters": {
    "tempo_range": [80, 140],
    "genre": ["hip-hop", "trap"]
  }
}
```

**Response**:
```json
{
  "total_matches": 47,
  "results": [
    {
      "source_song_id": "uuid",
      "sections": [
        {
          "song_id": "uuid",
          "section": "chorus",
          "similarity_score": 0.94,
          "tempo": 128,
          "key": "C minor",
          "genre": "trap",
          "preview_url": "/api/preview/uuid",
          "midi_available": true
        }
      ]
    }
  ]
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

### Basic Analysis Flow
1. **Upload**: User uploads an audio file (MP3, WAV, etc.)
2. **Visualize**: Waveform displays the full song
3. **Select**: User drags to select a 15-90 second snippet
4. **Choose**: User selects which instrument to analyze (drums for MVP)
5. **Analyze**: Click "Analyze" button, loading indicator appears
6. **View**: Piano roll visualization shows the pattern with time-aligned hits
7. **Learn**: User can now recreate the pattern in their DAW

### Pattern Discovery Flow (NEW)
1. **Analyze**: User completes basic analysis of their chosen snippet
2. **Discover**: Click "Find Similar Patterns" button
3. **Filter**: Select instrument type (drums, bass, chords)
4. **Browse**: View grid of similar patterns with similarity scores
5. **Preview**: Listen to audio previews of similar patterns
6. **Download**: Export MIDI of similar patterns (paid tiers only)

---

## 🧪 Data Flow Details

### Audio Processing Pipeline

1. **Upload & Validation**
   - Validate file format (MP3, WAV, FLAC)
   - Check file size (limit: 50MB for MVP)
   - Save to temporary storage

2. **Duplicate Detection (NEW)**
   - Generate audio fingerprint using Chromaprint
   - Check if source song already exists in database
   - If free tier user already analyzed this song: reject with message
   - If paid tier or first time: proceed with analysis

3. **Snippet Extraction**
   - Use librosa or pydub to extract the user-selected time range
   - Convert to standard format (44.1kHz, stereo)

4. **Stem Separation (Spleeter)**
   - Input: trimmed audio file
   - Process: Spleeter 4-stem model (drums, bass, vocals, other)
   - Output: isolated tracks as WAV files

5. **Onset Detection & Classification (librosa)**
   - Input: isolated drum track
   - Process: `librosa.onset.onset_detect()` with optimized parameters
   - Output: array of timestamps where drum hits occur
   - Classify by frequency: Low=Kick, Mid=Snare, High=Hi-hat

6. **Pattern Fingerprinting (NEW)**
   - Create 60-dimensional vector for drum patterns:
     - Rhythmic density per component (kick, snare, hi-hat) [4 dims]
     - Syncopation measure [1 dim]
     - Binary groove grid for 16 steps × 3 components [48 dims]
     - Tempo, velocity variance, groove features [7 dims]
   - Store fingerprint in database for similarity search

7. **MIDI Formatting**
   - Convert timestamps to MIDI note numbers
   - Standard mapping: Kick=36, Snare=38, Hi-hat=42
   - Create JSON structure for frontend rendering

8. **Database Storage (NEW)**
   - Save song metadata with source_song_id grouping
   - Save patterns with fingerprints
   - Link to user account and tier
   - Set privacy based on user tier

9. **Response**
   - Return MIDI data and visualizations to frontend
   - Clean up temporary audio files
   - Trigger background job to compute similarities (optional)

---

## 💰 Monetization Model

### Tier Structure

| Feature | Free | Starter ($4.99) | Producer ($9.99) | Studio ($24.99) |
|---------|------|-----------------|------------------|-----------------|
| Clip length | 15s | 30s | 90s | 5min |
| Analyses/month | 3 | 25 | Unlimited | Unlimited |
| Sections per song | 1 | 1 | Unlimited | Unlimited |
| PDF export | ✓ (watermark) | ✓ | ✓ | ✓ |
| Visualizations | Drums only | All | All | All |
| MIDI export | ✗ | Drums only | All | All |
| Similarity search | Preview only | 10 results | Unlimited | Unlimited |
| Download similar MIDI | ✗ | ✗ | ✓ | ✓ |
| Stem separation | ✗ | ✗ | ✗ | ✓ |
| Privacy settings | Public only | Public only | Private option | Private option |
| Saved analyses | 0 | 10 | Unlimited | Unlimited |

### The Freemium Strategy

**Free Tier:**
- 15 seconds is enough to capture complete musical loops (4-8 bars)
- 1 section per source song prevents duplicate spam
- Patterns are public by default (builds database)
- Clear upgrade path when users hit limits

**Paid Tiers:**
- Longer clips for full analysis
- Multiple sections per song allowed
- Private patterns option
- Full MIDI export and similarity search

---

## 🚀 Development Phases

### Phase 1: Foundation Setup (Week 1) ✅ COMPLETE
- [x] Initialize Django project with DRF
- [x] Create React app with Tailwind CSS
- [x] Implement file upload endpoint
- [x] Build file upload UI with drag-and-drop
- [x] Test full file transfer flow frontend-to-backend
- [x] Add validation and error handling

### Phase 2: Audio Processing Backend (Week 2-3) ⚠️ PARTIAL
- [x] Install and configure Spleeter
- [x] Implement audio trimming with pydub
- [x] Create stem separation service
- [x] Test with sample audio files
- [ ] Add Chromaprint for audio fingerprinting
- [ ] Implement duplicate detection logic
- [ ] Set up Celery for async processing

### Phase 3: Database & Pattern Storage (Week 3-4)
- [ ] Implement songs table with source_song_id
- [ ] Implement patterns table
- [ ] Create pattern fingerprinting algorithm
- [ ] Build duplicate detection workflow
- [ ] Add section detection (intro/verse/chorus/bridge)
- [ ] Implement tier-based access control

### Phase 4: Waveform & Selection UI (Week 4-5)
- [ ] Integrate wavesurfer.js
- [ ] Add time range selection
- [ ] Create instrument selector
- [ ] Connect UI to API
- [ ] Add duplicate detection feedback

### Phase 5: Drum Detection & MIDI (Week 5-6) ⚠️ PARTIAL
- [x] Implement onset detection with librosa
- [x] Add drum classification logic (kick/snare/hihat)
- [x] Convert to MIDI format with MIDIUtil
- [x] Debug and fix onset detection parameters (backtrack, filter_weak)
- [ ] Verify MIDI timing alignment with audio
- [ ] Fine-tune accuracy with diverse samples
- [ ] Create integrated API endpoint
- [ ] Save patterns to database

### Phase 6: Visualization (Week 7)
- [ ] Build piano roll component
- [ ] Add playback sync
- [ ] Polish UI/UX

### Phase 7: Pattern Similarity Search (Week 8-9)
- [ ] Implement similarity search algorithm (cosine distance)
- [ ] Build similarity search UI
- [ ] Add filtering (tempo, genre, key)
- [ ] Group results by source_song_id
- [ ] Implement tier-based result limiting
- [ ] Add audio preview for similar patterns

### Phase 8: Testing & Polish (Week 10-11)
- [ ] Test with various songs and genres
- [ ] Bug fixes and optimization
- [ ] Error handling improvements
- [ ] Performance tuning
- [ ] Database health monitoring

### Phase 9: MVP Launch (Week 12)
- [ ] Deploy backend to production
- [ ] Deploy frontend to production
- [ ] Set up payment processing (Stripe)
- [ ] Gather user feedback
- [ ] Plan next features

---

## 🔮 Future Features (Post-MVP)

### Phase 10: Bass & Chord Analysis
- Detect bass guitar and synth bass patterns
- Chord progression analysis
- Show pitch information alongside timing

### Phase 11: Full Manipulation Suite
- Audio-to-MIDI editing capabilities
- Pattern splicing (combine elements from different songs)
- Tempo/key adjustment
- Compete with Samplab on manipulation side

### Phase 12: Community Features
- Pattern collections (curated by users)
- Pattern marketplace (buy/sell patterns)
- Community tagging and voting
- Genre-specific libraries

### Phase 13: Advanced Features
- Pattern generation (AI suggests variations)
- Batch processing for Studio tier
- API for external integrations
- DAW plugins (FL Studio, Ableton, Logic)

---

## 🛠️ Development Guidelines

### Code Style
- **Python**: Follow PEP 8, use type hints
- **JavaScript/React**: ESLint + Prettier, functional components only
- **Naming**: Clear, descriptive variable names

### Testing Strategy
- Unit tests for audio processing functions
- Integration tests for API endpoints
- Test duplicate detection with known duplicates
- Test pattern fingerprinting consistency
- Manual testing with diverse music genres

### Performance Considerations
- Process audio asynchronously with Celery
- Pre-compute pattern similarities in background
- Use FAISS for similarity search at scale (>100K patterns)
- Cache processed results to avoid re-processing
- Optimize onset detection parameters for speed vs accuracy
- Delete audio files immediately after processing

### Security & Privacy
- Validate file types and sizes
- Sanitize user inputs
- Rate limit API endpoints
- Auto-delete uploaded audio files after processing
- Store only pattern fingerprints, not copyrighted audio
- Implement tier-based access control
- GDPR/CCPA compliant data handling

### Database Health Monitoring
Track these metrics:
- Unique source songs vs total uploads
- Genre distribution (incentivize diversity)
- Duplicate detection accuracy
- Pattern quality scores
- User contribution patterns

---

## 🔑 Key Technical Decisions

### Why 15-Second Free Tier?
- Captures complete musical loops (4-8 bars at typical tempos)
- Reduces processing costs
- Forces pattern diversity (can't spam same song)
- Creates clear upgrade incentive
- Faster processing = better UX for free users

### Why Pattern Fingerprinting?
- Enables similarity search without storing copyrighted audio
- Creates defensible moat (proprietary pattern database)
- Network effects: more uploads = better recommendations
- Legal safe harbor: analyzing patterns, not redistributing audio

### Why Source Song Grouping?
- Prevents database pollution from duplicates
- Improves search quality (same song doesn't dominate results)
- Allows section-specific analysis (chorus vs verse)
- Better user experience in similarity search

### Duplicate Detection Strategy
- **Level 1**: Audio fingerprinting (Chromaprint) - catches same source
- **Level 2**: File hash - catches exact file duplicates  
- **Level 3**: Tempo + key + duration - secondary verification
- Free tier: 1 section per source song per user
- Paid tier: unlimited sections, optional privacy

### Similarity Search Scaling
- **< 10K patterns**: PostgreSQL with real-time cosine similarity
- **10K-100K patterns**: Pre-computed similarities (background jobs)
- **> 100K patterns**: FAISS approximate nearest neighbor search

---

## 📚 Key Learning Resources

- **Spleeter Documentation**: https://github.com/deezer/spleeter
- **librosa Documentation**: https://librosa.org/doc/latest/index.html
- **Chromaprint/AcoustID**: https://acoustid.org/chromaprint
- **FAISS (Facebook AI Similarity Search)**: https://github.com/facebookresearch/faiss
- **Music Information Retrieval**: https://musicinformationretrieval.com/
- **MIDI Standard**: https://www.midi.org/specifications

---

## 🐛 Known Issues / Limitations

### Current (MVP)
- Drum classification accuracy varies by genre (electronic drums work better than acoustic)
- Processing time: ~10-30 seconds per snippet
- Only supports drums (no melodic instruments yet)
- Similarity search limited to database size
- No offline mode (requires internet for processing)

### Technical Debt
- Need to add Celery for async processing
- Need to implement FAISS for large-scale similarity search
- Pre-computed similarities not yet implemented
- Limited error recovery mechanisms
- No comprehensive test coverage yet

---

## 💡 Key Design Decisions

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

### Why Pattern Database?
- Creates network effects (more users = more value)
- Differentiates from Samplab (they're a tool, we're a platform)
- Builds defensible moat (proprietary pattern data)
- Opens multiple revenue streams (subscriptions, data licensing, API)

### Why Middle Ground Freemium?
- Free tier builds database (public patterns by default)
- 1 section per song prevents spam, maintains quality
- Paid tiers unlock privacy + unlimited sections
- Clear upgrade incentive at every tier

---

## 📧 Contact

Project Creator: Jesse Hernandez  
Questions/Feedback: jessemhernandez123@gmail.com

---

**Last Updated**: October 14, 2025  
**Version**: 0.2.0 (MVP Development + Pattern Database)