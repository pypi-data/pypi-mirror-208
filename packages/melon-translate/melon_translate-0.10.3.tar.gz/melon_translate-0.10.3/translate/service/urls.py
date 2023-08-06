from django.urls import path, re_path

from translate.service.views import (
    LivelinessCheckView,
    ReadinessCheckView,
    TranslationsAPIView,
)

urlpatterns = [
    path("translations/<language>/", TranslationsAPIView.as_view(), name="api_translations"),
    path("status/liveliness", LivelinessCheckView.as_view(), name="status_liveliness"),
    path("status/readiness", ReadinessCheckView.as_view(), name="status_readiness"),
]
