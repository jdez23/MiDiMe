# MiDiMe Frontend - React Application

This is the React frontend for the Music Pattern Analyzer (MiDiMe) project. It provides an intuitive interface for uploading audio, analyzing patterns, and discovering similar patterns across our community database.

## Features

### Phase 1 - Core Upload ✅
- **File Upload**: Drag-and-drop or click to upload audio files
- **File Validation**: Automatically validates file format and size
- **Progress Tracking**: Real-time upload progress indicator
- **Responsive UI**: Beautiful Tailwind CSS styling
- **Error Handling**: Clear error messages for failed uploads

### Phase 3-6 - Analysis & Visualization (In Progress)
- **Waveform Display**: Interactive audio waveform with wavesurfer.js
- **Time Range Selection**: Visual snippet selection (15-90s based on tier)
- **Instrument Selector**: Choose drums, bass, chords, or melody
- **Piano Roll Visualization**: MIDI pattern display with Canvas
- **Duplicate Detection Feedback**: Clear messaging when song already analyzed
- **Tier-Based Features**: Different capabilities based on subscription level

### Phase 7-9 - Pattern Discovery (Coming Soon)
- **Similarity Search**: Find patterns similar to your analyzed song
- **Filter Results**: By tempo, genre, key, similarity score
- **Audio Preview**: Listen to similar patterns before downloading
- **MIDI Download**: Export patterns to your DAW (paid tiers)
- **Pattern Library**: Browse community-contributed patterns

## Tech Stack

- **React 19.2.0** - UI library with hooks
- **Axios** - HTTP client for API calls
- **Tailwind CSS 3.3.0** - Utility-first CSS framework
- **wavesurfer.js** - Audio waveform visualization
- **Tone.js / HTML5 Canvas** - MIDI pattern visualization
- **React Router** (future) - Navigation for multi-page app
- **Zustand** (future) - State management for complex features

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Configure Environment Variables

Create a `.env` file in the frontend directory:

```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws  # For real-time updates (future)

# Feature Flags (for development)
REACT_APP_ENABLE_SIMILARITY_SEARCH=false  # Enable in Phase 7
REACT_APP_ENABLE_PATTERN_LIBRARY=false    # Enable in Phase 9

# Stripe (for payments - future)
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Analytics (future)
REACT_APP_GOOGLE_ANALYTICS_ID=UA-XXXXX-Y
```

### 3. Start Development Server

```bash
npm start
```

The app will run at `http://localhost:3000`

### 4. Build for Production

```bash
npm run build
```

## Project Structure

```
frontend/
├── public/                        # Static files
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/                # React components
│   │   ├── Upload/
│   │   │   ├── FileUpload.jsx     # Main file upload component
│   │   │   └── DragDropZone.jsx   # Drag-drop UI
│   │   ├── Waveform/
│   │   │   ├── WaveformDisplay.jsx  # Wavesurfer integration
│   │   │   └── TimeSelector.jsx     # Snippet selection
│   │   ├── Analysis/
│   │   │   ├── InstrumentSelector.jsx
│   │   │   ├── PianoRoll.jsx        # MIDI visualization
│   │   │   ├── PatternVisualizer.jsx
│   │   │   └── AnalysisResults.jsx
│   │   ├── Discovery/               # NEW - Phase 7
│   │   │   ├── SimilaritySearch.jsx # Search similar patterns
│   │   │   ├── ResultsGrid.jsx      # Display results
│   │   │   ├── PatternCard.jsx      # Individual pattern card
│   │   │   └── FilterPanel.jsx      # Tempo/genre filters
│   │   ├── Common/
│   │   │   ├── LoadingSpinner.jsx
│   │   │   ├── ErrorMessage.jsx
│   │   │   ├── TierBadge.jsx        # NEW - Display user tier
│   │   │   ├── UpgradePrompt.jsx    # NEW - Paywall UI
│   │   │   └── Button.jsx
│   │   └── Layout/
│   │       ├── Header.jsx
│   │       ├── Footer.jsx
│   │       └── Sidebar.jsx
│   ├── services/
│   │   ├── api.js                   # API service for backend calls
│   │   ├── audio.js                 # Audio processing utilities
│   │   └── auth.js                  # NEW - Authentication (Phase 3)
│   ├── hooks/                       # Custom React hooks
│   │   ├── useAudioUpload.js
│   │   ├── useWaveform.js
│   │   ├── usePatternAnalysis.js
│   │   └── useSimilaritySearch.js   # NEW - Phase 7
│   ├── contexts/                    # React Context providers
│   │   ├── UserContext.js           # NEW - User state & tier
│   │   └── AnalysisContext.js       # Analysis state
│   ├── utils/
│   │   ├── formatters.js            # Format time, file size, etc.
│   │   ├── validators.js            # Client-side validation
│   │   └── constants.js             # App constants
│   ├── styles/
│   │   └── index.css                # Global styles with Tailwind
│   ├── App.js                       # Main app component
│   ├── index.js                     # Entry point
│   └── setupTests.js
├── package.json
├── tailwind.config.js               # Tailwind configuration
└── README.md                        # This file
```

