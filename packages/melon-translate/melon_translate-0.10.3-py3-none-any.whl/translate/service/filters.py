from baton.admin import SimpleDropdownFilter
from django_admin_inline_paginator.admin import TabularInlinePaginated

from translate.service.models import Translation, TranslationKey

FILTER_TRANSLATIONS_MIMO = "mimo"
FILTER_TRANSLATIONS_MELON = "melon"
FILTER_KEYS_MIMO = "mimo-keys"
FILTER_KEYS_MELON = "melon-keys"
FILTER_CONTEXT = "context-inserted"
FILTER_NO_CONTEXT = "context-not-inserted"


class TranslationInline(TabularInlinePaginated):
    fields = ("translation", "translation_plural", "language")
    per_page = 7
    model = Translation


class IgnoreMimoTranslationsFilter(SimpleDropdownFilter):
    """
    This is a filter for filtering translations by heritage. Mimo translations are old
    translations, used in legacy codebase, and melon are new and currently used ones.
    """

    title = "Ignoring mimo translations"
    parameter_name = "mimo"

    def lookups(self, request, model_admin):
        return (
            (FILTER_TRANSLATIONS_MIMO, "Old mimo translations"),
            (FILTER_TRANSLATIONS_MELON, "New translations"),
        )

    def queryset(self, request, queryset):
        if self.value() == FILTER_TRANSLATIONS_MIMO:
            return Translation.objects.filter(key__snake_name__startswith="snake_name_").order_by("-modified")
        if self.value() == FILTER_TRANSLATIONS_MELON:
            return Translation.objects.exclude(key__snake_name__startswith="snake_name_").order_by("-modified")


class IgnoreMimoKeysFilter(SimpleDropdownFilter):
    """
    This is a filter for filtering keys by heritage. Mimo translation keys are old
    translations, used in legacy codebase, and melon are new and currently used ones.
    """

    title = "Ignoring mimo keys"
    parameter_name = "mimo-keys"

    def lookups(self, request, model_admin):
        return [
            (FILTER_KEYS_MIMO, "Old mimo translation keys"),
            (FILTER_KEYS_MELON, "New translation keys"),
        ]

    def queryset(self, request, queryset):
        if self.value() == FILTER_KEYS_MIMO:
            return TranslationKey.objects.filter(snake_name__startswith="snake_name_").order_by("-modified")
        if self.value() == FILTER_KEYS_MELON:
            return TranslationKey.objects.exclude(snake_name__startswith="snake_name_").order_by("-modified")


class ContextInputFilter(SimpleDropdownFilter):

    title = "context"
    parameter_name = "context-input"

    def lookups(self, request, model_admin):
        return [
            (FILTER_CONTEXT, "Inserted"),
            (FILTER_NO_CONTEXT, "Not inserted"),
        ]

    def queryset(self, request, queryset):
        if self.value() == FILTER_CONTEXT:
            return TranslationKey.objects.filter(usage_context__isnull=False).order_by("-modified")
        if self.value() == FILTER_NO_CONTEXT:
            return TranslationKey.objects.filter(usage_context__isnull=True).order_by("-modified")
