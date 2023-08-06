import glob
import json
import operator
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict

import django.db.utils
import polib
from django.conf import settings
from django.conf.locale import LANG_INFO
from django.core.management.base import BaseCommand

from translate.core.utils.logging import log
from translate.service.models import Language, Translation, TranslationKey

SNAKE_TRANSLATIONS = Path("snake_translations.json")
# DEFAULT_DIR_PATH = Path("translate/service/tests/fixtures")  # This is a testing directory
DEFAULT_DIR_PATH = Path("export_translations")


def extract_language(path: str) -> str:
    """Extract language from path with locale."""
    parts = path.split("/")
    idx = parts.index("locale")
    return parts[idx + 1]


class Command(BaseCommand):
    help = "Importing translation keys command from .json and .po files"

    def add_arguments(self, parser):
        """Attach argument for import_translations command."""
        parser.add_argument(
            "translations_dir",
            type=str,
            nargs="?",
            default=DEFAULT_DIR_PATH,
        )

    @staticmethod
    def read_po_files(dirs) -> dict:
        """Read po files."""
        log.info("Reading po files.")
        po_files = {
            po_file: polib.pofile(po_file, encoding="utf-8")
            for po_file in glob.iglob(f"{dirs}/**/*.po", recursive=True)
        }

        files_with_languages = defaultdict(list)
        for file_path, file in po_files.items():
            lang = extract_language(file_path)
            files_with_languages[lang].append((file_path, file))

        log.info("Done")
        return files_with_languages

    @staticmethod
    def create_po_keys(file_entries):
        """Create po keys."""

        existing_po_keys = {key.id_name: key for key in TranslationKey.objects.all()}

        new_po_keys = {
            entry.msgid: TranslationKey(
                id_name=entry.msgid,
                id_name_plural=entry.msgid_plural,
                encoding=entry.encoding,
                usage_context=entry.msgctxt,
                occurrences=sorted(map(operator.itemgetter(0), entry.occurrences)),
                flags=entry.flags,
            )
            for entry in file_entries
            if entry.msgid not in existing_po_keys.keys()
        }

        return existing_po_keys, new_po_keys

    @staticmethod
    def create_po_translations(file_entries, key_entries, language) -> list:
        """Create po translations."""

        entries = [
            Translation(
                language=language,
                key=key_entries.get(entry.msgid),
                translation=entry.msgstr if entry.msgstr else entry.msgid,
                translation_plural=entry.msgid_plural,
            )
            for entry in file_entries
        ]

        return entries

    @staticmethod
    def process_po_files(dirs):
        """Process po files."""
        po_files = Command.read_po_files(dirs)

        existing_keys, new_key_entries = {}, {}
        for lang, files in sorted(po_files.items()):
            for file_path, file_entries in files:
                d1, d2 = Command.create_po_keys(file_entries)
                existing_keys = {**existing_keys, **d1}
                new_key_entries = {**new_key_entries, **d2}

        log.info(f"Found {len(existing_keys.items())} already existing TranslationKeys.")
        log.info(f"Prepared {len(new_key_entries.items())} of new TranslationKeys via po files.")

        inserts = TranslationKey.objects.bulk_create(new_key_entries.values(), ignore_conflicts=True)
        if not inserts:
            log.info("NO NEW PO TRANSLATIONS HAVE BEEN ADDED")
        else:
            log.info(f"Done. Inserted {len(inserts)} TranslationKeys from po files.")
        log.info("----------------------------------------------------")

        all_keys = {**existing_keys, **new_key_entries}

        translations = defaultdict(list)
        for lang, files in sorted(po_files.items()):
            language, _ = Language.objects.get_or_create(lang_info=lang)
            for file_path, file_entries in files:
                translations[lang].extend(Command.create_po_translations(file_entries, all_keys, language))

        for lang, translations_list in translations.items():
            translation_inserts = []
            integrity_errors = 0
            try:
                log.info(f"Prepared {len(translations_list)} Translations for {lang} language. Inserting bulk... ")
                translation_inserts = Translation.objects.bulk_create(translations_list, ignore_conflicts=True)
            except django.db.utils.IntegrityError:
                log.info("Integrity error occurred, and bulk create was canceled! Inserting individually...")
                for obj in translations_list:
                    try:
                        obj.save()
                        translation_inserts.append(obj)
                    except django.db.utils.IntegrityError:
                        integrity_errors += 1

            log.info(f"Integrity error occurred with {integrity_errors} Translations for {lang} language.")
            if not translation_inserts:
                log.info("NO NEW PO TRANSLATIONS HAVE BEEN ADDED")
            log.info(f"Done. Inserted {len(translation_inserts)} Translations from po files for {lang} language.")
            log.info("----------------------------------------------------")

    @staticmethod
    def create_json_keys(language_data, language_code):
        """Create language data."""
        log.info("Preparing translation keys.")
        keys = [
            TranslationKey(
                snake_name=snake_name, id_name=obj.get("translations"), views=[source_dict] + obj.get("source")
            )
            for source_dict, value in language_data.items()
            for snake_name, obj in value.items()
        ]
        key_dict = {}
        for key in keys:
            key_dict[key.snake_name] = key

        log.info(f"Prepared {len(keys)} RAW TranslationKeys for {language_code} language.")

        log.info("Cleaning")
        already_imported_sn = Command.json_keys_sanity_check(keys)
        for name in already_imported_sn:
            if name in key_dict.keys():
                key_dict.pop(name)

        bulk_inserts = key_dict.values()
        if not bulk_inserts:
            log.info("NO NEW KEYS HAVE BEEN INSERTED!")
        else:
            log.info("Inserting in bulk...")
            objs = TranslationKey.objects.bulk_create(bulk_inserts, ignore_conflicts=True)
            log.info("Done!")
            log.info(f"Imported {len(objs)} TranslationKeys into database!")

        return key_dict

    @staticmethod
    def json_keys_sanity_check(obj_keys) -> list:
        """
        This method returns a list of already imported key objects snake_names
        """
        snake_names = []
        for key in obj_keys:
            snake_names.append(key.snake_name)

        already_existing_keys = TranslationKey.objects.in_bulk(snake_names, field_name="snake_name")
        log.info(f"Already existing json keys and snake names {len(already_existing_keys.keys())} founded in database.")
        return already_existing_keys.keys()

    @staticmethod
    def read_json_translations(dirs):
        """Read JSON translations."""
        log.info("Reading json translations")
        translations = json.loads((settings.BASE_DIR.parent / dirs / SNAKE_TRANSLATIONS).read_text())
        log.info("Done")
        log.info(f"There are {len(translations)} available languages in this file.")
        return translations

    @staticmethod
    def create_json_translations(translations: Dict[str, Any], lang_key: str):
        """Import snake_names for a specific language."""
        log.info(f"Processing snake_names from JSON for {lang_key} language.")
        language = Language.objects.get(lang_info=lang_key)
        data_for_provided_language = translations.get(lang_key)

        bulk_translations = []
        for _, dict_data in data_for_provided_language.items():
            snake_names_list = list(dict_data.keys())
            keys = {key.snake_name: key for key in TranslationKey.objects.filter(snake_name__in=snake_names_list)}

            for snake_key, snake_data in dict_data.items():
                translation_key = keys.get(snake_key)
                if translation_key:
                    translation = Translation(
                        language=language,
                        key=translation_key,
                        translation=snake_data.get("translations"),
                        translation_plural=snake_data.get("translations"),
                    )
                    bulk_translations.append(translation)

        try:
            Translation.objects.bulk_create(bulk_translations, ignore_conflicts=True)
        except django.db.utils.IntegrityError:
            log.info("There was a Integrity Error with json files, none were inserted.")
        log.info("Done")
        log.info("----------------------------------------------------")

    @staticmethod
    def process_json_files(dirs):
        """Process json files."""
        translations = Command.read_json_translations(dirs)

        _ = {
            lang: Language.objects.get_or_create(lang_info=lang)
            for lang in translations
            if lang in list(LANG_INFO.keys())
        }

        for lang in translations:
            _ = Command.create_json_keys(translations.get(lang), lang)
            _ = Command.create_json_translations(translations, lang)

    def handle(self, *args, **options):
        """Entrypoint to the command."""

        dir_name = Path(settings.BASE_DIR.parent, options.get("translations_dir"))

        Command.process_json_files(dir_name)
        Command.process_po_files(dir_name)
