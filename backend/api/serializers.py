from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    """Serializer for audio file uploads."""
    audio_file = serializers.FileField()
    
    def validate_audio_file(self, value):
        """
        Validate the uploaded file.
        
        Args:
            value: The uploaded file
            
        Returns:
            The validated file
            
        Raises:
            ValidationError: If file is invalid
        """
        # Check file size (max 50MB for MVP)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is 50MB. Your file is {value.size / (1024*1024):.2f}MB."
            )
        
        # Check file extension
        allowed_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
        file_ext = value.name.lower()
        if not any(file_ext.endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        return value
