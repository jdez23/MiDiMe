from rest_framework import serializers


class FileUploadSerializer(serializers.Serializer):
    """Serializer for audio file uploads."""
    audio_file = serializers.FileField()

    def validate_audio_file(self, value):
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is 50MB. "
                f"Your file is {value.size / (1024*1024):.2f}MB."
            )

        allowed_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )

        return value


class AudioAnalyzeSerializer(serializers.Serializer):
    """Serializer for drum analysis requests."""
    audio_file = serializers.FileField()
    grid_size = serializers.ChoiceField(
        choices=[8, 16, 32], default=16, required=False
    )
    bar_count = serializers.ChoiceField(
        choices=[1, 2, 4], default=2, required=False
    )
    start_time = serializers.FloatField(min_value=0.0, required=False, default=None)
    end_time = serializers.FloatField(min_value=0.0, required=False, default=None)

    def validate_audio_file(self, value):
        max_size = 50 * 1024 * 1024
        if value.size > max_size:
            raise serializers.ValidationError(
                f"File size too large. Maximum size is 50MB. "
                f"Your file is {value.size / (1024*1024):.2f}MB."
            )

        allowed_extensions = ['.mp3', '.wav', '.flac', '.m4a', '.ogg']
        if not any(value.name.lower().endswith(ext) for ext in allowed_extensions):
            raise serializers.ValidationError(
                f"Unsupported file format. Allowed: {', '.join(allowed_extensions)}"
            )

        return value

    def validate(self, data):
        start = data.get('start_time')
        end = data.get('end_time')

        if start is not None and end is not None:
            if end <= start:
                raise serializers.ValidationError(
                    {'end_time': 'End time must be greater than start time.'}
                )
            duration = end - start
            if duration > 300:
                raise serializers.ValidationError(
                    {'end_time': f'Duration too long: {duration:.1f}s. Maximum is 5 minutes.'}
                )
        elif (start is None) != (end is None):
            raise serializers.ValidationError(
                'Provide both start_time and end_time, or neither.'
            )

        data['grid_size'] = int(data.get('grid_size', 16))
        data['bar_count'] = int(data.get('bar_count', 2))

        return data
