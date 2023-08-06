from django.conf.locale import LANG_INFO
from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from translate.service.models import Language, Translation, TranslationKey


class LanguageField(serializers.Field):
    """Custom language field serializer."""

    def to_internal_value(self, value) -> dict:
        """Override interface."""
        if not isinstance(value, str):
            raise ValidationError("invalid `lang_info` type")

        data = LANG_INFO.get(value)
        if not data:
            raise ValidationError("invalid `lang_info` - no metadata found")

        fallback = data.get("fallback")
        if fallback:
            data = LANG_INFO.get(fallback.pop())

        return data

    def to_representation(self, value):
        """Override interface"""
        return LANG_INFO.get(value)


class LanguageSerializer(serializers.ModelSerializer):
    """Language model serializer."""

    lang_info = LanguageField()

    class Meta:
        model = Language
        fields = [
            "id",
            "lang_info",
        ]

    def validate_lang_info(self, value: dict) -> dict:
        """Check lang_info and return metadata."""
        if not isinstance(value, dict) or not value.get("code"):
            raise ValidationError("invalid `lang_info` type")

        return value

    def validate(self, data) -> dict:
        """Object level validation."""
        return data

    def create(self, validated_data) -> Language:
        """Create and return a new ``Translation`` instance for a given validated data."""
        code = validated_data.get("lang_info").get("code")

        if not code or code not in LANG_INFO:
            raise ValidationError("invalid language locale")

        return Language.objects.get_or_create(lang_info=code)


class CategoryField(serializers.ChoiceField):
    """Custom field for Category Choices"""

    def to_representation(self, value):
        _choice = self._choices.get(value)
        if not value and self.allow_blank:
            raise ValidationError("Category value should be provided.")
        return _choice

    def to_internal_value(self, data):
        if not data:
            return None
        return data


class TranslationKeySerializer(serializers.ModelSerializer):
    """TranslationKey model serializer."""

    category = CategoryField(choices=TranslationKey.Category.choices, default=0)

    class Meta:
        model = TranslationKey
        fields = [
            "id",
            "usage_context",
            "category",
            "snake_name",
            "id_name",
            "views",
            "flags",
            "occurrences",
        ]

    def validate_snake_name(self, value) -> dict:
        """Check snake name."""
        if not value:
            raise ValidationError("invalid ``snake_name``")

        return value

    def validate(self, data) -> dict:
        """Object level validation."""
        return dict(data)

    def create(self, validated_data) -> "TranslationKey":
        """Create and return a new ``TranslationKey`` instance for a given validated data."""
        return TranslationKey.objects.get_or_create(**validated_data)


class TranslationSerializer(serializers.Serializer):
    """Translation model serializer."""

    id = serializers.UUIDField(read_only=True)
    language = LanguageSerializer()
    key = TranslationKeySerializer()
    translation = serializers.CharField()

    class Meta:
        model = Translation
        fields = [
            "id",
            "language",
            "key",
            "translation",
        ]

    def validate(self, data: dict) -> dict:
        """Object level validation."""
        return dict(data)

    def create(self, validated_data):
        """Create and return a new ``Translation`` instance for a given validated data."""
        translation_key = validated_data.pop("key")
        language = validated_data.pop("language").pop("lang_info")

        with transaction.atomic():
            key, _ = TranslationKey.objects.get_or_create(snake_name=translation_key.get("snake_name"))
            language, _ = Language.objects.get_or_create(lang_info=language.get("code"))

            return Translation.objects.get_or_create(
                language=language, key=key, translation=validated_data.get("translation")
            )


class TranslationRequestSerializer(serializers.Serializer):

    language = LanguageField(required=True)

    views = serializers.ListField(child=serializers.CharField(), required=False, default=[])
    occurrences = serializers.ListField(child=serializers.CharField(), required=False, default=[])
    snake_keys = serializers.ListField(child=serializers.CharField(), required=False, default=[])

    page = serializers.IntegerField(required=False, allow_null=True)
    page_size = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data) -> dict:
        """Object level validation."""
        return dict(data)


class MelonSerializer(serializers.Serializer):
    """Melon parent serializer."""

    def update(self, instance, validated_data):
        """Override default update field."""
        pass

    def create(self, validated_data):
        """Override default create field."""
        pass


class LivelinessCheckSerializer(MelonSerializer):
    """Liveliness check serializer."""

    LIVELINESS_DEFAULT_STATUS = "ok"

    status = serializers.CharField(initial=LIVELINESS_DEFAULT_STATUS)


class ReadinessCheckSerializer(MelonSerializer):
    """Readiness check serializer."""

    cache_backend = serializers.CharField(source="Cache backend: default", read_only=True)
    celery_backend = serializers.CharField(source="CeleryHealthCheckCelery", read_only=True)
    database_backend = serializers.CharField(source="DatabaseBackend", read_only=True)
    fs_file_storage = serializers.CharField(source="DefaultFileStorageHealthCheck", read_only=True)
    disk_usage = serializers.CharField(source="DiskUsage", read_only=True)
    memory_usage = serializers.CharField(source="MemoryUsage", read_only=True)
    migrations_check = serializers.CharField(source="MigrationsHealthCheck", read_only=True)
    redis_backend = serializers.CharField(source="RedisHealthCheck", read_only=True)
