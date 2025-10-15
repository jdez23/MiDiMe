# MiDiMe Backend - Django REST API

This is the Django backend for the Music Pattern Analyzer (MiDiMe) project. It handles audio processing, pattern extraction, duplicate detection, and pattern similarity search.

## Setup Instructions

### 1. Install System Dependencies

**macOS:**
```bash
# Install FFmpeg (required for audio processing)
brew install ffmpeg

# Install Chromaprint (for audio fingerprinting)
brew install chromaprint

# Install PostgreSQL
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y ffmpeg libchromaprint-tools postgresql redis-server
sudo systemctl start postgresql
sudo systemctl start redis
```

**Windows:**
- Download FFmpeg from https://ffmpeg.org/download.html
- Download Chromaprint from https://acoustid.org/chromaprint
- Install PostgreSQL from https://www.postgresql.org/download/windows/
- Install Redis from https://github.com/microsoftarchive/redis/releases

### 2. Install Python Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

**Key Dependencies:**
- Django 4.2.7 - Web framework
- Django REST Framework 3.14.0 - API toolkit
- Spleeter - Stem separation (Phase 2)
- librosa - Audio analysis
- pyacoustid/chromaprint - Audio fingerprinting
- NumPy/SciPy - Pattern fingerprinting
- Celery - Async task processing
- psycopg2 - PostgreSQL adapter
- redis - Cache and task queue

### 3. Configure Environment Variables

Create a `.env` file in the backend directory:

```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/midime
POSTGRES_USER=midime_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=midime

# Redis
REDIS_URL=redis://localhost:6379/0

# Django
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Audio Processing
SPLEETER_MODEL_PATH=./models/spleeter
TEMP_AUDIO_PATH=./storage/temp
MAX_UPLOAD_SIZE_MB=50

# Pattern Database Settings
ENABLE_DUPLICATE_DETECTION=True
MAX_SECTIONS_PER_SONG=5
SIMILARITY_THRESHOLD=0.7

# Optional: Vector Database (for scaling)
# FAISS_INDEX_PATH=./storage/faiss_indexes
# PINECONE_API_KEY=your-key-here
# PINECONE_ENVIRONMENT=us-west1-gcp

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
```

### 4. Set Up Database

```bash
# Create PostgreSQL database
createdb midime

# Or using psql
psql -U postgres
CREATE DATABASE midime;
CREATE USER midime_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE midime TO midime_user;
\q

# Run migrations
python manage.py migrate
```

### 5. Download Spleeter Models (Phase 2)

```bash
# Download pre-trained models
python -c "from spleeter.separator import Separator; Separator('spleeter:4stems')"
```

This will download models to `~/.cache/spleeter/` (about 200MB)

### 6. Start the Development Server

```bash
# Terminal 1: Django server
python manage.py runserver

# Terminal 2: Celery worker (for async processing)
celery -A config worker -l info

# Terminal 3: Celery beat (for scheduled tasks, optional)
celery -A config beat -l info
```

The server will run at `http://localhost:8000`

## API Endpoints

### Phase 1 - Core Upload ✅

#### Health Check
- **GET** `/api/health`
- Returns server status

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-14T10:30:00Z",
  "database": "connected",
  "redis": "connected"
}
```

#### Upload Audio File
- **POST** `/api/upload`
- Accepts audio file uploads (MP3, WAV, FLAC, M4A, OGG)
- Max file size: 50MB

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/upload \
  -F "audio_file=@path/to/song.mp3"
```

**Example Response:**
```json
{
  "status": "success",
  "message": "File uploaded successfully",
  "data": {
    "filename": "song.mp3",
    "file_size": "5.23 MB",
    "file_size_bytes": 5485760,
    "file_hash": "a1b2c3d4e5f6..."
  }
}
```

### Phase 2-6 - Analysis & Pattern Storage

#### Analyze Audio
- **POST** `/api/analyze`
- Analyzes audio snippet and returns pattern data
- Includes duplicate detection

**Request:**
```json
{
  "audio_file": "<file>",
  "start_time": 30.5,
  "end_time": 45.5,
  "instrument": "drums",
  "user_id": "uuid",
  "user_tier": "free"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "data": {
    "song_id": "uuid",
    "source_song_id": "uuid",
    "section": "chorus",
    "duplicate_detected": false,
    "duration": 15.0,
    "midi_data": {
      "kick": [0.0, 2.0, 4.0, 6.0, 8.0],
      "snare": [1.0, 3.0, 5.0, 7.0, 9.0],
      "hihat": [0.5, 1.0, 1.5, 2.0, 2.5, ...]
    },
    "tempo": 120,
    "time_signature": "4/4",
    "detected_key": "C minor"
  }
}
```

**Response (Duplicate Detected - Free Tier):**
```json
{
  "status": "error",
  "message": "You already analyzed a section from this song. Try a different song!",
  "data": {
    "duplicate_detected": true,
    "source_song_id": "uuid",
    "existing_sections": ["chorus"],
    "suggestions": [
      {"title": "Similar Song 1", "artist": "Artist A"},
      {"title": "Similar Song 2", "artist": "Artist B"}
    ]
  }
}
```

