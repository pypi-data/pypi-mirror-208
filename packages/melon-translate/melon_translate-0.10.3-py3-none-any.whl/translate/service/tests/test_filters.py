import pytest


class TestFilters:
    @pytest.mark.filter
    def test_translation_melon_filter(self, translation_factory):
        """
        Test for filtering Translations that have keys with valid by convention snake_names, not randomly generated ones
        """
        from translate.service import admin
        from translate.service.filters import (
            FILTER_TRANSLATIONS_MELON,
            IgnoreMimoTranslationsFilter,
        )
        from translate.service.models import Translation

        obj, _, _ = translation_factory

        parameter_name = IgnoreMimoTranslationsFilter.parameter_name

        translation_filter_melon = IgnoreMimoTranslationsFilter(
            None,
            {parameter_name: FILTER_TRANSLATIONS_MELON},
            Translation,
            admin.TranslationAdmin,
        )

        melon_obj_qs = translation_filter_melon.queryset(None, None)
        values_list = melon_obj_qs.values_list("id", flat=True)

        assert melon_obj_qs
        assert obj.id in values_list

    @pytest.mark.filter
    def test_translation_mimo_filter(self, translation_mimo_factory):
        """
        Test for filtering Translations that are connected with keys that have randomly generated snake_name_UUID
        """
        from translate.service import admin
        from translate.service.filters import (
            FILTER_TRANSLATIONS_MIMO,
            IgnoreMimoTranslationsFilter,
        )
        from translate.service.models import Translation

        obj, _, _ = translation_mimo_factory
        parameter_name = IgnoreMimoTranslationsFilter.parameter_name

        translation_filter_mimo = IgnoreMimoTranslationsFilter(
            None,
            {parameter_name: FILTER_TRANSLATIONS_MIMO},
            Translation,
            admin.TranslationAdmin,
        )

        mimo_obj_qs = translation_filter_mimo.queryset(None, None)
        values_list = mimo_obj_qs.values_list("id", flat=True)

        assert mimo_obj_qs
        assert obj.id in values_list

    @pytest.mark.filter
    def test_translation_key_filter(self, translation_key_factory):
        """
        Test for filtering TranslationKeys that have keys with snake_names valid by convention i.e. melon keys
        """
        from translate.service import admin
        from translate.service.filters import FILTER_KEYS_MELON, IgnoreMimoKeysFilter
        from translate.service.models import TranslationKey

        translation_key = translation_key_factory
        parameter_name = IgnoreMimoKeysFilter.parameter_name

        translation_key_melon_filter = IgnoreMimoKeysFilter(
            None, {parameter_name: FILTER_KEYS_MELON}, TranslationKey, admin.TranslationKeyAdmin
        )

        melon_obj_qs = translation_key_melon_filter.queryset(None, None)
        values_list = melon_obj_qs.values_list("id", flat=True)
        assert melon_obj_qs
        assert translation_key.id in values_list

    @pytest.mark.filter
    def test_translation_key_mimo_filter(self, translation_key_mimo_factory):
        """
        Test for filtering TranslationKeys that are connected with legacy keys that have randomly generated snake_names
        """
        from translate.service import admin
        from translate.service.filters import FILTER_KEYS_MIMO, IgnoreMimoKeysFilter
        from translate.service.models import TranslationKey

        translation_key = translation_key_mimo_factory
        parameter_name = IgnoreMimoKeysFilter.parameter_name

        translation_key_mimo_filter = IgnoreMimoKeysFilter(
            None,
            {parameter_name: FILTER_KEYS_MIMO},
            TranslationKey,
            admin.TranslationKeyAdmin,
        )

        mimo_obj_qs = translation_key_mimo_filter.queryset(None, None)
        values_list = mimo_obj_qs.values_list("id", flat=True)

        assert mimo_obj_qs
        assert translation_key.id in values_list

    @pytest.mark.filter
    def test_context_input_filter(self, translation_key_with_context_factory):
        """
        Test for filtering TranslationKeys based on usage context input
        """
        from translate.service import admin
        from translate.service.filters import (
            FILTER_CONTEXT,
            FILTER_NO_CONTEXT,
            ContextInputFilter,
        )
        from translate.service.models import TranslationKey

        tk_list = translation_key_with_context_factory
        parameter_name = ContextInputFilter.parameter_name

        # NOTE: Since context field is recently added, and its empty across db,
        # we bypassed getting keys with context with new factory

        context_filter = ContextInputFilter(
            None,
            {parameter_name: FILTER_CONTEXT},
            TranslationKey,
            admin.TranslationKeyAdmin,
        )

        context_obj_qs = context_filter.queryset(None, None).filter(id__in=[tk.id for tk in tk_list])
        values_context_list = context_obj_qs.values_list("id", flat=True)

        assert context_obj_qs

        for tk in tk_list:
            assert tk.id in values_context_list

        assert context_obj_qs.count() == len(tk_list), "Unexpected number of keys with context"
        assert set(values_context_list) == set([tk.id for tk in tk_list]), "Unexpected keys with context"

        # Testing filters for keys with no context
        no_context_filter = ContextInputFilter(
            None,
            {parameter_name: FILTER_NO_CONTEXT},
            TranslationKey,
            admin.TranslationKeyAdmin,
        )

        no_context_obj = no_context_filter.queryset(None, None)

        # Assert that there are no TranslationKeys with context
        assert no_context_obj.filter(usage_context__isnull=False).count() == 0, "Unexpected keys with context"
