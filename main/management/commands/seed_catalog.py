from django.core.management.base import BaseCommand

from main.models import Category, Tag


class Command(BaseCommand):
    help = "Seed initial ZAAD catalog categories and tags."

    def handle(self, *args, **options):
        categories = [
            {
                "section": Category.Section.FLOWERS,
                "name": "دسته گل",
                "slug": "bouquet",
                "sort_order": 10,
            },
            {
                "section": Category.Section.FLOWERS,
                "name": "سبد",
                "slug": "basket",
                "sort_order": 20,
            },
            {
                "section": Category.Section.FLOWERS,
                "name": "استند",
                "slug": "stand",
                "sort_order": 30,
            },
            {
                "section": Category.Section.FLOWERS,
                "name": "باکس",
                "slug": "box",
                "sort_order": 40,
            },
            {
                "section": Category.Section.BAKERY,
                "name": "کیک تولد",
                "slug": "birthday-cakes",
                "sort_order": 10,
            },
            {
                "section": Category.Section.BAKERY,
                "name": "کوکی",
                "slug": "cookies",
                "sort_order": 20,
            },
            {
                "section": Category.Section.GIFTS,
                "name": "شمع",
                "slug": "candles",
                "sort_order": 10,
            },
            {
                "section": Category.Section.GIFTS,
                "name": "سفال",
                "slug": "ceramic",
                "sort_order": 20,
            },
            {
                "section": Category.Section.GIFTS,
                "name": "سایر",
                "slug": "others",
                "sort_order": 30,
            },
        ]

        tags = [
            {
                "name": "تولد",
                "slug": "birthday",
                "sort_order": 10,
            },
            {
                "name": "تسلیت",
                "slug": "condolence",
                "sort_order": 20,
            },
            {
                "name": "عذرخواهی",
                "slug": "apology",
                "sort_order": 30,
            },
            {
                "name": "خاص",
                "slug": "special",
                "sort_order": 40,
            },
            {
                "name": "عاشقانه",
                "slug": "romantic",
                "sort_order": 50,
            },
        ]

        for item in categories:
            category, created = Category.objects.update_or_create(
                section=item["section"],
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "is_active": True,
                    "sort_order": item["sort_order"],
                },
            )

            status = "ساخته شد" if created else "به‌روزرسانی شد"
            self.stdout.write(self.style.SUCCESS(f"{category} - {status}"))

        for item in tags:
            tag, created = Tag.objects.update_or_create(
                slug=item["slug"],
                defaults={
                    "name": item["name"],
                    "is_occasion": True,
                    "is_active": True,
                    "sort_order": item["sort_order"],
                },
            )

            status = "ساخته شد" if created else "به‌روزرسانی شد"
            self.stdout.write(self.style.SUCCESS(f"{tag} - {status}"))

        self.stdout.write(self.style.SUCCESS("دسته‌بندی‌ها و برچسب‌های اولیه ساخته شدند."))