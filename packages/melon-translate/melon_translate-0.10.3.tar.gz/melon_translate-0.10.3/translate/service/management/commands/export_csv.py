import csv
from pathlib import Path

from django.conf.locale import LANG_INFO
from django.core.management.base import BaseCommand

from translate.core.utils.logging import log
from translate.service.models import Language, Translation


class Command(BaseCommand):
    """Export translations in following format:  language, key, context, translation, translation_plural"""

    help = "Export database translations to CSV file"

    def add_arguments(self, parser):
        """Attach argument for import_translations command."""
        parser.add_argument(
            "languages",
            type=str,
            nargs="+",
            default=["de"],
        )

    @staticmethod
    def export_csv(language: Language):
        """Export translations to CSV file."""
        _DB_READ_PAGE_SIZE = 500
        _CSV_HEADER = ["language", "key", "context", "translation", "translation_plural"]

        file_name = Path(f"translations_{language.lang_info}.csv")
        log.info(f"Exporting translations to {file_name.absolute()}")

        qs = (
            Translation.objects.filter(language=language)
            .exclude(key__snake_name__startswith="snake_name_")
            .order_by("key__snake_name")
        )

        with file_name.open(mode="w") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=_CSV_HEADER)

            writer.writeheader()
            for record in qs.iterator(chunk_size=_DB_READ_PAGE_SIZE):
                record = {
                    "language": record.language.lang_info,
                    "key": record.key.snake_name,
                    "context": record.key.usage_context,
                    "translation": record.translation,
                    "translation_plural": record.translation_plural,
                }
                log.info(f"Writing record {record}")
                writer.writerow(record)

    def handle(self, *args, **options):
        """Handle command."""
        languages = options.get("languages")
        for language in languages:
            if language not in LANG_INFO:
                raise RuntimeError(f"Language {language} not found.")

            try:
                language = Language.objects.get(lang_info=language)
                self.export_csv(language)
            except Language.DoesNotExist:
                log.error(f"Language {language} not found in database.")
                continue

        log.info("Done!")
