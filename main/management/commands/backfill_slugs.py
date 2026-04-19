from django.core.management.base import BaseCommand
from django.utils.text import slugify

from main.models import Flower


# --- فرمان نگهداری برای تکمیل اسلاگ‌های ناقص ---
class Command(BaseCommand):
    help = "Fill missing slugs for existing Flower rows."

    def handle(self, *args, **options):
        updated = 0

        for flower in Flower.objects.all().order_by("id"):
            if flower.slug:
                continue

            # --- تولید slug یکتا با fallback ---
            base = slugify(flower.name) or f"flower-{flower.pk}"
            slug = base
            i = 2

            while Flower.objects.filter(slug=slug).exclude(pk=flower.pk).exists():
                slug = f"{base}-{i}"
                i += 1

            flower.slug = slug
            flower.save(update_fields=["slug"])
            updated += 1

        # --- گزارش تعداد رکوردهای به‌روزرسانی‌شده ---
        self.stdout.write(self.style.SUCCESS(f"Done. Updated {updated} rows."))
