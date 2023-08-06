import uuid

import django
import pytest


@pytest.fixture
def readiness_provider(provider_to_fixture):
    """Readiness provider fixture."""
    from translate.service.tests.providers import ReadinessCheckProvider

    provider_to_fixture.add_provider(ReadinessCheckProvider)

    yield provider_to_fixture


@pytest.fixture
@pytest.mark.xdist_group(name="group_db")
def language_factory():
    """Language factory fixture."""
    from translate.service.models import Language
    from translate.service.tests.factories import LanguageFactory

    factory = LanguageFactory.build()

    obj, created = Language.objects.get_or_create(lang_info=factory.lang_info)
    yield obj

    counter = 0
    while created and obj.id:
        try:
            obj.delete()
        except (django.db.IntegrityError, django.db.models.deletion.RestrictedError, ValueError):
            counter += 1
            if counter > 3:
                break
            continue


@pytest.fixture(
    params=[
        "general_accept",
        "1another_one",
        "$my_translation",
        "my msgid " "%$#$@@#534",
    ],
)
@pytest.mark.xdist_group(name="group_db")
def translation_key_factory(request, language_factory):
    """``TranslationKey`` factory fixture."""
    from translate.service.models import TranslationKey as Tk
    from translate.service.tests.factories import TranslationKeyFactory

    factory = TranslationKeyFactory.build(
        snake_name=f"{request.param}_{uuid.uuid4().hex}",
        category=Tk.Category.SERVICE,
    )

    obj, created = Tk.objects.get_or_create(snake_name=factory.snake_name, category=factory.category)
    yield obj

    if created:
        obj.delete()


@pytest.fixture(
    params=[
        {
            "keys": [
                {
                    "key": "$my_context_key",
                    "usage_context": "$my_translation context",
                },
                {
                    "key": "and_1another_one",
                    "usage_context": "1another_one context",
                },
            ]
        },
    ],
)
def translation_key_with_context_factory(request):
    """``TranslationKey`` that have usage context inserted factory fixture."""
    from translate.service.models import TranslationKey as Tk
    from translate.service.tests.factories import TranslationKeyFactory

    tks = [
        TranslationKeyFactory.create(
            snake_name=f"{tk.get('key')}_{uuid.uuid4().hex}",
            category=Tk.Category.SERVICE,
            usage_context=tk.get("usage_context"),
        )
        for tk in request.param.get("keys")
    ]

    yield tks

    for tk in tks:
        tk.delete()


@pytest.fixture(
    params=[
        "snake_name_one",
        "snake_name_two2",
        "snake_name_%$#@%^&@",
    ],
)
def translation_key_mimo_factory(request):
    """``TranslationKey`` with mimo snake_names factory fixture."""
    from translate.service.models import TranslationKey as Tk
    from translate.service.tests.factories import TranslationKeyFactory

    tk = TranslationKeyFactory.create(
        snake_name=f"{request.param}_{uuid.uuid4().hex}",
        category=Tk.Category.SERVICE,
    )

    yield tk
    tk.delete()


@pytest.fixture
@pytest.mark.xdist_group(name="group_db")
def translation_factory(language_factory, translation_key_factory):
    """Translation factory fixture."""
    from translate.service.tests.factories import TranslationFactory

    obj = TranslationFactory.create(language=language_factory, key=translation_key_factory)

    yield obj, language_factory, translation_key_factory
    obj.delete()


@pytest.fixture
@pytest.mark.xdist_group(name="group_db")
def translation_mimo_factory(language_factory, translation_key_mimo_factory):
    """Translation factory fixture."""
    from translate.service.tests.factories import TranslationFactory

    obj = TranslationFactory.create(language=language_factory, key=translation_key_mimo_factory)

    yield obj, language_factory, translation_key_mimo_factory
    obj.delete()


@pytest.fixture
def translation_provider(provider_to_fixture):
    """Translation provider fixture."""
    from translate.service.tests.providers import TranslationProvider

    provider_to_fixture.add_provider(TranslationProvider)

    yield provider_to_fixture


@pytest.fixture
def language_provider(provider_to_fixture):
    """Language provider fixture."""
    from translate.service.tests.providers import LanguageProvider

    provider_to_fixture.add_provider(LanguageProvider)

    yield provider_to_fixture


@pytest.fixture
def translation_key_provider(provider_to_fixture):
    """Translation key provider."""
    from translate.service.tests.providers import TranslationKeyProvider

    provider_to_fixture.add_provider(TranslationKeyProvider)

    yield provider_to_fixture


@pytest.fixture
def user_account(worker_id):
    """Use a different account in each xdist worker"""
    return f"account_{worker_id}"


@pytest.fixture
def import_german_translations_fixture():
    """Inserts data into test database before running tests. Needed for ``client`` tests."""
    from django.core.management import call_command

    from translate.service.models import Language, Translation, TranslationKey

    Translation.objects.all().delete()
    TranslationKey.objects.all().delete()
    Language.objects.all().delete()

    call_command("import_translations", translations_dir="translate/service/tests/fixtures/german_fixtures")
    yield

    Translation.objects.all().delete()
    TranslationKey.objects.all().delete()
    Language.objects.all().delete()


@pytest.fixture
def import_french_translations_fixture():
    """Inserts data into test database before running tests. Needed for ``client`` tests."""
    from django.core.management import call_command

    from translate.service.models import Language, Translation, TranslationKey

    Translation.objects.all().delete()
    TranslationKey.objects.all().delete()
    Language.objects.all().delete()

    call_command("import_translations", translations_dir="translate/service/tests/fixtures/french_fixtures")
    yield

    Translation.objects.all().delete()
    TranslationKey.objects.all().delete()
    Language.objects.all().delete()


@pytest.fixture
def request_serializer_fixture(make_request):
    from translate.service.serializers import TranslationRequestSerializer

    lang = {"language": "de"}
    arguments = {
        "views": ["translation_center_frontend", "translations_center_placeholders"],
        "page": 1,
        "page_size": 5,
    }
    data = dict(lang, **arguments)
    yield TranslationRequestSerializer(data=data)


@pytest.fixture
def export_csv_fixture(import_german_translations_fixture):
    """Yields path of generated CSV file"""
    import os
    from pathlib import Path

    from django.core.management import call_command

    language_code = "de"
    file_name = f"translations_{language_code}.csv"

    call_command("export_csv", language_code)
    file_path = Path(file_name)

    yield file_path

    os.remove(file_name)
