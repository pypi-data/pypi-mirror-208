import pytest


class TestLanguageSerializer:
    """Tests for ``Language`` model serializer."""

    @pytest.mark.serializer
    def test_serialization_expected_fields(self, language_factory):
        """Check expected fields after serializing ``Language`` model."""
        from translate.service.serializers import LanguageSerializer

        serializer = LanguageSerializer(language_factory)
        assert {"lang_info", "id"} == set(serializer.data)
        assert serializer.data.get("lang_info")
        assert serializer.data.get("id")

    @pytest.mark.serializer
    def test_deserialization_expected_fields(self, language_provider):
        """Check model instance creation and validation through serializer."""
        from translate.service.serializers import LanguageSerializer

        serializer = LanguageSerializer(data=language_provider.language())
        assert serializer.is_valid(raise_exception=True), "All provided fields should be valid"
        assert {"lang_info"} == set(serializer.validated_data)
        assert {"bidi", "code", "name", "name_local"} == set(serializer.validated_data.get("lang_info"))
        assert serializer.validated_data.get("lang_info").get("code") == "en"

    @pytest.mark.serializer
    def test_deserialization_create(self, language_provider):
        """Check deserialization for ``Language`` model."""
        from translate.service.models import Language
        from translate.service.serializers import LanguageSerializer

        serializer = LanguageSerializer(data=language_provider.language())
        assert serializer.is_valid(raise_exception=True)

        obj, created = serializer.save()
        assert obj and obj.id

        obj_reloaded = Language.objects.get(id=obj.id)
        assert obj_reloaded and obj_reloaded.id
        assert obj_reloaded.lang_info == obj.lang_info


class TestTranslationKeySerializer:
    """Tests for ``TranslationKey`` model serializer."""

    @pytest.mark.serializer
    def test_serialization_expected_fields(self, translation_key_factory):
        """Check expected fields after serializing ``TranslationKey`` model."""
        from translate.service.serializers import TranslationKeySerializer

        serializer = TranslationKeySerializer(translation_key_factory)
        for element in {"snake_name", "category", "usage_context", "id"}:
            assert element in set(serializer.data)

        assert serializer.data.get("snake_name")
        assert isinstance(serializer.data.get("category"), str)
        assert serializer.data.get("category")
        assert serializer.data.get("usage_context") is None
        assert serializer.data.get("id")

    @pytest.mark.serializer
    def test_deserialization_expected_fields(self, translation_key_provider):
        """Check model instance creation and validation through serializer."""
        from translate.service.serializers import TranslationKeySerializer

        serializer = TranslationKeySerializer(data=translation_key_provider.snake_key())

        assert serializer.is_valid(raise_exception=True)

        assert {"snake_name", "category", "usage_context", "id_name", "views"} == set(serializer.validated_data.keys())
        assert isinstance(serializer.validated_data.get("snake_name"), str)
        assert isinstance(serializer.validated_data.get("category"), int)
        assert isinstance(serializer.validated_data.get("usage_context"), str)
        assert isinstance(serializer.validated_data.get("id_name"), str)
        assert isinstance(serializer.validated_data.get("views"), list)

    @pytest.mark.serializer
    def test_deserialization_create(self, translation_key_provider):
        """Check deserialization for ``TranslationKey``."""
        from translate.service.models import TranslationKey
        from translate.service.serializers import TranslationKeySerializer

        serializer = TranslationKeySerializer(data=translation_key_provider.snake_key())
        assert serializer.is_valid(raise_exception=True)

        obj, created = serializer.save()
        assert obj and obj.id

        obj_reloaded = TranslationKey.objects.get(id=obj.id)
        assert obj_reloaded and obj_reloaded.id


class TestTranslationSerializer:
    """Tests for ``Translation`` model serializer."""

    @pytest.mark.serializer
    def test_serialization_expected_fields(self, translation_factory):
        """Check expected fields after serializing ``Translation`` model."""
        from translate.service.serializers import TranslationSerializer

        translation, *_ = translation_factory
        serializer = TranslationSerializer(translation)
        for element in {"translation", "language", "key", "id"}:
            assert element in set(serializer.data)

        # NOTE: Check that read-only fields are populated as expected.
        assert serializer.data.get("id")
        assert serializer.data.get("translation")
        assert serializer.data.get("language")
        assert serializer.data.get("key")
        # NOTE: Assert that we didn't get any additional keys.
        assert set(serializer.data.keys()) == {"id", "language", "key", "translation"}

    @pytest.mark.serializer
    def test_deserialization_expected_fields(self, translation_provider, language_factory, translation_key_factory):
        """Check deserialization"""
        from translate.service.serializers import TranslationSerializer

        serializer = TranslationSerializer(
            data=translation_provider.translation(language_factory, translation_key_factory)
        )

        assert serializer.is_valid(raise_exception=True)

        for element in {"key", "language", "translation"}:
            assert element in set(serializer.validated_data.keys())

        assert isinstance(serializer.validated_data.pop("translation"), str)
        assert isinstance(serializer.validated_data.pop("language"), dict)
        assert isinstance(serializer.validated_data.pop("key"), dict)

    @pytest.mark.serializer
    def test_deserialization_create(self, translation_provider, language_factory, translation_key_factory):
        """Check deserialization for ``TranslationSerializer``."""
        from translate.service.models import Translation
        from translate.service.serializers import TranslationSerializer

        data = translation_provider.translation(language_factory, translation_key_factory)

        serializer = TranslationSerializer(data=data)

        assert serializer.is_valid(raise_exception=True)

        obj, created = serializer.save()
        assert created
        assert obj and obj.id

        obj_reloaded = Translation.objects.get(id=obj.id)
        assert obj_reloaded and obj_reloaded.id and obj_reloaded.translation == obj.translation


class TestLivelinessCheckSerializer:
    """Tests for liveliness serializer."""

    def test_read(self):
        """Test reading default data."""
        from translate.service.serializers import LivelinessCheckSerializer

        assert LivelinessCheckSerializer().data == {"status": LivelinessCheckSerializer.LIVELINESS_DEFAULT_STATUS}


class TestReadinessCheckSerializer:
    """Tests for readiness serializer."""

    def test_read(self, readiness_provider):
        """Test reading default data."""
        from translate.service.serializers import ReadinessCheckSerializer

        data = ReadinessCheckSerializer(readiness_provider.health_check()).data

        assert data.pop("celery_backend") == "unavailable: Unknown error"
        assert data.pop("cache_backend") == "working"
        assert data.pop("database_backend") == "working"
        assert data.pop("fs_file_storage") == "working"
        assert data.pop("disk_usage") == "working"
        assert data.pop("memory_usage") == "working"
        assert data.pop("migrations_check") == "working"
        assert data.pop("redis_backend") == "working"

        # NOTE: Assert that only above values are contained.
        assert set(data) == set()


class TestRequestSerializer:
    """Test request serialization"""

    def test_request_serialization(self, request_serializer_fixture):

        serializer = request_serializer_fixture

        assert serializer.is_valid()
        assert serializer.validated_data
        assert isinstance(serializer.validated_data.get("language").get("code"), str)
        assert isinstance(serializer.validated_data.get("views"), list)
        assert isinstance(serializer.validated_data.get("occurrences"), list)
        assert isinstance(serializer.validated_data.get("snake_keys"), list)
