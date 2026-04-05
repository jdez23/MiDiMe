import json
import os
import time
import logging
import shutil
import uuid
from collections import defaultdict
from pathlib import Path
from threading import Lock

from django.conf import settings
from django.http import StreamingHttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import FileUploadSerializer, AudioAnalyzeSerializer

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Simple in-memory rate limiter (per-IP, sliding window)
# ---------------------------------------------------------------------------
_rate_lock = Lock()
_rate_log: dict = defaultdict(list)

RATE_WINDOW = 60
RATE_MAX_REQUESTS = 5


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    with _rate_lock:
        timestamps = _rate_log[ip]
        _rate_log[ip] = [t for t in timestamps if now - t < RATE_WINDOW]
        if len(_rate_log[ip]) >= RATE_MAX_REQUESTS:
            return False
        _rate_log[ip].append(now)
        return True


def _sanitize_filename(name: str) -> str:
    name = Path(name).name
    return name.replace("\x00", "").strip(". ")


def _event(stage, progress, message, **extra):
    """Format a single NDJSON progress event."""
    data = {"stage": stage, "progress": progress, "message": message}
    data.update(extra)
    return json.dumps(data) + "\n"


# ---------------------------------------------------------------------------
# Views
# ---------------------------------------------------------------------------

class FileUploadView(APIView):
    """POST /api/upload — accept audio file, return metadata."""

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Invalid file",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            audio_file = serializer.validated_data["audio_file"]
            safe_name = _sanitize_filename(audio_file.name)

            upload_dir = os.path.join(settings.MEDIA_ROOT, "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            file_path = os.path.join(upload_dir, safe_name)

            with open(file_path, "wb+") as dest:
                for chunk in audio_file.chunks():
                    dest.write(chunk)

            file_size_mb = audio_file.size / (1024 * 1024)

            return Response({
                "status": "success",
                "message": "File uploaded successfully",
                "data": {
                    "filename": safe_name,
                    "file_size": f"{file_size_mb:.2f} MB",
                    "file_size_bytes": audio_file.size,
                },
            })

        except Exception:
            logger.exception("Upload failed")
            return Response({
                "status": "error",
                "message": "File upload failed. Please try again.",
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HealthCheckView(APIView):
    """GET /api/health — lightweight liveness probe."""

    def get(self, request):
        from datetime import datetime

        return Response({
            "status": "healthy",
            "timestamp": datetime.now().isoformat() + "Z",
        })


class AudioAnalyzeView(APIView):
    """
    POST /api/analyze — drum pattern analysis with streaming progress.

    Returns NDJSON (newline-delimited JSON) with real-time stage updates.
    Rate-limited to 5 requests / IP / minute.
    """

    def post(self, request):
        ip = request.META.get("REMOTE_ADDR", "unknown")
        if not _check_rate_limit(ip):
            return Response({
                "status": "error",
                "message": "Too many requests. Please wait a minute before trying again.",
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)

        serializer = AudioAnalyzeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "status": "error",
                "message": "Invalid request data",
                "errors": serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        audio_file = serializer.validated_data["audio_file"]
        grid_size = serializer.validated_data["grid_size"]
        bar_count = serializer.validated_data["bar_count"]
        start_time = serializer.validated_data.get("start_time")
        end_time = serializer.validated_data.get("end_time")

        analysis_id = str(uuid.uuid4())
        request_dir = os.path.join(settings.MEDIA_ROOT, "processing", analysis_id)
        os.makedirs(request_dir, exist_ok=True)

        safe_name = _sanitize_filename(audio_file.name)
        file_path = os.path.join(request_dir, safe_name)

        def generate():
            try:
                yield _event("uploading", 0.05, "Saving audio…")

                with open(file_path, "wb+") as dest:
                    for chunk in audio_file.chunks():
                        dest.write(chunk)

                logger.info(
                    f"Analysis {analysis_id}: grid={grid_size}, bars={bar_count}"
                )

                audio_to_analyze = file_path
                if start_time is not None and end_time is not None:
                    yield _event("trimming", 0.10, "Trimming region…")
                    audio_to_analyze = self._trim(
                        file_path, start_time, end_time, request_dir
                    )

                yield _event("separating", 0.15, "Separating drum stem…")

                drum_onsets, method = self._classify_drums(
                    audio_to_analyze, request_dir
                )

                yield _event("detecting", 0.70, "Detecting tempo…")

                tempo = self._get_tempo(audio_to_analyze)

                logger.info(
                    f"  method={method}, tempo={tempo:.1f}, "
                    f"kicks={len(drum_onsets['kick'])}, "
                    f"snares={len(drum_onsets['snare'])}, "
                    f"hihats={len(drum_onsets['hihat'])}"
                )

                yield _event("building", 0.85, "Building pattern grid…")

                from audio_processing.quantizer import build_pattern_response

                pattern = build_pattern_response(
                    drum_onsets, tempo, grid_size, bar_count
                )

                yield _event(
                    "complete", 1.0, "Done",
                    pattern=pattern,
                    method=method,
                    analysis_id=analysis_id,
                )

            except Exception:
                logger.exception(f"Analysis {analysis_id} failed")
                yield _event(
                    "error", 0,
                    "Analysis failed. Please try a different audio file or region.",
                )

            finally:
                self._cleanup(request_dir)

        response = StreamingHttpResponse(
            generate(), content_type="text/plain; charset=utf-8"
        )
        response["Cache-Control"] = "no-cache"
        response["X-Accel-Buffering"] = "no"
        origin = request.META.get("HTTP_ORIGIN", "")
        if origin:
            response["Access-Control-Allow-Origin"] = origin
        return response

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _trim(file_path, start, end, out_dir):
        from audio_processing.utils import trim_audio

        trimmed = os.path.join(out_dir, "trimmed.wav")
        trim_audio(file_path, trimmed, start, end)
        return trimmed

    @staticmethod
    def _classify_drums(audio_path, work_dir):
        try:
            from audio_processing.stem_separator import separate_stems
            from audio_processing.onset_detector import analyze_drum_pattern
            from audio_processing.drum_classifier import classify_drum_pattern

            stems_dir = os.path.join(work_dir, "stems")
            stem_paths = separate_stems(audio_path, stems_dir)
            drum_stem = stem_paths.get("drums")

            if not drum_stem or not os.path.exists(drum_stem):
                raise RuntimeError("Drum stem not produced")

            import librosa

            y, sr = librosa.load(drum_stem, sr=22050, mono=True)
            analysis = analyze_drum_pattern(drum_stem, y=y, sr=sr)
            onset_times = analysis["onset_times"]
            drum_pattern = classify_drum_pattern(
                drum_stem, onset_times, y=y, sr=sr
            )
            return drum_pattern, "demucs"

        except (ImportError, RuntimeError) as exc:
            logger.warning(
                f"Demucs unavailable ({exc}), using band-analyzer fallback"
            )
            from audio_processing.band_analyzer import analyze_by_frequency_bands

            return analyze_by_frequency_bands(audio_path), "band_filter"

    @staticmethod
    def _get_tempo(audio_path):
        try:
            from audio_processing.band_analyzer import get_tempo_from_audio

            return get_tempo_from_audio(audio_path)
        except Exception:
            return 120.0

    @staticmethod
    def _cleanup(request_dir):
        try:
            if os.path.isdir(request_dir):
                shutil.rmtree(request_dir, ignore_errors=True)
        except OSError:
            pass
