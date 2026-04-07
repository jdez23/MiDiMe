import {
  useCallback,
  useEffect,
  useLayoutEffect,
  useMemo,
  useRef,
  useState,
} from 'react';
import { PRESETS } from '../data/presets';
import { tileArray } from '../audio/drumAnalysis';
import { buildDrumPatternMidi, downloadBlob } from '../audio/exportMidi';
import { drawWaveform } from '../audio/waveform';
import api from '../services/api';

const LS_KEY = 'midime-drum-visualizer-v1';
const DEFAULT_GRID_SIZE = 16;
const DEFAULT_BAR_COUNT = 2;
const MAX_REGION = 30;
const MIN_REGION = 1;

function formatTime(seconds) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, '0')}`;
}

const GRADIENT_COLORS = ['#96d7ff', '#c8aaff', '#ffb4c8', '#ffdc96'];
const ZOOM_LEVELS = [1, 2, 4, 8];

const ROW_CONFIG = [
  { label: 'Kick', cls: 'kick', row: 'kick', vel: 'kickVel' },
  { label: 'Snare', cls: 'snare', row: 'snare', vel: 'snareVel' },
  { label: 'Hi-Hat', cls: 'hihat', row: 'hihat', vel: 'hihatVel' },
];

function patternFromPreset(index, gridSize, barCount) {
  const p = PRESETS[index];
  const ns = gridSize * barCount;
  return {
    kick: tileArray(p.kick, ns),
    snare: tileArray(p.snare, ns),
    hihat: tileArray(p.hihat, ns),
    kickVel: tileArray(p.kickVel, ns),
    snareVel: tileArray(p.snareVel, ns),
    hihatVel: tileArray(p.hihatVel, ns),
    bpm: p.bpm,
    swing: p.swing,
    steps: ns,
    style: { name: p.genre, desc: p.desc },
    desc: p.desc,
  };
}

export default function DrumDissect() {
  const [dragOver, setDragOver] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingProgress, setLoadingProgress] = useState(0);
  const [loadingMessage, setLoadingMessage] = useState('');
  const [error, setError] = useState(null);
  const [audioBuffer, setAudioBuffer] = useState(null);
  const [trackName, setTrackName] = useState('—');
  const [gridSize, setGridSize] = useState(DEFAULT_GRID_SIZE);
  const [barCount, setBarCount] = useState(DEFAULT_BAR_COUNT);
  const [currentPattern, setCurrentPattern] = useState(() =>
    patternFromPreset(0, DEFAULT_GRID_SIZE, DEFAULT_BAR_COUNT)
  );
  const [activePresetIndex, setActivePresetIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [playheadPct, setPlayheadPct] = useState(0);
  const [timeDisplay, setTimeDisplay] = useState('0:00');
  const [hydrated, setHydrated] = useState(false);
  const [regionStart, setRegionStart] = useState(0);
  const [regionEnd, setRegionEnd] = useState(MAX_REGION);
  const [zoomLevel, setZoomLevel] = useState(1);
  const [zoomOffset, setZoomOffset] = useState(0);

  const fileInputRef = useRef(null);
  const canvasRef = useRef(null);
  const waveformWrapRef = useRef(null);
  const audioCtxRef = useRef(null);
  const sourceNodeRef = useRef(null);
  const startTimeRef = useRef(0);
  const pauseOffsetRef = useRef(0);
  const animRef = useRef(null);
  const isPlayingRef = useRef(false);
  const uploadedFileRef = useRef(null);
  const abortRef = useRef(null);
  const draggingRef = useRef(null);
  const tickFnRef = useRef(null);
  // Stable function reference whose identity never changes — RAF always calls this,
  // and it delegates to tickFnRef.current which IS updated every render.
  const stableTick = useRef(function stableTick() { tickFnRef.current?.(); });
  const dragOriginRef = useRef({ x: 0, rStart: 0, rEnd: 0 });

  useEffect(() => {
    isPlayingRef.current = isPlaying;
  }, [isPlaying]);

  // --- LocalStorage hydration ---
  useEffect(() => {
    try {
      const raw = localStorage.getItem(LS_KEY);
      if (!raw) {
        setHydrated(true);
        return;
      }
      const o = JSON.parse(raw);
      const gs = Number(o.gridSize) || 16;
      const bc = Number(o.barCount) || 2;
      const ns = gs * bc;
      if (o.pattern && o.pattern.steps === ns) {
        setCurrentPattern(o.pattern);
        setGridSize(gs);
        setBarCount(bc);
        setActivePresetIndex(
          typeof o.activePresetIndex === 'number' ? o.activePresetIndex : null
        );
      }
    } catch {
      /* ignore */
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated || !currentPattern) return;
    try {
      localStorage.setItem(
        LS_KEY,
        JSON.stringify({
          gridSize,
          barCount,
          activePresetIndex,
          pattern: currentPattern,
        })
      );
    } catch {
      /* quota */
    }
  }, [hydrated, currentPattern, gridSize, barCount, activePresetIndex]);

  const LOADING_CELLS = useMemo(
    () =>
      Array.from({ length: 200 }, (_, i) => ({
        top: Math.random() * 100,
        left: Math.random() * 100,
        color: GRADIENT_COLORS[i % GRADIENT_COLORS.length],
        delay: Math.random() * 200,
      })),
    []
  );

  // --- Explicit analysis: only runs when user clicks "Analyze Selection" ---
  const analyzeSelection = useCallback(async () => {
    if (!uploadedFileRef.current) return;

    if (abortRef.current) {
      abortRef.current.abort();
    }
    const controller = new AbortController();
    abortRef.current = controller;

    setLoading(true);
    setLoadingProgress(0);
    setLoadingMessage('Preparing…');
    setError(null);

    try {
      const pattern = await api.analyzeAudio(
        uploadedFileRef.current,
        gridSize,
        barCount,
        regionStart,
        regionEnd,
        controller.signal,
        (event) => {
          setLoadingProgress(event.progress);
          setLoadingMessage(event.message);
        }
      );
      setCurrentPattern(pattern);
      setActivePresetIndex(null);
    } catch (err) {
      if (controller.signal.aborted) return;
      setError(err.message || 'Server analysis failed');
    } finally {
      if (!controller.signal.aborted) {
        setLoading(false);
      }
      if (abortRef.current === controller) {
        abortRef.current = null;
      }
    }
  }, [gridSize, barCount, regionStart, regionEnd]);

  // --- Preset grid/bar sync ---
  useEffect(() => {
    if (audioBuffer) return;
    if (activePresetIndex === null || activePresetIndex < 0) return;
    setCurrentPattern(patternFromPreset(activePresetIndex, gridSize, barCount));
  }, [gridSize, barCount, audioBuffer, activePresetIndex]);

  const regionDur = regionEnd - regionStart;

  // --- Playback (scoped to selected region) ---
  const stopPlayback = useCallback(() => {
    if (sourceNodeRef.current) {
      sourceNodeRef.current.onended = null;
      try {
        sourceNodeRef.current.stop();
        sourceNodeRef.current.disconnect();
      } catch {
        /* already stopped */
      }
      sourceNodeRef.current = null;
    }
    if (audioCtxRef.current) {
      pauseOffsetRef.current =
        audioCtxRef.current.currentTime - startTimeRef.current;
    }
    setIsPlaying(false);
    if (animRef.current) {
      cancelAnimationFrame(animRef.current);
      animRef.current = null;
    }
    if (audioBuffer) {
      const absTime = regionStart + pauseOffsetRef.current;
      setPlayheadPct((absTime / audioBuffer.duration) * 100);
      setTimeDisplay(formatTime(pauseOffsetRef.current));
    }
  }, [audioBuffer, regionStart]);

  // Keep tickFnRef current every render so the rAF loop always reads fresh values
  tickFnRef.current = () => {
    const ctx = audioCtxRef.current;
    const buf = audioBuffer;
    if (!ctx || !buf || !isPlayingRef.current) return;
    const elapsed = ctx.currentTime - startTimeRef.current;
    if (elapsed >= regionDur) {
      pauseOffsetRef.current = 0;
      setPlayheadPct((regionStart / buf.duration) * 100);
      setTimeDisplay('0:00');
      setIsPlaying(false);
      isPlayingRef.current = false;
      return;
    }
    const absTime = regionStart + elapsed;
    setPlayheadPct((absTime / buf.duration) * 100);
    setTimeDisplay(formatTime(elapsed));
    animRef.current = requestAnimationFrame(stableTick.current);
  };

  const tickPlayhead = useCallback(() => {
    stableTick.current();
  }, []);

  const startPlayback = useCallback(() => {
    if (!audioBuffer) return;
    if (sourceNodeRef.current) {
      sourceNodeRef.current.onended = null;
      try {
        sourceNodeRef.current.stop();
        sourceNodeRef.current.disconnect();
      } catch { /* */ }
      sourceNodeRef.current = null;
    }
    if (animRef.current) {
      cancelAnimationFrame(animRef.current);
      animRef.current = null;
    }
    let ctx = audioCtxRef.current;
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      ctx = new AC();
      audioCtxRef.current = ctx;
    }
    const src = ctx.createBufferSource();
    src.buffer = audioBuffer;
    src.connect(ctx.destination);
    const offset = regionStart + pauseOffsetRef.current;
    const remaining = regionDur - pauseOffsetRef.current;
    src.start(0, offset, remaining);
    startTimeRef.current = ctx.currentTime - pauseOffsetRef.current;
    sourceNodeRef.current = src;
    setIsPlaying(true);
    isPlayingRef.current = true;
    src.onended = () => {
      if (!isPlayingRef.current) return;
      if (animRef.current) cancelAnimationFrame(animRef.current);
      animRef.current = null;
      pauseOffsetRef.current = 0;
      setPlayheadPct((regionStart / audioBuffer.duration) * 100);
      setTimeDisplay('0:00');
      setIsPlaying(false);
      isPlayingRef.current = false;
      sourceNodeRef.current = null;
    };
    animRef.current = requestAnimationFrame(tickPlayhead);
  }, [audioBuffer, regionStart, regionDur, tickPlayhead]);

  const togglePlay = useCallback(() => {
    if (!audioBuffer) return;
    if (isPlayingRef.current) stopPlayback();
    else startPlayback();
  }, [audioBuffer, startPlayback, stopPlayback]);

  useEffect(
    () => () => {
      if (animRef.current) cancelAnimationFrame(animRef.current);
      if (sourceNodeRef.current) {
        try {
          sourceNodeRef.current.stop();
        } catch {
          /* */
        }
      }
    },
    []
  );

  useEffect(() => {
    const onKey = (e) => {
      if (e.code !== 'Space') return;
      const tag = e.target?.tagName;
      if (tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT') return;
      if (!audioBuffer) return;
      e.preventDefault();
      togglePlay();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [audioBuffer, togglePlay]);

  useLayoutEffect(() => {
    if (!audioBuffer || !waveformWrapRef.current) return;
    const viewEnd = Math.min(1, zoomOffset + 1 / zoomLevel);
    const win = zoomLevel > 1 ? { start: zoomOffset, end: viewEnd } : null;
    const el = waveformWrapRef.current;
    const ro = new ResizeObserver(() => {
      drawWaveform(canvasRef.current, audioBuffer, win);
    });
    ro.observe(el);
    drawWaveform(canvasRef.current, audioBuffer, win);
    return () => ro.disconnect();
  }, [audioBuffer, zoomLevel, zoomOffset]);

  // --- File handling: send to backend ---
  const handleFile = async (file) => {
    if (!file) return;
    setError(null);
    uploadedFileRef.current = file;

    let ctx = audioCtxRef.current;
    if (!ctx) {
      const AC = window.AudioContext || window.webkitAudioContext;
      ctx = new AC();
      audioCtxRef.current = ctx;
    }

    let buf;
    try {
      buf = await ctx.decodeAudioData(await file.arrayBuffer());
    } catch (err) {
      console.error(err);
      setError('Could not decode audio file.');
      setLoading(false);
      return;
    }

    stopPlayback();
    pauseOffsetRef.current = 0;
    setCurrentPattern(null);
    setActivePresetIndex(null);
    setAudioBuffer(buf);
    setTrackName(file.name);
    setPlayheadPct(0);
    setTimeDisplay('0:00');
    setRegionStart(0);
    setRegionEnd(Math.min(buf.duration, MAX_REGION));
    setZoomLevel(1);
    setZoomOffset(0);
  };

  const loadPreset = (i) => {
    setActivePresetIndex(i);
    setCurrentPattern(patternFromPreset(i, gridSize, barCount));
  };

  const clearUploadedAudio = useCallback(() => {
    if (abortRef.current) {
      abortRef.current.abort();
      abortRef.current = null;
    }
    if (animRef.current) {
      cancelAnimationFrame(animRef.current);
      animRef.current = null;
    }
    if (sourceNodeRef.current) {
      try {
        sourceNodeRef.current.stop();
        sourceNodeRef.current.disconnect();
      } catch {
        /* */
      }
      sourceNodeRef.current = null;
    }
    pauseOffsetRef.current = 0;
    isPlayingRef.current = false;
    setIsPlaying(false);
    setAudioBuffer(null);
    setTrackName('—');
    setPlayheadPct(0);
    setTimeDisplay('0:00');
    setActivePresetIndex(0);
    setCurrentPattern(patternFromPreset(0, gridSize, barCount));
    setError(null);
    setRegionStart(0);
    setRegionEnd(MAX_REGION);
    uploadedFileRef.current = null;
    setZoomLevel(1);
    setZoomOffset(0);
  }, [gridSize, barCount]);

  const onExportMidi = () => {
    if (!currentPattern) return;
    const blob = buildDrumPatternMidi(currentPattern, gridSize);
    downloadBlob(blob, 'drum-pattern.mid');
  };

  const toggleCell = (rowKey, step) => {
    setCurrentPattern((prev) => {
      if (!prev) return prev;
      const kick = [...prev.kick];
      const snare = [...prev.snare];
      const hihat = [...prev.hihat];
      const kickVel = [...prev.kickVel];
      const snareVel = [...prev.snareVel];
      const hihatVel = [...prev.hihatVel];
      const map = { kick, snare, hihat };
      const vmap = { kick: kickVel, snare: snareVel, hihat: hihatVel };
      const d = map[rowKey];
      const v = vmap[rowKey];
      d[step] = d[step] > 0 ? 0 : 1;
      v[step] = d[step] > 0 ? 0.8 : 0;
      return { ...prev, kick, snare, hihat, kickVel, snareVel, hihatVel };
    });
  };


  const zoomIn = useCallback(() => {
    setZoomLevel((prev) => {
      const idx = ZOOM_LEVELS.indexOf(prev);
      if (idx === ZOOM_LEVELS.length - 1) return prev;
      const next = ZOOM_LEVELS[idx + 1];
      // Keep the center of the current view centered after zoom
      const viewCenter = zoomOffset + 1 / (prev * 2);
      const newOffset = Math.max(0, Math.min(1 - 1 / next, viewCenter - 1 / (next * 2)));
      setZoomOffset(newOffset);
      return next;
    });
  }, [zoomOffset]);

  const zoomOut = useCallback(() => {
    setZoomLevel((prev) => {
      const idx = ZOOM_LEVELS.indexOf(prev);
      if (idx === 0) return prev;
      const next = ZOOM_LEVELS[idx - 1];
      const viewCenter = zoomOffset + 1 / (prev * 2);
      const newOffset = Math.max(0, Math.min(1 - 1 / next, viewCenter - 1 / (next * 2)));
      setZoomOffset(newOffset);
      return next;
    });
  }, [zoomOffset]);

  const onWaveformWheel = useCallback(
    (e) => {
      if (!audioBuffer) return;
      e.preventDefault();
      if (e.deltaY < 0) zoomIn();
      else zoomOut();
    },
    [audioBuffer, zoomIn, zoomOut]
  );

  useEffect(() => {
    const el = waveformWrapRef.current;
    if (!el) return;
    el.addEventListener('wheel', onWaveformWheel, { passive: false });
    return () => el.removeEventListener('wheel', onWaveformWheel);
  }, [onWaveformWheel]);

  const pxToTime = useCallback(
    (clientX) => {
      if (!waveformWrapRef.current || !audioBuffer) return 0;
      const rect = waveformWrapRef.current.getBoundingClientRect();
      const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
      return zoomOffset * audioBuffer.duration + pct * (audioBuffer.duration / zoomLevel);
    },
    [audioBuffer, zoomLevel, zoomOffset]
  );

  const onHandleDown = useCallback(
    (which, e) => {
      e.preventDefault();
      e.stopPropagation();
      draggingRef.current = which;
      const x = e.touches ? e.touches[0].clientX : e.clientX;
      dragOriginRef.current = { x, rStart: regionStart, rEnd: regionEnd };
    },
    [regionStart, regionEnd]
  );

  useEffect(() => {
    const onMove = (e) => {
      if (!draggingRef.current || !audioBuffer) return;
      const x = e.touches ? e.touches[0].clientX : e.clientX;
      const t = pxToTime(x);
      const which = draggingRef.current;

      if (which === 'start') {
        const ns = Math.max(0, Math.min(regionEnd - MIN_REGION, t));
        const clamped = ns < regionEnd - MAX_REGION ? regionEnd - MAX_REGION : ns;
        setRegionStart(clamped);
        pauseOffsetRef.current = 0;
        setPlayheadPct((clamped / audioBuffer.duration) * 100);
      } else if (which === 'end') {
        const ne = Math.min(audioBuffer.duration, Math.max(regionStart + MIN_REGION, t));
        const clamped = ne > regionStart + MAX_REGION ? regionStart + MAX_REGION : ne;
        setRegionEnd(clamped);
      } else if (which === 'region') {
        const delta = t - pxToTime(dragOriginRef.current.x);
        const len = dragOriginRef.current.rEnd - dragOriginRef.current.rStart;
        let ns = dragOriginRef.current.rStart + delta;
        if (ns < 0) ns = 0;
        if (ns + len > audioBuffer.duration) ns = audioBuffer.duration - len;
        setRegionStart(ns);
        setRegionEnd(ns + len);
        pauseOffsetRef.current = 0;
        setPlayheadPct((ns / audioBuffer.duration) * 100);
      }
    };

    const onUp = () => {
      if (draggingRef.current) {
        draggingRef.current = null;
        pauseOffsetRef.current = 0;
      }
    };

    window.addEventListener('mousemove', onMove);
    window.addEventListener('mouseup', onUp);
    window.addEventListener('touchmove', onMove, { passive: false });
    window.addEventListener('touchend', onUp);
    return () => {
      window.removeEventListener('mousemove', onMove);
      window.removeEventListener('mouseup', onUp);
      window.removeEventListener('touchmove', onMove);
      window.removeEventListener('touchend', onUp);
    };
  }, [audioBuffer, regionStart, regionEnd, pxToTime]);

  const spb = gridSize / 4;
  const steps = currentPattern?.steps ?? gridSize * barCount;
  const activeStep =
    isPlaying && audioBuffer
      ? Math.floor(
          (((playheadPct / 100) * audioBuffer.duration - regionStart) / regionDur) * steps
        )
      : -1;

  const analysis = currentPattern && {
    bpm: currentPattern.bpm,
    bpmDetail: `${(60 / currentPattern.bpm).toFixed(2)}s per beat`,
    styleName: currentPattern.style.name,
    styleDetail: currentPattern.style.desc || currentPattern.desc,
    swing: `${currentPattern.swing}%`,
    swingDetail:
      currentPattern.swing > 10
        ? 'Shuffled feel'
        : currentPattern.swing > 3
          ? 'Slight swing'
          : 'Straight',
    density: `${Math.round(
      ((currentPattern.kick.filter(Boolean).length +
        currentPattern.snare.filter(Boolean).length +
        currentPattern.hihat.filter(Boolean).length) /
        (currentPattern.steps * 3)) *
        100
    )}%`,
    densityDetail: `${currentPattern.kick.filter(Boolean).length + currentPattern.snare.filter(Boolean).length + currentPattern.hihat.filter(Boolean).length} hits / ${currentPattern.steps} steps`,
  };

  // --- Region drag interaction ---
  const dur = audioBuffer?.duration ?? 1;
  // When zoomed, positions are relative to the visible view window
  const viewDur = dur / zoomLevel;
  const viewStart = zoomOffset * dur;
  const regionLeftPct = ((regionStart - viewStart) / viewDur) * 100;
  const regionWidthPct = ((regionEnd - regionStart) / viewDur) * 100;
  // Playhead as % of visible window
  const playheadInViewPct =
    audioBuffer
      ? (((playheadPct / 100) * dur - viewStart) / viewDur) * 100
      : playheadPct;
  const regionLabel = `${formatTime(regionStart)} — ${formatTime(regionEnd)}`;

  const onWaveformMouseDown = useCallback(
    (e) => {
      if (!audioBuffer || !waveformWrapRef.current) return;
      e.preventDefault();

      const getTime = (clientX) => {
        const rect = waveformWrapRef.current.getBoundingClientRect();
        const pct = Math.max(0, Math.min(1, (clientX - rect.left) / rect.width));
        return zoomOffset * audioBuffer.duration + pct * (audioBuffer.duration / zoomLevel);
      };

      const startX = e.clientX;
      const startTime = getTime(startX);
      const startZoomOffset = zoomOffset;
      const rect = waveformWrapRef.current.getBoundingClientRect();
      const inSelection = zoomLevel > 1 && startTime >= regionStart && startTime <= regionEnd;

      let dragging = false;
      let mode = null;

      const onMove = (ev) => {
        const dx = ev.clientX - startX;
        if (!dragging && Math.abs(dx) > 3) {
          dragging = true;
          mode = inSelection ? 'pan' : 'select';
          if (mode === 'select') {
            if (isPlayingRef.current) {
              if (sourceNodeRef.current) {
                sourceNodeRef.current.onended = null;
                try { sourceNodeRef.current.stop(); sourceNodeRef.current.disconnect(); } catch { /* */ }
                sourceNodeRef.current = null;
              }
              if (animRef.current) { cancelAnimationFrame(animRef.current); animRef.current = null; }
              isPlayingRef.current = false;
              setIsPlaying(false);
            }
            pauseOffsetRef.current = 0;
            setRegionStart(startTime);
            setRegionEnd(startTime);
            setPlayheadPct((startTime / audioBuffer.duration) * 100);
          }
        }
        if (!dragging) return;

        if (mode === 'pan') {
          const fracDelta = dx / rect.width;
          const timeDelta = fracDelta * (audioBuffer.duration / zoomLevel);
          const newOffset = Math.max(0, Math.min(1 - 1 / zoomLevel,
            startZoomOffset - timeDelta / audioBuffer.duration));
          setZoomOffset(newOffset);
        } else {
          const t = getTime(ev.clientX);
          if (t >= startTime) {
            setRegionStart(startTime);
            setRegionEnd(Math.min(audioBuffer.duration, Math.min(startTime + MAX_REGION, t)));
            setPlayheadPct((startTime / audioBuffer.duration) * 100);
          } else {
            const ns = Math.max(0, Math.max(startTime - MAX_REGION, t));
            setRegionStart(ns);
            setRegionEnd(startTime);
            setPlayheadPct((ns / audioBuffer.duration) * 100);
          }
        }
      };

      const onUp = (ev) => {
        window.removeEventListener('mousemove', onMove);
        window.removeEventListener('mouseup', onUp);
        if (!dragging) {
          // Plain click → seek
          const clickTime = getTime(ev.clientX);
          const clamped = Math.max(regionStart, Math.min(regionEnd, clickTime));
          pauseOffsetRef.current = clamped - regionStart;
          if (isPlayingRef.current && sourceNodeRef.current) {
            sourceNodeRef.current.onended = null;
            try { sourceNodeRef.current.stop(); sourceNodeRef.current.disconnect(); } catch { /* */ }
            sourceNodeRef.current = null;
            setIsPlaying(false);
            isPlayingRef.current = false;
            if (animRef.current) cancelAnimationFrame(animRef.current);
            startPlayback();
          } else {
            setPlayheadPct((clamped / audioBuffer.duration) * 100);
            setTimeDisplay(formatTime(clamped - regionStart));
          }
        }
      };

      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
    },
    [audioBuffer, zoomLevel, zoomOffset, regionStart, regionEnd, startPlayback]
  );

  const shellClass = `drop-zone-shell${dragOver ? ' drop-zone-shell--dragover' : ''}`;

  return (
    <div>
      <div
        className={shellClass}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragOver(false);
          const f = e.dataTransfer.files[0];
          if (f) handleFile(f);
        }}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
      >
        <div className="drop-zone-blob" aria-hidden="true" />
        <div
          role="button"
          tabIndex={0}
          className="drop-zone-content"
          onClick={() => fileInputRef.current?.click()}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ' ') {
              e.preventDefault();
              fileInputRef.current?.click();
            }
          }}
        >
          <span className="drop-icon"></span>
          <div className="drop-text">
            <strong>drop audio here</strong>
            <br />
            or tap to browse
          </div>
          <div className="drop-hint">wav · mp3 · aiff · flac</div>
          <input
            ref={fileInputRef}
            type="file"
            accept="audio/*,.wav,.mp3,.aiff,.flac,.ogg"
            className="visually-hidden-input"
            aria-label="Choose audio file"
            onChange={(e) => {
              const f = e.target.files?.[0];
              if (f) handleFile(f);
            }}
          />
        </div>
      </div>

      {audioBuffer ? (
        <div className="transport-section">
          <div className="transport-header">
            <span className="track-name track-name--header" title={trackName}>
              {trackName}
            </span>
            <button
              type="button"
              className="transport-dismiss"
              aria-label="Remove audio and return to reference patterns"
              onClick={clearUploadedAudio}
            >
              ×
            </button>
            <button
              type="button"
              className="analyze-btn"
              onClick={analyzeSelection}
              disabled={loading}
            >
              Analyze Selection
            </button>
          </div>
          <p className="region-label">{regionLabel}</p>
          <div className="waveform-zoom-bar">
            <button
              type="button"
              className="zoom-btn"
              aria-label="Zoom out"
              disabled={zoomLevel === 1}
              onClick={zoomOut}
            >
              −
            </button>
            <span className="zoom-label">{zoomLevel}×</span>
            <button
              type="button"
              className="zoom-btn"
              aria-label="Zoom in"
              disabled={zoomLevel === 8}
              onClick={zoomIn}
            >
              +
            </button>
          </div>
          <div className="transport">
            <button
              type="button"
              className="transport-btn"
              aria-label={isPlaying ? 'Pause' : 'Play'}
              onClick={togglePlay}
            >
              {isPlaying ? '⏸' : '▶'}
            </button>
            <div
              ref={waveformWrapRef}
              className="waveform-container"
              onMouseDown={onWaveformMouseDown}
              role="presentation"
              style={{ cursor: 'crosshair' }}
            >
              <canvas ref={canvasRef} className="waveform-canvas" />
              {regionEnd > regionStart && (
                <>
                  <div
                    className="region-dim"
                    style={{ left: 0, width: `${Math.max(0, regionLeftPct)}%` }}
                  />
                  <div
                    className="region-dim"
                    style={{
                      left: `${Math.min(100, regionLeftPct + regionWidthPct)}%`,
                      right: 0,
                      width: 'auto',
                    }}
                  />
                  <div
                    className="waveform-region"
                    style={{ left: `${regionLeftPct}%`, width: `${regionWidthPct}%` }}
                    onMouseDown={(e) => onHandleDown('region', e)}
                    onTouchStart={(e) => onHandleDown('region', e)}
                  />
                  <div
                    className="region-handle region-handle--start"
                    style={{ left: `${regionLeftPct}%` }}
                    onMouseDown={(e) => onHandleDown('start', e)}
                    onTouchStart={(e) => onHandleDown('start', e)}
                  />
                  <div
                    className="region-handle region-handle--end"
                    style={{ left: `${regionLeftPct + regionWidthPct}%` }}
                    onMouseDown={(e) => onHandleDown('end', e)}
                    onTouchStart={(e) => onHandleDown('end', e)}
                  />
                </>
              )}
              <div className="playhead" style={{ left: `${playheadInViewPct}%` }} />
            </div>
            <span className="time-display">{timeDisplay}</span>
          </div>
        </div>
      ) : null}

      {error && (
        <div className="pattern-desc pattern-desc--error alert-block">
          <div className="panel-heading">Analysis failed</div>
          <div className="panel-body">{error}</div>
          <button type="button" className="text-link" onClick={analyzeSelection}>
            Retry
          </button>
        </div>
      )}

      {!audioBuffer ? (
        <>
          <div className="section-header">
            <span className="section-title">Reference Patterns</span>
            <div className="section-line" />
          </div>
          <p className="section-microcopy section-microcopy--below">
            Pick a template to load into the grid. Upload audio to replace this
            section with the waveform and analyze your own loop.
          </p>
          <div className="preset-grid">
            {PRESETS.map((p, i) => (
              <button
                key={p.name}
                type="button"
                className={`preset-btn${activePresetIndex === i ? ' active' : ''}`}
                onClick={() => loadPreset(i)}
              >
                <span className="preset-name">{p.name}</span>
                <div className="preset-genre">{p.genre}</div>
              </button>
            ))}
          </div>
        </>
      ) : null}

      <div className={analysis ? 'analysis-info' : 'analysis-info hidden'}>
        <div className="info-card">
          <div className="info-card-label">Style</div>
          <div className="info-card-value">{analysis?.styleName}</div>
          <div className="info-card-detail">{analysis?.styleDetail}</div>
        </div>
        <div className="info-card">
          <div className="info-card-label">BPM</div>
          <div className="info-card-value">{analysis?.bpm ?? '—'}</div>
          <div className="info-card-detail">{analysis?.bpmDetail}</div>
        </div>
        <div className="info-card">
          <div className="info-card-label">Swing</div>
          <div className="info-card-value">{analysis?.swing}</div>
          <div className="info-card-detail">{analysis?.swingDetail}</div>
        </div>
        <div className="info-card">
          <div className="info-card-label">Density</div>
          <div className="info-card-value">{analysis?.density}</div>
          <div className="info-card-detail">{analysis?.densityDetail}</div>
        </div>
      </div>

      {currentPattern ? (
        <div>
          <div className="section-header">
            <span className="section-title">Pattern Grid</span>
            <div className="section-line" />
          </div>
          <div className="controls-row">
            <div className="control-group">
              <span className="control-label">Grid</span>
              <select
                className="grid-select"
                value={gridSize}
                onChange={(e) => setGridSize(Number(e.target.value))}
                aria-label="Steps per bar"
              >
                <option value={8}>8 steps</option>
                <option value={16}>16 steps</option>
                <option value={32}>32 steps</option>
              </select>
            </div>
            <div className="control-group">
              <span className="control-label">Bars</span>
              <select
                className="grid-select"
                value={barCount}
                onChange={(e) => setBarCount(Number(e.target.value))}
                aria-label="Number of bars"
              >
                <option value={1}>1 bar</option>
                <option value={2}>2 bars</option>
                <option value={4}>4 bars</option>
              </select>
            </div>
            <button type="button" className="export-btn" onClick={onExportMidi}>
              Export MIDI
            </button>
          </div>
          <div className="grid-wrapper">
            <div className="grid-header">
              {Array.from({ length: steps }, (_, i) => {
                const db = i % spb === 0;
                return (
                  <div key={i} className={`beat-label${db ? ' downbeat' : ''}`}>
                    {db ? Math.floor(i / spb) + 1 : '·'}
                  </div>
                );
              })}
            </div>
            {ROW_CONFIG.map((row) => (
              <div key={row.row} className="grid-row">
                <div className="row-label">
                  <span className={`row-dot ${row.cls}`} />
                  {row.label}
                </div>
                <div className="grid-cells">
                  {Array.from({ length: steps }, (_, i) => {
                    const data = currentPattern[row.row];
                    const vel = currentPattern[row.vel];
                    const active = data[i] > 0;
                    const db = i % spb === 0;
                    const v = vel[i] ?? 1;
                    return (
                      <button
                        key={i}
                        type="button"
                        className={`grid-cell${db ? ' downbeat' : ''}${
                          active ? ` active-${row.cls}` : ''
                        }${i === activeStep ? ' active-col' : ''}`}
                        style={active ? { opacity: 0.5 + v * 0.5 } : undefined}
                        title={
                          active
                            ? `${row.label} vel: ${Math.round(v * 127)}`
                            : undefined
                        }
                        onClick={() => toggleCell(row.row, i)}
                      >
                        {active && v < 0.6 ? (
                          <span className="velocity-bar" />
                        ) : null}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
          <div className="pattern-desc">{currentPattern.desc}</div>
        </div>
      ) : null}

      <div className={`loading-overlay${loading ? ' active' : ''}`}>
        <div className="loading-grid-bg" aria-hidden="true">
          {LOADING_CELLS.map((cell, i) => (
            <div
              key={i}
              className={`loading-cell${cell.left < loadingProgress * 120 ? ' visible' : ''}`}
              style={{
                top: `${cell.top}%`,
                left: `${cell.left}%`,
                '--cell-color': cell.color,
                animationDelay: `${cell.delay}ms`,
              }}
            />
          ))}
        </div>
        <div className="loading-content">
          <div className="loading-bar-track">
            <div
              className="loading-bar-fill"
              style={{ width: `${loadingProgress * 100}%` }}
            />
          </div>
          <div className="loading-status">{loadingMessage}</div>
          <div className="loading-pct">
            {Math.round(loadingProgress * 100)}%
          </div>
        </div>
      </div>
    </div>
  );
}
