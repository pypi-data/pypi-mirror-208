from django.core.management.base import BaseCommand

from translate.core.utils.logging import log
from translate.service.models import Translation, TranslationKey


class Command(BaseCommand):
    help = "Delete all keys that have no usage_context inserted"

    def handle(self, *args, **kwargs):

        translations = Translation.objects.filter(key__usage_context__isnull=True)
        t_keys = TranslationKey.objects.filter(usage_context__isnull=True)

        log.info(f"Prepared {len(translations)} Translations and {len(t_keys)} TranslationKeys for deletion.")
        log.info("Deleting...")

        translations.delete()
        t_keys.delete()

        log.info("Done!")
