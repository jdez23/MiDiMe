import os
import logging
import uuid
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer, AudioAnalyzeSerializer
from audio_processing.audio_service import process_audio_snippet
from audio_processing.onset_detector import analyze_drum_pattern
from audio_processing.drum_classifier import classify_drum_pattern
from audio_processing.midi_converter import convert_pattern_to_json

logger = logging.getLogger(__name__)


class FileUploadView(APIView):
    """
    API endpoint for uploading audio files.
    
    POST /api/upload
    Accepts an audio file and returns filename and file size.
    """
    
    def post(self, request):
        """
        Handle file upload.
        
        Args:
            request: HTTP request containing the audio file
            
        Returns:
            JSON response with file information or error message
        """
        serializer = FileUploadSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                audio_file = serializer.validated_data['audio_file']
                
                # Save file to uploads directory
                upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
                os.makedirs(upload_dir, exist_ok=True)
                
                file_path = os.path.join(upload_dir, audio_file.name)
                
                # Write file to disk
                with open(file_path, 'wb+') as destination:
                    for chunk in audio_file.chunks():
                        destination.write(chunk)
                
                # Get file size in MB
                file_size_mb = audio_file.size / (1024 * 1024)
                
                return Response({
                    'status': 'success',
                    'message': 'File uploaded successfully',
                    'data': {
                        'filename': audio_file.name,
                        'file_size': f"{file_size_mb:.2f} MB",
                        'file_size_bytes': audio_file.size
                    }
                }, status=status.HTTP_200_OK)
                
            except Exception as e:
                return Response({
                    'status': 'error',
                    'message': f'Error saving file: {str(e)}'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'status': 'error',
            'message': 'Invalid file',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


class HealthCheckView(APIView):
    """
    Health check endpoint.

    GET /api/health
    Returns the health status of the API.
    """

    def get(self, request):
        """Return health status."""
        from datetime import datetime
        return Response({
            'status': 'healthy',
            'timestamp': datetime.now().isoformat() + 'Z'
        }, status=status.HTTP_200_OK)


class AudioAnalyzeView(APIView):
    """
    API endpoint for analyzing audio snippets and extracting musical patterns.

    POST /api/analyze
    Accepts an audio file, time range, and instrument type.
    Returns MIDI pattern data with onset timings.
    """

    def post(self, request):
        """
        Analyze an audio snippet and return pattern data.

        Args:
            request: HTTP request containing:
                - audio_file: Audio file (MP3, WAV, FLAC, M4A, OGG)
                - start_time: Start time in seconds
                - end_time: End time in seconds
                - instrument: Instrument type (drums, bass, chords, melody)

        Returns:
            JSON response with MIDI pattern data or error message
        """
        serializer = AudioAnalyzeSerializer(data=request.data)

        if not serializer.is_valid():
            return Response({
                'status': 'error',
                'message': 'Invalid request data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        # Extract validated data
        audio_file = serializer.validated_data['audio_file']
        start_time = serializer.validated_data['start_time']
        end_time = serializer.validated_data['end_time']
        instrument = serializer.validated_data['instrument']

        # Generate unique ID for this analysis
        analysis_id = str(uuid.uuid4())

        # Setup paths
        upload_dir = os.path.join(settings.MEDIA_ROOT, 'uploads')
        processed_dir = os.path.join(settings.MEDIA_ROOT, 'processed')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)

        # Save uploaded file temporarily
        file_path = os.path.join(upload_dir, f"{analysis_id}_{audio_file.name}")

        try:
            # Write uploaded file to disk
            with open(file_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)

            logger.info(f"Starting analysis {analysis_id}: {instrument} from {start_time}s to {end_time}s")

            # Currently only drums are fully implemented
            if instrument != 'drums':
                return Response({
                    'status': 'error',
                    'message': f'{instrument.capitalize()} analysis not yet implemented. Only drums are supported in MVP.'
                }, status=status.HTTP_501_NOT_IMPLEMENTED)

            # Step 1: Process audio snippet (trim + stem separation)
            result = process_audio_snippet(
                audio_path=file_path,
                start_time_seconds=start_time,
                end_time_seconds=end_time,
                output_base_dir=processed_dir,
                extract_stems=True,
                cleanup_after=True
            )

            if not result.success:
                return Response({
                    'status': 'error',
                    'message': 'Audio processing failed',
                    'error': result.error
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Get drum stem path
            drum_stem_path = result.stem_paths.get('drums')

            if not drum_stem_path or not os.path.exists(drum_stem_path):
                return Response({
                    'status': 'error',
                    'message': 'Failed to extract drum stem'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            logger.info(f"Drum stem extracted: {drum_stem_path}")

            # Step 2: Analyze drum pattern (onset detection)
            pattern_analysis = analyze_drum_pattern(drum_stem_path)
            onset_times = pattern_analysis['onset_times']
            tempo = pattern_analysis['tempo_bpm']

            logger.info(f"Detected {len(onset_times)} onsets at {tempo:.1f} BPM")

            # Step 3: Classify drums (kick/snare/hihat)
            drum_pattern = classify_drum_pattern(drum_stem_path, onset_times)

            logger.info(
                f"Classification: {len(drum_pattern['kick'])} kicks, "
                f"{len(drum_pattern['snare'])} snares, "
                f"{len(drum_pattern['hihat'])} hi-hats"
            )

            # Step 4: Convert to JSON format for frontend
            midi_json = convert_pattern_to_json(drum_pattern, tempo)

            # Step 5: Cleanup temporary files
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                if os.path.exists(drum_stem_path):
                    os.remove(drum_stem_path)
                # Cleanup parent directory if empty
                stem_parent_dir = os.path.dirname(drum_stem_path)
                if os.path.exists(stem_parent_dir) and not os.listdir(stem_parent_dir):
                    os.rmdir(stem_parent_dir)
            except OSError as e:
                logger.warning(f"Cleanup warning: {e}")

            # Build response
            return Response({
                'status': 'success',
                'analysis_id': analysis_id,
                'instrument': instrument,
                'duration': end_time - start_time,
                'midi_data': midi_json['midi_data'],
                'tempo': midi_json['tempo'],
                'time_signature': midi_json['time_signature'],
                'metadata': {
                    **midi_json['metadata'],
                    'snippet_duration_seconds': result.metadata.get('snippet_duration_seconds'),
                    'sample_rate': result.metadata.get('sample_rate'),
                    'hit_density': pattern_analysis['hit_density']
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}", exc_info=True)

            # Cleanup on error
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except OSError:
                pass

            return Response({
                'status': 'error',
                'message': f'Analysis failed: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
