import random
import uuid
from typing import Any, Dict

from django.conf.locale import LANG_INFO
from faker.providers import BaseProvider


class TranslationProvider(BaseProvider):
    """Data provider for ``TranslationSerializer``."""

    def translation(self, language_factory, translation_key_factory) -> Dict[str, str]:
        """Translation data instance."""
        return {
            "language": {"lang_info": random.choice(list(LANG_INFO.keys()))},
            "key": {"snake_name": uuid.uuid1().hex, "category": 30},
            "translation": "my little translation",
        }


class LanguageProvider(BaseProvider):
    """Data provider for ``LanguageSerializer``."""

    def language(self) -> Dict[str, str]:
        """Language data instance."""
        return {
            "lang_info": "en",
        }


class TranslationKeyProvider(BaseProvider):
    """Data provider for ``TranslationKeySerializer``."""

    def snake_key(self) -> Dict[str, Any]:
        """Translation key data instance."""
        return {
            "snake_name": str(self.generator.name()).replace(" ", "_"),
            "category": 30,
            "usage_context": "context",
            "id": uuid.uuid4().hex,
            "id_name": "some id name",
            "views": ["TRANSLATION_CENTER_FRONTEND"],
        }


class ReadinessCheckProvider(BaseProvider):
    """Readiness response provider."""

    @staticmethod
    def health_check() -> dict:
        """Django health check provider."""
        data = {
            "Cache backend: default": "working",
            "CeleryHealthCheckCelery": "unavailable: Unknown error",
            "DatabaseBackend": "working",
            "DefaultFileStorageHealthCheck": "working",
            "DiskUsage": "working",
            "MemoryUsage": "working",
            "MigrationsHealthCheck": "working",
            "RedisHealthCheck": "working",
        }
        return data
