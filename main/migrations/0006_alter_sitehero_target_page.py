from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("main", "0005_alter_product_product_code"),
    ]

    operations = [
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
                    ("visit", "بازدید حضوری"),
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