### Phase 7-9 - Pattern Discovery

#### Search Similar Patterns
- **POST** `/api/search/similar`
- Find patterns similar to a given pattern
- Requires paid tier for full access

**Request:**
```json
{
  "song_id": "uuid",
  "instrument": "drums",
  "min_similarity": 0.7,
  "limit": 20,
  "filters": {
    "tempo_range": [80, 140],
    "genre": ["hip-hop", "trap"],
    "key": ["C minor", "D minor"]
  }
}
```

**Response:**
```json
{
  "status": "success",
  "total_matches": 47,
  "query_info": {
    "song_id": "uuid",
    "instrument": "drums",
    "tempo": 128,
    "key": "C minor"
  },
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
          "midi_available": true,
          "upload_date": "2025-10-10"
        },
        {
          "song_id": "uuid2",
          "section": "verse",
          "similarity_score": 0.89,
          "tempo": 130,
          "key": "C minor",
          "genre": "hip-hop",
          "preview_url": "/api/preview/uuid2",
          "midi_available": true,
          "upload_date": "2025-10-12"
        }
      ]
    }
  ]
}
```

#### Get Pattern Preview
- **GET** `/api/preview/{pattern_id}`
- Returns audio preview of a pattern (15 seconds max)
- Available to all tiers

#### Download Pattern MIDI
- **GET** `/api/download/midi/{pattern_id}`
- Download MIDI file for a pattern
- Requires Producer tier or higher

## Project Structure

```
backend/
├── config/                    # Django project settings
│   ├── settings.py            # Main configuration
│   ├── urls.py                # Root URL routing
│   ├── celery.py              # Celery configuration
│   └── wsgi.py
├── api/                       # REST API app
│   ├── views.py               # API endpoints
│   ├── serializers.py         # Data validation
│   ├── permissions.py         # Tier-based access control (NEW)
│   └── urls.py                # API routes
├── audio_processing/          # Audio analysis logic
│   ├── stem_separator.py      # Spleeter integration
│   ├── onset_detector.py      # librosa onset detection
│   ├── midi_converter.py      # Convert onsets to MIDI
│   ├── drum_classifier.py     # Classify kick/snare/hihat
│   ├── fingerprinting.py      # Pattern fingerprinting (NEW)
│   ├── duplicate_detection.py # Audio fingerprint matching (NEW)
│   └── utils.py               # Helper functions
├── similarity/                # Pattern similarity (NEW - Phase 7)
│   ├── search.py              # Pattern similarity search
│   ├── vector_index.py        # FAISS/vector database
│   └── ranking.py             # Result ranking algorithms
├── models.py                  # Database models
├── tasks.py                   # Celery async tasks
├── storage/                   # File storage
│   ├── uploads/               # Temporary uploaded files
│   ├── processed/             # Processed audio (temporary)
│   ├── test_samples/          # Test audio files
│   └── faiss_indexes/         # Vector indexes (Phase 7+)
├── tests/                     # Unit and integration tests
│   ├── test_audio_processing.py
│   ├── test_fingerprinting.py
│   ├── test_duplicate_detection.py
│   └── test_similarity_search.py
├── manage.py                  # Django management script
└── requirements.txt           # Python dependencies
```

## Database Schema

### Current Tables

**songs** (Phase 3+)
```sql
CREATE TABLE songs (
    song_id VARCHAR(36) PRIMARY KEY,
    source_song_id VARCHAR(36),      -- Groups sections from same song
    audio_fingerprint TEXT,          -- Chromaprint fingerprint
    section_label VARCHAR(20),       -- intro/verse/chorus/bridge
    user_id VARCHAR(36),
    upload_date TIMESTAMP,
    duration INTEGER,
    tempo FLOAT,
    detected_key VARCHAR(10),
    detected_genre VARCHAR(50),
    file_hash VARCHAR(64),
    privacy_setting VARCHAR(10),
    INDEX(user_id),
    INDEX(source_song_id),
    INDEX(audio_fingerprint)
);
```

**patterns** (Phase 3+)
```sql
CREATE TABLE patterns (
    pattern_id VARCHAR(36) PRIMARY KEY,
    song_id VARCHAR(36),
    instrument_type VARCHAR(20),
    midi_data JSON,
    tempo FLOAT,
    key_signature VARCHAR(10),
    fingerprint BLOB,                -- 60-100 dimensional vector
    quality_score FLOAT,
    created_at TIMESTAMP,
    FOREIGN KEY (song_id) REFERENCES songs(song_id)
);
```

**pattern_similarities** (Phase 7+ - Optional)
```sql
CREATE TABLE pattern_similarities (
    similarity_id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pattern_id_1 VARCHAR(36),
    pattern_id_2 VARCHAR(36),
    similarity_score FLOAT,
    instrument_type VARCHAR(20),
    computed_at TIMESTAMP
);
```

