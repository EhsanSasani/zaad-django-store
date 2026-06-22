from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Compatibility wrapper. Use seed_catalog to sync zad tags and categories."

    def handle(self, *args, **options):
        self.stdout.write("seed_tags قدیمی بود؛ همگام‌سازی کامل از طریق seed_catalog انجام می‌شود.")
        call_command("seed_catalog")
