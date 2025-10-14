# MiDiMe Backend - Django REST API

This is the Django backend for the Music Pattern Analyzer (MiDiMe) project.

## Setup Instructions

### 1. Install Dependencies

```bash
cd backend
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Run Migrations

```bash
python manage.py migrate
```

### 3. Start the Development Server

```bash
python manage.py runserver
```

The server will run at `http://localhost:8000`

## API Endpoints

### Health Check
- **GET** `/api/health`
- Returns server status

**Example Response:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-13T10:30:00Z"
}
```

### Upload Audio File
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
    "file_size_bytes": 5485760
  }
}
```

**Error Response (Invalid File):**
```json
{
  "status": "error",
  "message": "Invalid file",
  "errors": {
    "audio_file": ["Unsupported file format. Allowed formats: .mp3, .wav, .flac, .m4a, .ogg"]
  }
}
```

## Project Structure

```
backend/
├── config/              # Django project settings
│   ├── settings.py      # Main configuration
│   ├── urls.py          # Root URL routing
│   └── wsgi.py
├── api/                 # REST API app
│   ├── views.py         # API endpoints
│   ├── serializers.py   # Data validation
│   └── urls.py          # API routes
├── storage/             # File storage
│   ├── uploads/         # Uploaded audio files
│   ├── processed/       # Processed audio (future)
│   └── test_samples/    # Test audio files
├── manage.py            # Django management script
└── requirements.txt     # Python dependencies
```

## Technology Stack

- **Django 4.2.7** - Web framework
- **Django REST Framework 3.14.0** - API toolkit
- **django-cors-headers** - CORS support for React frontend

## Development Notes

- Uploaded files are stored in `storage/uploads/`
- Files are automatically validated for size and format
- CORS is configured for `localhost:3000` (React default port)

## Next Steps (Phase 2)

- Add audio processing with librosa
- Integrate Spleeter for stem separation
- Implement onset detection for drum patterns
- Create MIDI conversion functionality