## Testing

### Run Unit Tests
```bash
# All tests
python manage.py test

# Specific module
python manage.py test api.tests.test_upload

# With coverage
coverage run --source='.' manage.py test
coverage report
```

### Test Audio Processing
```bash
# Test with sample files
python manage.py test audio_processing.tests

# Manual testing
python manage.py shell
>>> from audio_processing.stem_separator import separate_stems
>>> result = separate_stems('storage/test_samples/song.mp3')
>>> print(result)
```

### Test Pattern Fingerprinting
```bash
python manage.py test audio_processing.tests.test_fingerprinting

# Should verify:
# - Consistency (same audio = same fingerprint)
# - Similarity (similar patterns = high similarity score)
# - Distinctiveness (different patterns = low similarity)
```

### Test Duplicate Detection
```bash
python manage.py test audio_processing.tests.test_duplicate_detection

# Should verify:
# - Same song detection across different sections
# - Different songs correctly identified as unique
# - Edge cases (remixes, covers, etc.)
```

## Development Workflow

### Current Phase: Phase 2 - Audio Processing Backend

**Tasks:**
1. Install and configure Spleeter ✓
2. Implement audio trimming
3. Create stem separation service
4. Add Chromaprint for audio fingerprinting
5. Implement duplicate detection logic
6. Set up Celery for async processing
7. Test with diverse audio samples

**Testing Checklist:**
- [ ] Spleeter successfully separates stems
- [ ] Audio fingerprinting detects duplicates (>85% accuracy)
- [ ] Duplicate detection workflow works end-to-end
- [ ] Processing completes in < 30 seconds
- [ ] Celery tasks execute properly
- [ ] Temporary files are cleaned up

### Phase 3: Database & Pattern Storage (Next)
- Implement database models
- Create pattern fingerprinting algorithm
- Build duplicate detection workflow
- Add tier-based access control

### Phase 7: Pattern Similarity Search (Future)
- Implement similarity search algorithm
- Build FAISS index for scaling
- Add filtering and ranking

## Performance Optimization

### Audio Processing
- Use Celery for async processing (all clips > 15 seconds)
- Cache Spleeter models in memory
- Process at 22.05kHz sample rate for speed (vs 44.1kHz)
- Delete temporary files immediately after processing

### Pattern Similarity Search
- **< 10K patterns**: PostgreSQL with real-time cosine similarity
- **10K-100K patterns**: Pre-computed similarities (Celery background jobs)
- **> 100K patterns**: FAISS approximate nearest neighbor

### Database Optimization
- Index all foreign keys
- Use connection pooling (pgbouncer)
- Regular VACUUM for PostgreSQL
- Monitor query performance with django-debug-toolbar

## Common Issues & Solutions

### Spleeter Installation Issues
```bash
# If TensorFlow errors occur
pip install --upgrade tensorflow==2.8.0

# If CUDA errors (GPU version)
# Use CPU version instead
pip uninstall spleeter
pip install spleeter --no-dependencies
pip install tensorflow==2.8.0
```

### Chromaprint Not Found
```bash
# macOS
brew install chromaprint
export DYLD_LIBRARY_PATH=$(brew --prefix chromaprint)/lib

# Linux
sudo apt-get install libchromaprint-tools
```

### Celery Connection Issues
```bash
# Check Redis is running
redis-cli ping
# Should return: PONG

# Restart Celery worker
celery -A config worker --purge -l info
```

### Database Migration Issues
```bash
# Reset migrations (development only!)
python manage.py migrate api zero
rm api/migrations/00*.py
python manage.py makemigrations
python manage.py migrate
```

## Security Considerations

- Audio files are deleted immediately after pattern extraction
- File uploads validated for type, size, and content
- Rate limiting enforced per tier
- CORS configured for specific origins only
- SQL injection protection via Django ORM
- Secrets stored in environment variables (never in code)

## Monitoring & Logging

### Log Locations
- Django logs: `logs/django.log`
- Celery logs: `logs/celery.log`
- Error logs: `logs/errors.log`

### Key Metrics to Monitor
- Upload success rate
- Processing time per clip
- Pattern extraction quality scores
- Duplicate detection accuracy
- Similarity search query time
- Celery task queue length
- Database query performance

## API Rate Limits

| Tier | Requests/Hour | Analyses/Month | Uploads/Day |
|------|---------------|----------------|-------------|
| Free | 10 | 3 | 3 |
| Starter | 50 | 25 | 10 |
| Producer | 100 | Unlimited | 50 |
| Studio | 200 | Unlimited | 100 |

## Contributing

See main project README.md for development guidelines.

## Support

For questions or issues:
- Check the main README.md
- Review the .clinerules file for coding guidelines
- Contact: jessemhernandez123@gmail.com

---

**Last Updated**: October 14, 2025  
**Version**: 0.2.0 (Phase 2 - Audio Processing Backend)