from django.db import migrations, models


def delete_visit_heroes(apps, schema_editor):
    SiteHero = apps.get_model("main", "SiteHero")
    SiteHero.objects.filter(target_page="visit").delete()


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0006_alter_sitehero_target_page"),
    ]

    operations = [
        migrations.RunPython(delete_visit_heroes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="sitehero",
            name="target_page",
            field=models.CharField(
                choices=[
                    ("flowers", "گل‌ها"),
                    ("bakery", "بیکری"),
                    ("gifts", "هدایا"),
                    ("events", "رویدادها"),
                    ("occasions", "مناسبت‌ها"),
                    ("contact", "تماس با ما"),
                    ("faq", "سوالات پرتکرار"),
                    ("blog", "بلاگ"),
                    ("about", "درباره زاد"),
                    ("mashhad", "سفارش در مشهد"),
                    ("subcategory", "زیر‌دسته"),
                    ("item", "صفحه محصول"),
                ],
                max_length=30,
                verbose_name="صفحه هدف",
            ),
        ),
    ]
