from django.core.management.base import BaseCommand

from main.models import Tag


class Command(BaseCommand):
    help = "Create default ZAAD tags."

    def handle(self, *args, **options):
        tags = [
            # Occasion
            ("تولد", "birthday", Tag.TagType.OCCASION, 10),
            ("عاشقانه", "romantic", Tag.TagType.OCCASION, 20),
            ("تبریک", "congratulations", Tag.TagType.OCCASION, 30),
            ("عذرخواهی", "apology", Tag.TagType.OCCASION, 40),
            ("تسلیت", "sympathy", Tag.TagType.OCCASION, 50),
            ("مراسم و رویداد", "events", Tag.TagType.OCCASION, 60),

            # Price
            ("اقتصادی", "budget", Tag.TagType.PRICE, 10),
            ("متوسط", "standard", Tag.TagType.PRICE, 20),
            ("خاص", "premium", Tag.TagType.PRICE, 30),

            # Vibe
            ("مینیمال", "minimal", Tag.TagType.VIBE, 10),
            ("کلاسیک", "classic", Tag.TagType.VIBE, 20),
            ("مدرن", "modern", Tag.TagType.VIBE, 30),
            ("لطیف", "soft", Tag.TagType.VIBE, 40),
            ("لوکس", "luxury", Tag.TagType.VIBE, 50),
        ]

        created_count = 0
        updated_count = 0

        for name, slug, tag_type, sort_order in tags:
            tag, created = Tag.objects.update_or_create(
                slug=slug,
                defaults={
                    "name": name,
                    "tag_type": tag_type,
                    "sort_order": sort_order,
                    "is_active": True,
                },
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Tags ready. Created: {created_count}, Updated: {updated_count}"
            )
        )