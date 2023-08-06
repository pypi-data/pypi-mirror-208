import pytest
from django.urls import reverse
from rest_framework import status


class TestTranslationsView:
    """Test cases for translations View."""

    @pytest.mark.view
    def test_get(self, request_factory, import_german_translations_fixture):
        """Check view get method for getting all translations"""
        from translate.service.views import TranslationsAPIView

        kwargs = {"language": "de"}
        get_request = request_factory.get(reverse("api_translations", kwargs=kwargs))
        response = TranslationsAPIView.as_view()(get_request, **kwargs)

        assert response.status_code == status.HTTP_200_OK
        assert response.data


class TestLivelinessCheckView:
    """Test liveliness check view."""

    @pytest.mark.view
    def test_get(self, make_request):
        """Test liveliness check success for GET method."""

        from translate.service.views import LivelinessCheckView

        request = make_request(f"get::status_liveliness")
        response = LivelinessCheckView.as_view()(request)

        assert response and response.status_code == status.HTTP_200_OK
        assert set(response.data) == {"status"}


class TestReadinessCheckView:
    """Test readiness check view."""

    def test_get(self, make_request):
        """Test readiness check success for GET method."""

        from translate.service.views import ReadinessCheckView

        request = make_request(f"get::status_readiness")
        response = ReadinessCheckView.as_view()(request)

        assert response and response.status_code == status.HTTP_200_OK
        assert set(response.data) == {
            "migrations_check",
            "database_backend",
            "fs_file_storage",
            "cache_backend",
        }
