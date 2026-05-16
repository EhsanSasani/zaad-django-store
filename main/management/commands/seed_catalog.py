from django.core.management.base import BaseCommand

from main.models import Category, Product, Tag


class Command(BaseCommand):
    help = "Seed/sync ZAAD catalog categories and tags safely."

    FLOWER_CATEGORIES = [
        {
            "name": "دسته گل",
            "slug": "hand-bouquet",
            "sort_order": 10,
            "legacy_slugs": ["bouquet"],
        },
        {
            "name": "باکس گل",
            "slug": "box",
            "sort_order": 20,
            "legacy_names": ["باکس"],
        },
        {
            "name": "بوکت",
            "slug": "bouquet",
            "sort_order": 30,
        },
        {
            "name": "استند گل",
            "slug": "stand",
            "sort_order": 40,
            "legacy_names": ["استند"],
        },
        {
            "name": "ماشین عروس",
            "slug": "bridal-car",
            "sort_order": 50,
            "legacy_slugs": ["bridal-car-decoration"],
        },
        {
            "name": "دسته گل عروس",
            "slug": "bridal-bouquet",
            "sort_order": 60,
        },
        {
            "name": "جار گل",
            "slug": "jar",
            "sort_order": 70,
        },
        {
            "name": "گیاه",
            "slug": "plants",
            "sort_order": 80,
            "legacy_slugs": ["plant"],
        },
    ]

    OTHER_CATEGORIES = [
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

    TAGS = [
        {
            "name": "تولد",
            "slug": "tavalod",
            "sort_order": 10,
            "legacy_slugs": ["birthday"],
        },
        {
            "name": "عاشقانه",
            "slug": "asheghane",
            "sort_order": 20,
            "legacy_slugs": ["romantic"],
        },
        {
            "name": "یونیک",
            "slug": "unique",
            "sort_order": 30,
            "legacy_slugs": ["special"],
            "legacy_names": ["خاص"],
        },
        {
            "name": "تبریک",
            "slug": "tabrik",
            "sort_order": 40,
            "legacy_slugs": ["congratulations"],
        },
        {
            "name": "معذرت خواهی",
            "slug": "mazerat-khahi",
            "sort_order": 50,
            "legacy_slugs": ["apology"],
            "legacy_names": ["عذرخواهی"],
        },
        {
            "name": "ترحیم",
            "slug": "tarhim",
            "sort_order": 60,
            "legacy_slugs": ["condolence", "sympathy"],
            "legacy_names": ["تسلیت"],
        },
        {
            "name": "خواستگاری",
            "slug": "khastegari",
            "sort_order": 70,
            "legacy_slugs": ["proposal"],
        },
        {
            "name": "بله برون",
            "slug": "bale-boroon",
            "sort_order": 80,
        },
        {
            "name": "بدون مناسبت",
            "slug": "bedoone-monasebat",
            "sort_order": 90,
            "legacy_slugs": ["no-occasion"],
        },
        {
            "name": "ارسال روز",
            "slug": "ersale-rooz",
            "sort_order": 100,
            "is_occasion": False,
            "legacy_slugs": ["same-day"],
            "legacy_names": ["ارسال فوری"],
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write("شروع همگام‌سازی کاتالوگ زاد...")

        for item in self.FLOWER_CATEGORIES:
            self.sync_category(
                section=Category.Section.FLOWERS,
                name=item["name"],
                slug=item["slug"],
                sort_order=item["sort_order"],
                legacy_slugs=item.get("legacy_slugs", []),
                legacy_names=item.get("legacy_names", []),
            )

        for item in self.OTHER_CATEGORIES:
            self.sync_category(
                section=item["section"],
                name=item["name"],
                slug=item["slug"],
                sort_order=item["sort_order"],
                legacy_slugs=item.get("legacy_slugs", []),
                legacy_names=item.get("legacy_names", []),
            )

        self.deactivate_legacy_flower_category("basket", "سبد گل قدیمی غیرفعال شد.")

        for item in self.TAGS:
            self.sync_tag(
                name=item["name"],
                slug=item["slug"],
                sort_order=item["sort_order"],
                is_occasion=item.get("is_occasion", True),
                legacy_slugs=item.get("legacy_slugs", []),
                legacy_names=item.get("legacy_names", []),
            )

        self.stdout.write(self.style.SUCCESS("کاتالوگ زاد با موفقیت همگام‌سازی شد."))

    def sync_category(self, *, section, name, slug, sort_order, legacy_slugs=None, legacy_names=None):
        legacy_slugs = legacy_slugs or []
        legacy_names = legacy_names or []

        category = self.find_category(section, slug, name, legacy_slugs, legacy_names)
        target = Category.objects.filter(section=section, slug=slug).first()

        if category and target and category.pk != target.pk:
            moved = Product.objects.filter(category=category).update(category=target)
            category.is_active = False
            category.slug = f"{category.slug}-legacy-{category.pk}"
            category.name = f"{category.name} قدیمی"
            category.save(update_fields=["is_active", "slug", "name", "updated_at"])
            category = target
            self.stdout.write(self.style.WARNING(f"{moved} محصول از دسته قدیمی به {target} منتقل شد."))

        if category:
            created = False
        else:
            category = Category(section=section, slug=slug)
            created = True

        category.name = name
        category.slug = slug
        category.section = section
        category.is_active = True
        category.sort_order = sort_order
        category.save()

        status = "ساخته شد" if created else "به‌روزرسانی شد"
        self.stdout.write(self.style.SUCCESS(f"{category} - {status}"))
        return category

    def find_category(self, section, slug, name, legacy_slugs, legacy_names):
        lookups = [
            {"section": section, "slug": slug},
            {"section": section, "name": name},
        ]

        lookups += [{"section": section, "slug": legacy_slug} for legacy_slug in legacy_slugs]
        lookups += [{"section": section, "name": legacy_name} for legacy_name in legacy_names]

        for lookup in lookups:
            category = Category.objects.filter(**lookup).order_by("id").first()
            if category:
                return category

        return None

    def deactivate_legacy_flower_category(self, slug, message):
        category = Category.objects.filter(
            section=Category.Section.FLOWERS,
            slug=slug,
            is_active=True,
        ).first()

        if not category:
            return

        if Product.objects.filter(category=category).exists():
            self.stdout.write(self.style.WARNING(f"{category} محصول دارد؛ غیرفعال نشد."))
            return

        category.is_active = False
        category.save(update_fields=["is_active", "updated_at"])
        self.stdout.write(self.style.WARNING(message))

    def sync_tag(self, *, name, slug, sort_order, is_occasion=True, legacy_slugs=None, legacy_names=None):
        legacy_slugs = legacy_slugs or []
        legacy_names = legacy_names or []

        tag = self.find_tag(slug, name, legacy_slugs, legacy_names)
        target = Tag.objects.filter(slug=slug).first()

        if tag and target and tag.pk != target.pk:
            for product in tag.products.all():
                product.tags.add(target)
            tag.is_active = False
            tag.slug = f"{tag.slug}-legacy-{tag.pk}"
            tag.name = f"{tag.name} قدیمی"
            tag.save(update_fields=["is_active", "slug", "name", "updated_at"])
            tag = target
            self.stdout.write(self.style.WARNING(f"برچسب قدیمی در {target} ادغام شد."))

        if tag:
            created = False
        else:
            tag = Tag(slug=slug)
            created = True

        tag.name = name
        tag.slug = slug
        tag.is_occasion = is_occasion
        tag.is_active = True
        tag.sort_order = sort_order
        tag.save()

        status = "ساخته شد" if created else "به‌روزرسانی شد"
        self.stdout.write(self.style.SUCCESS(f"{tag} - {status}"))
        return tag

    def find_tag(self, slug, name, legacy_slugs, legacy_names):
        lookups = [{"slug": slug}, {"name": name}]
        lookups += [{"slug": legacy_slug} for legacy_slug in legacy_slugs]
        lookups += [{"name": legacy_name} for legacy_name in legacy_names]

        for lookup in lookups:
            tag = Tag.objects.filter(**lookup).order_by("id").first()
            if tag:
                return tag

        return None
