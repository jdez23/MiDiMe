# MiDiMe Frontend - React Application

This is the React frontend for the Music Pattern Analyzer (MiDiMe) project.

## Features

- **File Upload**: Drag-and-drop or click to upload audio files
- **File Validation**: Automatically validates file format and size
- **Progress Tracking**: Real-time upload progress indicator
- **Responsive UI**: Beautiful Tailwind CSS styling
- **Error Handling**: Clear error messages for failed uploads

## Tech Stack

- **React 19.2.0** - UI library
- **Axios** - HTTP client for API calls
- **Tailwind CSS 3.3.0** - Utility-first CSS framework
- **Create React App** - Build tooling

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm start
```

The app will run at `http://localhost:3000`

### 3. Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/                   # Static files
├── src/
│   ├── components/           # React components
│   │   ├── FileUpload.jsx    # Main file upload component
│   │   └── LoadingSpinner.jsx # Loading indicator
│   ├── services/
│   │   └── api.js            # API service for backend calls
│   ├── App.js                # Main app component
│   ├── index.js              # Entry point
│   └── index.css             # Global styles with Tailwind
├── package.json
└── tailwind.config.js        # Tailwind configuration
```

## Components

### FileUpload
Main component for uploading audio files to the Django backend.

**Features:**
- Drag-and-drop file upload
- Click to browse files
- File type validation (MP3, WAV, FLAC, M4A, OGG)
- File size validation (max 50MB)
- Upload progress bar
- Success/error messaging

### LoadingSpinner
Reusable loading indicator component with customizable message.

## API Service

The `api.js` service provides methods to communicate with the Django backend:

- `uploadAudioFile(file, onUploadProgress)` - Upload audio file
- `checkHealth()` - Check backend health status

API base URL defaults to `http://localhost:8000` and can be configured via the `REACT_APP_API_URL` environment variable.

## Environment Variables

Create a `.env` file in the frontend directory to customize settings:

```
REACT_APP_API_URL=http://localhost:8000
```

## Available Scripts

- `npm start` - Run development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run eject` - Eject from Create React App

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- M4A (.m4a)
- OGG (.ogg)

Maximum file size: 50MB

## Development Notes

- The frontend connects to the Django backend running on port 8000
- CORS is configured in the Django backend to allow requests from localhost:3000
- File validation happens both on the frontend (UI) and backend (security)

## Next Steps (Phase 2)

- Add waveform visualization with wavesurfer.js
- Implement time range selection for snippets
- Add instrument selector (drums, bass, etc.)
- Display processing status and results
- Show piano roll visualization

## Troubleshooting

### Backend Connection Issues

Make sure the Django backend is running:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### Port Already in Use

If port 3000 is already in use, you can specify a different port:
```bash
PORT=3001 npm start
```

## License

TBD - Will be determined before public launch