## Key Components

### Phase 1 Components

#### FileUpload
Main component for uploading audio files to the Django backend.

**Props:**
- `onUploadSuccess: (data) => void` - Callback when upload succeeds
- `onUploadError: (error) => void` - Callback when upload fails
- `maxFileSize: number` - Max file size in MB (default: 50)
- `userTier: string` - User subscription tier ('free', 'starter', 'producer', 'studio')

**Features:**
- Drag-and-drop file upload
- Click to browse files
- File type validation (MP3, WAV, FLAC, M4A, OGG)
- File size validation (max 50MB)
- Upload progress bar
- Success/error messaging
- Duplicate detection feedback

#### LoadingSpinner
Reusable loading indicator component with customizable message.

**Props:**
- `message: string` - Loading message to display
- `size: 'sm' | 'md' | 'lg'` - Spinner size

### Phase 3-6 Components

#### WaveformDisplay
Displays audio waveform using wavesurfer.js and allows time range selection.

**Props:**
- `audioUrl: string` - URL of audio file
- `onRegionChange: (start, end) => void` - Callback when selection changes
- `maxDuration: number` - Max selectable duration based on tier (15s, 30s, 90s, etc.)

**Features:**
- Interactive waveform
- Drag to select region
- Zoom controls
- Play/pause functionality
- Visual feedback for selected region

#### InstrumentSelector
Allows user to choose which instrument to analyze.

**Props:**
- `selected: string` - Currently selected instrument
- `onChange: (instrument) => void` - Callback when selection changes
- `availableInstruments: string[]` - Based on user tier

**Options (Phase-dependent):**
- Phase 1-6: drums only
- Phase 10+: drums, bass, chords, melody

#### PianoRoll
Displays MIDI pattern in piano roll format using HTML5 Canvas.

**Props:**
- `midiData: object` - MIDI note data from backend
- `tempo: number` - BPM for timing
- `width: number` - Canvas width
- `height: number` - Canvas height
- `interactive: boolean` - Allow playback control

**Features:**
- Visual representation of notes
- Time grid with bar/beat markers
- Color-coded by instrument type
- Playback cursor
- Export as PNG (future)

### Phase 7-9 Components (Pattern Discovery)

#### SimilaritySearch
Main component for searching similar patterns.

**Props:**
- `songId: string` - ID of analyzed song
- `instrument: string` - Which instrument to search
- `userTier: string` - For access control

**Features:**
- Instrument selector (drums, bass, chords)
- Similarity threshold slider (0.7-1.0)
- Filter panel (tempo, genre, key)
- Loading states
- Empty states with helpful messaging
- Upgrade prompts for free users

**Example Usage:**
```jsx
<SimilaritySearch
  songId={analysisResult.song_id}
  instrument="drums"
  userTier={user.tier}
  onResultsFound={(results) => console.log(results)}
/>
```

#### ResultsGrid
Displays grid of similar patterns with previews.

**Props:**
- `results: array` - Array of similar pattern objects
- `userTier: string` - For feature gating
- `onPatternSelect: (pattern) => void` - Callback when pattern clicked

**Features:**
- Grid layout of pattern cards
- Similarity score badges
- Audio preview buttons
- MIDI download buttons (gated by tier)
- Pagination for large result sets
- Sort options (similarity, tempo, date)

#### PatternCard
Individual pattern card in search results.

**Props:**
- `pattern: object` - Pattern data from API
- `showMidiDownload: boolean` - Based on user tier
- `onPlay: () => void` - Play audio preview
- `onDownload: () => void` - Download MIDI

**Displays:**
- Similarity score (e.g., "94% match")
- Tempo and key
- Genre tag
- Section label (chorus, verse, etc.)
- Upload date
- Lock icon if user can't access

#### FilterPanel
Sidebar filter panel for similarity search.

**Props:**
- `onFilterChange: (filters) => void`
- `availableGenres: string[]`
- `tempoRange: [number, number]`

