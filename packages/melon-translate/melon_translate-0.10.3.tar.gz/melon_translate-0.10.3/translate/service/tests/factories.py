import random

import factory
from django.conf.locale import LANG_INFO

from translate.service import models


class TranslationFactory(factory.django.DjangoModelFactory):
    """Testing factory for ``Translation`` model."""

    class Meta:
        model = models.Translation

    translation = factory.Faker("bs")


class LanguageFactory(factory.django.DjangoModelFactory):
    """Testing factory for ``Language`` model."""

    class Meta:
        model = models.Language

    lang_info = random.choice(list(LANG_INFO.keys()))


class TranslationKeyFactory(factory.django.DjangoModelFactory):
    """Testing factory for ``TranslationKey`` model."""

    class Meta:
        model = models.TranslationKey
