from django.urls import path
from .views import FileUploadView, HealthCheckView, AudioAnalyzeView

urlpatterns = [
    path('upload', FileUploadView.as_view(), name='file-upload'),
    path('health', HealthCheckView.as_view(), name='health-check'),
    path('analyze', AudioAnalyzeView.as_view(), name='audio-analyze'),
]
