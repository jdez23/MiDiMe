import os
import logging
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer, AudioAnalyzeSerializer

logger = logging.getLogger(__name__)


class FileUploadView(APIView):
    """
    POST /api/upload
    Accepts an audio file and returns filename and file size.
    """

    def post(self, request):
        serializer = FileUploadSerializer(data=request.data)

        if serializer.is_valid():
            try:
                audio_file = serializer.validated_data['audio_file']

                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                file_path = os.path.join(upload_dir, audio_file.name)

                with open(file_path, 'wb+') as dest:
                    for chunk in audio_file.chunks():
                        dest.write(chunk)

                file_size_mb = audio_file.size / (1024 * 1024)

                return Response({
                    'status': 'success',
                    'message': 'File uploaded successfully',
                    'data': {
                        'filename': audio_file.name,
                        'file_size': f"{file_size_mb:.2f} MB",
                        'file_size_bytes': audio_file.size,
                    }
                }, status=status.HTTP_200_OK)

            except Exception as exc:
                return Response({
                    'status': 'error',
                    'message': f'Error saving file: {exc}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            'status': 'error',
            'message': 'Invalid file',
            'errors': serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    """
    GET /api/health
    Returns the health status of the API.
    """

    def get(self, request):
        from datetime import datetime
        return Response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat() + 'Z',
        }, status=status.HTTP_200_OK)


class AudioAnalyzeView(APIView):
    """
    POST /api/analyze
    Accepts an audio file (and optional grid params), runs drum analysis,
    and returns a quantised grid pattern matching the frontend format.
    """

    def post(self, request):
        serializer = AudioAnalyzeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Invalid request data',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        audio_file = serializer.validated_data['audio_file']
        grid_size = serializer.validated_data['grid_size']
        bar_count = serializer.validated_data['bar_count']
        start_time = serializer.validated_data.get('start_time')
        end_time = serializer.validated_data.get('end_time')

        analysis_id = str(uuid.uuid4())
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)

        file_path = os.path.join(upload_dir, f"{analysis_id}_{audio_file.name}")

        try:
            with open(file_path, 'wb+') as dest:
                for chunk in audio_file.chunks():
                    dest.write(chunk)

            logger.info(f"Analysis {analysis_id}: grid={grid_size}, bars={bar_count}")

            # Optional trimming
            audio_to_analyze = file_path
            if start_time is not None and end_time is not None:
                audio_to_analyze = self._trim(file_path, start_time, end_time, processed_dir)

            # Drum onset classification — try Demucs, fall back to band filtering
            drum_onsets, method = self._classify_drums(audio_to_analyze, processed_dir)

            # Tempo estimation
            tempo = self._get_tempo(audio_to_analyze)

            logger.info(
                f"  method={method}, tempo={tempo:.1f}, "
                f"kicks={len(drum_onsets['kick'])}, "
                f"snares={len(drum_onsets['snare'])}, "
                f"hihats={len(drum_onsets['hihat'])}"
            )

            # Quantise to grid (produces the shape DrumDissect expects)
            from audio_processing.quantizer import build_pattern_response
            pattern = build_pattern_response(drum_onsets, tempo, grid_size, bar_count)

            return Response({
                'status': 'success',
                'analysis_id': analysis_id,
                'method': method,
                'pattern': pattern,
            }, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(f"Analysis failed: {exc}", exc_info=True)
            return Response({
                'status': 'error',
                'message': f'Analysis failed: {exc}',
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        finally:
            self._cleanup(file_path, processed_dir)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _trim(file_path: str, start: float, end: float, out_dir: str) -> str:
        from audio_processing.utils import trim_audio

        trimmed_path = os.path.join(out_dir, f"trimmed_{os.path.basename(file_path)}.wav")
        trim_audio(file_path, trimmed_path, start, end)
        return trimmed_path

    @staticmethod
    def _classify_drums(audio_path: str, processed_dir: str):
        """
        Try Demucs stem separation + onset/classification pipeline.
        On ImportError fall back to frequency-band analysis.
        """
        try:
            from audio_processing.stem_separator import separate_stems
            from audio_processing.onset_detector import analyze_drum_pattern
            from audio_processing.drum_classifier import classify_drum_pattern

            stems_dir = os.path.join(processed_dir, "stems")
            stem_paths = separate_stems(audio_path, stems_dir)
            drum_stem = stem_paths.get("drums")

            if not drum_stem or not os.path.exists(drum_stem):
                raise RuntimeError("Drum stem not produced")

            analysis = analyze_drum_pattern(drum_stem)
            onset_times = analysis["onset_times"]
            drum_pattern = classify_drum_pattern(drum_stem, onset_times)
            return drum_pattern, "demucs"

        except (ImportError, RuntimeError) as exc:
            logger.warning(f"Demucs unavailable ({exc}), using band-analyzer fallback")
            from audio_processing.band_analyzer import analyze_by_frequency_bands
            return analyze_by_frequency_bands(audio_path), "band_filter"

    @staticmethod
    def _get_tempo(audio_path: str) -> float:
        try:
            from audio_processing.band_analyzer import get_tempo_from_audio
            return get_tempo_from_audio(audio_path)
        except Exception:
            return 120.0

    @staticmethod
    def _cleanup(*paths):
        import shutil
        for p in paths:
            try:
                if os.path.isdir(p):
                    for child in os.listdir(p):
                        child_path = os.path.join(p, child)
                        if os.path.isdir(child_path):
                            shutil.rmtree(child_path, ignore_errors=True)
                elif os.path.isfile(p):
                    os.remove(p)
            except OSError:
                pass
