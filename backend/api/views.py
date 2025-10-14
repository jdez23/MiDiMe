import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import FileUploadSerializer


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
