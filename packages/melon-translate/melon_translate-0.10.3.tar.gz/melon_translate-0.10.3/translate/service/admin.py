from django.contrib import admin
from django.db import models
from django.forms import TextInput

from translate.service.filters import (
    ContextInputFilter,
    IgnoreMimoKeysFilter,
    IgnoreMimoTranslationsFilter,
    TranslationInline,
)
from translate.service.models import Language, Translation, TranslationKey


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    """Admin registration for ``Translation``."""

    formfield_overrides = {models.TextField: {"widget": TextInput()}}
    search_fields = ("key__snake_name", "key__id_name", "translation")
    fields = ("translation", "translation_plural", "language")

    list_display = ("key", "translation", "translation_plural", "language")
    list_filter = (
        "language",
        ("translation", admin.EmptyFieldListFilter),
        "key__category",
        IgnoreMimoTranslationsFilter,
    )
    list_editable = ("translation", "translation_plural")
    list_per_page = 15

    save_on_top = True


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    """Admin registration for ``Language``."""

    list_display = ("lang_info",)
    save_on_top = True


@admin.register(TranslationKey)
class TranslationKeyAdmin(admin.ModelAdmin):
    """Admin registration for ``TranslationKey.``"""

    formfield_overrides = {models.TextField: {"widget": TextInput()}}
    fields = ("snake_name", "id_name", "usage_context", "category", "views", "occurrences")
    inlines = (TranslationInline,)
    search_fields = ("snake_name", "id_name")

    list_display = ("snake_name", "id_name", "usage_context", "category")
    list_filter = (
        "category",
        "created",
        "modified",
        IgnoreMimoKeysFilter,
        ContextInputFilter,
    )
    list_editable = ("id_name", "usage_context", "category")
    list_per_page = 15

    save_on_top = True
