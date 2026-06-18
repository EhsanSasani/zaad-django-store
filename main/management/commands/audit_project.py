from django.core.management.base import BaseCommand
from django.urls import get_resolver, URLPattern, URLResolver

from main.models import Category, Product, ProductImage, Tag


class Command(BaseCommand):
    help = "Audit project URLs and catalog data without changing anything."

    def print_url_patterns(self, patterns, prefix=""):
        for pattern in patterns:
            if isinstance(pattern, URLPattern):
                route = prefix + str(pattern.pattern)
                name = pattern.name or "-"
                callback = getattr(pattern.callback, "__name__", str(pattern.callback))
                self.stdout.write(f"  {route:45} name={name:25} view={callback}")

            elif isinstance(pattern, URLResolver):
                nested_prefix = prefix + str(pattern.pattern)
                self.print_url_patterns(pattern.url_patterns, nested_prefix)

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("\n=== URL AUDIT ==="))

        resolver = get_resolver()
        self.print_url_patterns(resolver.url_patterns)

        self.stdout.write(self.style.WARNING("\n=== DATA AUDIT ==="))

        self.stdout.write("\nProducts:")
        self.stdout.write(f"  Total: {Product.objects.count()}")
        self.stdout.write(f"  Active: {Product.objects.filter(is_active=True).count()}")
        self.stdout.write(f"  Draft: {Product.objects.filter(publish_status='draft').count()}")
        self.stdout.write(f"  Published: {Product.objects.filter(publish_status='published').count()}")
        self.stdout.write(f"  Without image: {Product.objects.filter(cover_image='').count()}")
        self.stdout.write(f"  Without price: {Product.objects.filter(price__isnull=True).count()}")
        self.stdout.write(f"  Without name: {Product.objects.filter(name='').count()}")

        self.stdout.write("\nCategories:")
        empty_categories = []
        for category in Category.objects.all().order_by("section", "sort_order", "name"):
            count = Product.objects.filter(category=category).count()
            self.stdout.write(
                f"  [{category.section}] {category.name} / {category.slug}: {count} products"
            )
            if count == 0:
                empty_categories.append(category)

        self.stdout.write("\nEmpty categories:")
        if empty_categories:
            for category in empty_categories:
                self.stdout.write(f"  [{category.section}] {category.name} / {category.slug}")
        else:
            self.stdout.write("  None")

        self.stdout.write("\nTags:")
        empty_tags = []
        for tag in Tag.objects.all().order_by("slug"):
            count = Product.objects.filter(tags=tag).count()
            self.stdout.write(f"  {tag.name} / {tag.slug}: {count} products")
            if count == 0:
                empty_tags.append(tag)

        self.stdout.write("\nEmpty tags:")
        if empty_tags:
            for tag in empty_tags:
                self.stdout.write(f"  {tag.name} / {tag.slug}")
        else:
            self.stdout.write("  None")

        self.stdout.write("\nProduct images:")
        self.stdout.write(f"  Total ProductImage rows: {ProductImage.objects.count()}")

        self.stdout.write(self.style.SUCCESS("\nAudit finished. No data changed.\n"))