**Filters:**
- Tempo range slider (80-200 BPM)
- Genre multiselect
- Key signature select
- Sort by: similarity, tempo, date

### Common Components

#### TierBadge (NEW)
Displays user's current subscription tier.

**Props:**
- `tier: string` - 'free', 'starter', 'producer', 'studio'
- `size: 'sm' | 'md' | 'lg'`

**Displays:**
- Colored badge with tier name
- Icon representing tier level
- Hover tooltip with tier benefits

#### UpgradePrompt (NEW)
Modal or inline prompt encouraging upgrade.

**Props:**
- `feature: string` - Feature being gated
- `requiredTier: string` - Minimum tier needed
- `inline: boolean` - Show inline vs modal

**Displays:**
- Clear explanation of feature
- Comparison table of tiers
- CTA button to upgrade
- "Learn More" link

## API Service

The `api.js` service provides methods to communicate with the Django backend:

**Phase 1 Methods:**
```javascript
// Upload & Health
uploadAudioFile(file, onUploadProgress)
checkHealth()
```

**Phase 2-6 Methods:**
```javascript
// Analysis
analyzeAudio(audioFile, startTime, endTime, instrument, userId, userTier)
getAnalysisStatus(taskId)
getAnalysisResult(songId)
downloadMIDI(patternId)
```

**Phase 7-9 Methods:**
```javascript
// Pattern Discovery
searchSimilarPatterns(songId, instrument, filters)
getPatternPreview(patternId)
downloadPatternMIDI(patternId)
getPatternLibrary(filters, page, limit)
```

**Configuration:**
```javascript
// Base URL from environment
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Axios instance with interceptors
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Add auth token if available
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('auth_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## Custom Hooks

### useAudioUpload
Encapsulates upload logic with state management.

```javascript
const {
  upload,
  isUploading,
  uploadProgress,
  error,
  result
} = useAudioUpload();

// Usage
const handleUpload = async (file) => {
  const result = await upload(file);
  console.log('Upload complete:', result);
};
```

### useWaveform
Manages wavesurfer.js instance and interactions.

```javascript
const {
  waveformRef,
  isReady,
  isPlaying,
  currentTime,
  duration,
  play,
  pause,
  seekTo,
  setRegion
} = useWaveform(audioUrl);
```

### useSimilaritySearch (NEW - Phase 7)
Handles similarity search with filtering and pagination.

```javascript
const {
  search,
  results,
  isSearching,
  error,
  hasMore,
  loadMore,
  filters,
  updateFilters
} = useSimilaritySearch(songId, instrument);

// Usage
useEffect(() => {
  search();
}, [filters]);
```

## State Management

### UserContext (NEW - Phase 3)
Provides user data and subscription tier throughout the app.

```javascript
const { user, tier, isAuthenticated, login, logout } = useUser();

// Usage
{tier === 'free' && (
  <UpgradePrompt 
    feature="MIDI Download" 
    requiredTier="producer" 
  />
)}
```

### AnalysisContext
Manages current analysis state across components.

```javascript
const {
  currentAnalysis,
  setAnalysis,
  clearAnalysis
} = useAnalysis();
```

## Styling Guidelines

### Tailwind Configuration
```javascript
// tailwind.config.js
module.exports = {
  content: ['./src/**/*.{js,jsx,ts,tsx}'],
  theme: {
    extend: {
      colors: {
        primary: '#3B82F6',
        secondary: '#8B5CF6',
        accent: '#EC4899',
        success: '#10B981',
        warning: '#F59E0B',
        error: '#EF4444',
        // Tier colors
        'tier-free': '#6B7280',
        'tier-starter': '#3B82F6',
        'tier-producer': '#8B5CF6',
        'tier-studio': '#F59E0B'
      }
    }
  }
};
```

### Component Styling
- Use Tailwind utility classes for most styling
- Custom CSS only for complex animations or Canvas-based components
- Maintain consistent spacing (use Tailwind's spacing scale)
- Use responsive modifiers: `sm:`, `md:`, `lg:`, `xl:`

### Color Usage
- Primary: Main CTAs, links
- Secondary: Hover states, accents
- Success: Upload success, completed actions
- Warning: Upgrade prompts, approaching limits
- Error: Validation errors, API errors

## Tier-Based Feature Gating

### Implementation Pattern
```javascript
const FeatureComponent = ({ userTier }) => {
  const canAccess = ['producer', 'studio'].includes(userTier);
  
  if (!canAccess) {
    return (
      <UpgradePrompt 
        feature="Similarity Search"
        requiredTier="producer"
        inline={true}
      />
    );
  }
  
  return <ActualFeature />;
};
```

### Tier Capabilities
| Feature | Free | Starter | Producer | Studio |
|---------|------|---------|----------|--------|
| Upload length | 15s | 30s | 90s | 5min |
| Analyses/month | 3 | 25 | Unlimited | Unlimited |
| MIDI download | ✗ | Drums only | All | All |
| Similarity search | Preview | 10 results | Unlimited | Unlimited |
| Download similar MIDI | ✗ | ✗ | ✓ | ✓ |

## Environment Variables

Required `.env` variables:

```bash
# API
REACT_APP_API_URL=http://localhost:8000

