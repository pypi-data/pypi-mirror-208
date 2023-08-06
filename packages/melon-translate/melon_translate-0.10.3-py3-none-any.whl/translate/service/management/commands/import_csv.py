import csv
from pathlib import Path

from django.conf.locale import LANG_INFO
from django.core.exceptions import ObjectDoesNotExist
from django.core.management.base import BaseCommand

from translate.core.utils.logging import log
from translate.service.models import Language, Translation, TranslationKey


class Command(BaseCommand):
    """
    Updates translations in database from CSV file. It does not create new Translation objs, nor TranslationKey objs.
    Languages need to be created before usage of the command.
    Following format of CSV file is accepted:  language, key, context, translation, translation_plural
    """

    help = "Updates database with translations from CSV file"

    def add_arguments(self, parser):
        """Attach argument for import_translations command."""

        parser.add_argument(
            "file_name",
            type=str,
            nargs=1,
            default="translations_de.csv",
        )

    @staticmethod
    def get_language(file_name):
        """Opens CSV file and returns language obj"""
        file_name = Path(file_name)
        with file_name.open() as csvfile:
            reader_dict = csv.DictReader(csvfile)
            field_name = reader_dict.fieldnames[0]
            for record in reader_dict:
                language_code = record.get(field_name)
                if language_code not in LANG_INFO:
                    raise RuntimeError(f"Language {language_code} not found.")
                try:
                    language = Language.objects.get(lang_info=language_code)
                    return language
                except ObjectDoesNotExist:
                    log.error(f"Language {language_code} not found in database.")
                    break

    @staticmethod
    def import_csv(language: Language, file_name):
        """Import translations from CSV file to database."""

        file_name = Path(file_name)
        log.info(f"Importing translations from {file_name.absolute()}")

        with file_name.open() as csvfile:
            reader_dict = csv.DictReader(csvfile)

            for record in reader_dict:
                snake_key = record.get("key")
                translation = record.get("translation")  # .encode("utf-8").decode("ISO-8859-1")
                translation_plural = record.get("translation_plural")  # .encode("utf-8").decode("ISO-8859-1")

                if translation and translation_plural:
                    try:
                        key = TranslationKey.objects.get(snake_name=snake_key)
                    except ObjectDoesNotExist:
                        log.error(f"This key {snake_key} does not exists in database...")
                        log.error("Have you created keys with import_translations management command?")
                        continue

                    translation_updated = Translation.objects.filter(language=language, key=key).update(
                        translation=translation, translation_plural=translation_plural
                    )
                    if translation_updated:
                        log.info(f"Updating record {snake_key} for {language.lang_info} language")

    def handle(self, *args, **options):
        """Handle command."""
        file_name = options.get("file_name")[0]

        language = self.get_language(file_name)
        self.import_csv(language, file_name)

        log.info("Done!")
