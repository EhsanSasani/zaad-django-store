from django.db import migrations
from django.db.models import Q


def move_wedding_to_occasions(apps, schema_editor):
    Category = apps.get_model("main", "Category")
    Product = apps.get_model("main", "Product")
    Tag = apps.get_model("main", "Tag")

    wedding_tag = Tag.objects.filter(slug="wedding").first()

    if wedding_tag is None:
        wedding_tag = Tag.objects.filter(name="عروسی").first()

    if wedding_tag is None:
        wedding_tag = Tag.objects.create(
            name="عروسی",
            slug="wedding",
            is_occasion=True,
            is_active=True,
            sort_order=85,
        )
    else:
        wedding_tag.slug = "wedding"
        wedding_tag.is_occasion = True
        wedding_tag.is_active = True

        wedding_tag.save(
            update_fields=["slug", "is_occasion", "is_active", "updated_at"]
        )

    wedding_category_ids = Category.objects.filter(
        section="flowers",
    ).filter(
        Q(slug="wedding") | Q(slug="wedding-decoration")
    ).values_list("pk", flat=True)

    wedding_products = Product.objects.filter(category_id__in=wedding_category_ids)
    wedding_tag.products.add(*wedding_products)


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0007_remove_visit_page_hero_target"),
    ]

    operations = [
        migrations.RunPython(move_wedding_to_occasions, migrations.RunPython.noop),
    ]