# Feature Flags
REACT_APP_ENABLE_SIMILARITY_SEARCH=false
REACT_APP_ENABLE_PATTERN_LIBRARY=false

# Payments (future)
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_test_...

# Analytics (future)
REACT_APP_GOOGLE_ANALYTICS_ID=UA-XXXXX-Y
```

## Available Scripts

- `npm start` - Run development server
- `npm run build` - Build for production
- `npm test` - Run tests
- `npm run lint` - Run ESLint
- `npm run format` - Format with Prettier
- `npm run eject` - Eject from Create React App (irreversible!)

## Supported Audio Formats

- MP3 (.mp3)
- WAV (.wav)
- FLAC (.flac)
- M4A (.m4a)
- OGG (.ogg)

**File Size Limits:**
- Free tier: 50MB
- All paid tiers: 50MB

## Development Workflow

### Current Phase: Phase 1 Complete ✅

**Next Up (Phase 3-4):**
1. Integrate wavesurfer.js for waveform display
2. Add time range selection component
3. Create instrument selector
4. Connect to `/api/analyze` endpoint
5. Handle duplicate detection feedback
6. Display loading states during processing

**Testing Checklist:**
- [ ] Waveform loads and displays correctly
- [ ] Time selection respects tier limits (15s, 30s, 90s)
- [ ] Analysis request includes correct parameters
- [ ] Duplicate detection shows helpful message
- [ ] Loading states prevent multiple submissions
- [ ] Error messages are user-friendly

### Phase 7: Pattern Discovery (Future)
1. Build SimilaritySearch component
2. Implement filtering UI
3. Create ResultsGrid with pagination
4. Add audio preview functionality
5. Implement MIDI download (tier-gated)
6. Add empty states and upgrade prompts

## Testing

### Unit Tests
```bash
npm test

# With coverage
npm test -- --coverage
```

### Component Testing
```bash
# Test specific component
npm test FileUpload

# Watch mode
npm test -- --watch
```

### E2E Testing (future)
```bash
# Using Cypress
npm run cypress:open
```

## Performance Optimization

- Lazy load components with `React.lazy()` and `Suspense`
- Memoize expensive computations with `useMemo`
- Debounce search inputs and filters
- Virtualize long lists (react-window or react-virtualized)
- Code-split routes (when adding React Router)
- Optimize images and assets
- Use service workers for caching (future)

## Common Issues & Solutions

### Backend Connection Issues

Make sure the Django backend is running:
```bash
cd backend
source venv/bin/activate
python manage.py runserver
```

### CORS Errors

Check Django CORS settings in `backend/config/settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
]
```

### Wavesurfer Not Loading

Install wavesurfer.js:
```bash
npm install wavesurfer.js
```

### Port Already in Use

Specify a different port:
```bash
PORT=3001 npm start
```

## Accessibility

- Use semantic HTML elements
- Add ARIA labels to interactive elements
- Ensure keyboard navigation works
- Maintain sufficient color contrast
- Provide text alternatives for audio content
- Test with screen readers

## Browser Support

- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Mobile browsers (iOS Safari, Chrome Mobile)

## Deployment

### Production Build
```bash
npm run build
```

### Environment Configuration
Set production environment variables:
```bash
REACT_APP_API_URL=https://api.midime.com
REACT_APP_ENABLE_SIMILARITY_SEARCH=true
```

### Hosting Options
- **Vercel** (recommended) - Zero-config deployment
- **Netlify** - Easy CI/CD integration
- **AWS S3 + CloudFront** - Full control
- **GitHub Pages** - Free for public repos

## Contributing

See main project README.md for development guidelines and .clinerules for coding standards.

## Support

For questions or issues:
- Check the main README.md
- Review the .clinerules file
- Contact: jessemhernandez123@gmail.com

---

**Last Updated**: October 14, 2025  
**Version**: 0.2.0 (Phase 1 Complete, Phase 3-6 In Progress)