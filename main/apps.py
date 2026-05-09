from django.apps import AppConfig


# --- پیکربندی پایه اپ اصلی فروشگاه ---
class MainConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "main"
    verbose_name = "محتوای فروشگاه"
