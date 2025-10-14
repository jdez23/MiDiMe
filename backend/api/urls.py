from django.urls import path
from .views import FileUploadView, HealthCheckView

urlpatterns = [
    path('upload', FileUploadView.as_view(), name='file-upload'),
    path('health', HealthCheckView.as_view(), name='health-check'),
]
