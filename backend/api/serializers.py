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


class AudioAnalyzeSerializer(serializers.Serializer):
    """Serializer for audio analysis requests."""
    audio_file = serializers.FileField()
    start_time = serializers.FloatField(min_value=0.0)
    end_time = serializers.FloatField(min_value=0.0)
    instrument = serializers.ChoiceField(
        choices=['drums', 'bass', 'chords', 'melody'],
        default='drums'
    )

    def validate_audio_file(self, value):
        """Validate the uploaded audio file."""
        # Check file size (max 50MB)
        max_size = 50 * 1024 * 1024
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

    def validate(self, data):
        """Validate the time range."""
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if end_time <= start_time:
            raise serializers.ValidationError({
                'end_time': 'End time must be greater than start time.'
            })

        duration = end_time - start_time

        # Validate duration constraints (15-90 seconds for MVP)
        if duration < 15:
            raise serializers.ValidationError({
                'end_time': f'Duration too short: {duration:.1f}s. Minimum is 15 seconds.'
            })

        if duration > 90:
            raise serializers.ValidationError({
                'end_time': f'Duration too long: {duration:.1f}s. Maximum is 90 seconds for free tier.'
            })

        return data
