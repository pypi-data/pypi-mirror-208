from django.apps import AppConfig


class ServiceConfig(AppConfig):
    """Translation service configuration."""

    app_label = "translate_service"
    name = "translate.service"
