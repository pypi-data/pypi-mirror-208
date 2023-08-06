import pytest
from django.conf.locale import LANG_INFO


class TestTranslationModel:
    """Tests for ``Translation`` model."""

    @pytest.mark.model
    def test_translation_create(self, translation_factory):
        """Check creation of translation record."""
        from translate.service.models import Translation

        translation, language, translation_key = translation_factory

        # NOTE: Reload from database to ensure that record is stored.
        record = Translation.objects.get(id=translation.id)
        assert translation.translation == record.translation

        assert record.key.snake_name
        assert record.language.lang_info in LANG_INFO

    @pytest.mark.model
    def test_language_create(self, language_factory):
        """Check creation of language record."""
        from translate.service.models import Language

        # NOTE: Reload from database to ensure that record is stored.
        record = Language.objects.get(id=language_factory.id)
        assert record.lang_info in LANG_INFO

    @pytest.mark.model
    def test_translation_key_create(self, translation_key_factory):
        """Check creation of language key record."""
        from translate.service.models import TranslationKey as Tk

        # NOTE: Reload from database to ensure that record is stored.
        record = Tk.objects.get(id=translation_key_factory.id)

        assert record.snake_name
        assert record.category == Tk.Category.SERVICE.value
        assert record.usage_context is None

    def test_translations_ordering(self, make_request, import_german_translations_fixture):
        from translate.service.models import Translation
        from translate.service.views import TranslationsAPIView

        kwargs = {"language": "de"}
        request = make_request(f"get::api_translations", kwargs=kwargs)
        response = TranslationsAPIView.as_view()(request, **kwargs)

        results = response.data.get("results")
        first_item_id = results[0].get("id")
        first = Translation.objects.get(id=first_item_id)

        last_item_id = results[-1].get("id")
        last = Translation.objects.get(id=last_item_id)

        assert first.modified > last.modified, "First item should be last modified translation object"
