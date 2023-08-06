import time
import uuid
from enum import unique

from auditlog.registry import auditlog
from django.conf.locale import LANG_INFO
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.indexes import GinIndex
from django.db import models
from model_utils.models import TimeStampedModel, UUIDModel


class Language(TimeStampedModel, UUIDModel):
    """``Language`` records model."""

    lang_info = models.CharField(
        max_length=8,
        choices=[(lang, lang_info.get("name")) for lang, lang_info in LANG_INFO.items() if lang_info.get("name")],
        unique=True,
    )

    class Meta:
        verbose_name = "Language"
        verbose_name_plural = "Languages"

    def __str__(self):
        """String representation of ``Language``."""
        return LANG_INFO.get(self.lang_info).get("name") or self.lang_info


def default_snake_name() -> str:
    """Generate default snake name."""
    # return f"snake_name_{uuid.uuid1(time.time()).hex}"
    return f"snake_name_{uuid.uuid1().hex}"


class TranslationKey(TimeStampedModel, UUIDModel):
    """``TranslationKey`` records model."""

    @unique
    class Category(models.IntegerChoices):
        """``TranslationKey`` categories."""

        GENERAL = 0, "General"
        WEB = 10, "Web app"
        MOBILE = 20, "Mobile app"
        SERVICE = 30, "Microservice"

    category = models.PositiveSmallIntegerField(default=Category.GENERAL, choices=Category.choices)

    snake_name = models.CharField(unique=True, max_length=4096, default=default_snake_name)
    encoding = models.CharField(max_length=16, default="utf-8")
    usage_context = models.TextField(default=None, null=True, blank=True)

    # TODO: We cannot enforce uniqueness on database level here,
    #  therefore we should add additional checks during serialization.
    id_name = models.TextField(default=None, null=True, blank=True)
    id_name_plural = models.TextField(default=None, null=True, blank=True)

    occurrences = ArrayField(models.CharField(max_length=1024), size=32, default=None, null=True, blank=True)
    flags = ArrayField(models.CharField(max_length=1024), size=32, default=None, null=True, blank=True)
    views = ArrayField(models.CharField(max_length=1024), size=4096, default=None, null=True, blank=True)

    class Meta:
        verbose_name = "Translation Key"
        verbose_name_plural = "Translation Keys"
        indexes = [
            GinIndex(fields=["occurrences", "views"], name="occ_views_gin", fastupdate=False),
        ]

    def __str__(self):
        """String representation of ``TranslationKey``."""
        return self.snake_name


class Translation(TimeStampedModel, UUIDModel):
    """``Translation`` records model."""

    language = models.ForeignKey(
        Language,
        on_delete=models.RESTRICT,
        related_name="translations",
    )
    key = models.ForeignKey(
        TranslationKey,
        on_delete=models.RESTRICT,
        to_field="id",
        related_name="translation_keys",
    )

    translation = models.TextField()
    translation_plural = models.TextField()

    class Meta:
        verbose_name = "Translation"
        verbose_name_plural = "Translations"
        unique_together = (("language", "key"),)


auditlog.register(Translation)
auditlog.register(TranslationKey)
auditlog.register(Language)
