"""Django settings for config project."""

import os
from pathlib import Path

from dotenv import load_dotenv

# --- بارگذاری متغیرهای محیطی و مسیر پایه پروژه ---
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
# --- حالت اجرا و تنظیمات امنیتی پایه ---
ENV = os.getenv("ENV", "dev").lower()
DEBUG = os.getenv("DEBUG", "1" if ENV == "dev" else "0") == "1"
SECRET_KEY = os.getenv("SECRET_KEY", "dev-insecure-key-change-me")
ALLOWED_HOSTS = [h.strip() for h in os.getenv("ALLOWED_HOSTS", "*").split(",") if h.strip()]

# --- تعریف اپ‌ها و میان‌افزارها ---
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.sitemaps",
    "django.contrib.staticfiles",
    "main.apps.MainConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

# --- تنظیم موتور قالب و context processorها ---
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "main.context_processors.site_defaults",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"

# --- دیتابیس (توسعه/تولید) ---
if ENV == "prod":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("PGDATABASE"),
            "USER": os.getenv("PGUSER"),
            "PASSWORD": os.getenv("PGPASSWORD"),
            "HOST": os.getenv("PGHOST"),
            "PORT": os.getenv("PGPORT", "5432"),
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

# --- ذخیره‌سازی فایل‌ها و مدیا (لوکال/S3) ---
if ENV == "prod":
    INSTALLED_APPS += ["storages"]
    STORAGES = {
        "default": {"BACKEND": "storages.backends.s3.S3Storage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }

    AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_STORAGE_BUCKET_NAME = os.getenv("AWS_STORAGE_BUCKET_NAME")
    AWS_S3_ENDPOINT_URL = os.getenv("AWS_S3_ENDPOINT_URL")
    AWS_S3_REGION_NAME = os.getenv("AWS_S3_REGION_NAME", "")
    AWS_S3_ADDRESSING_STYLE = os.getenv("AWS_S3_ADDRESSING_STYLE", "path")
    AWS_DEFAULT_ACL = None
    AWS_QUERYSTRING_AUTH = False

    MEDIA_URL = os.getenv("MEDIA_URL", "/media/")
else:
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# --- اعتبارسنجی رمز عبور ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# --- بومی‌سازی و منطقه زمانی ---
LANGUAGE_CODE = "fa"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True

# --- استاتیک و پیش‌فرض کلید اصلی مدل‌ها ---
STATIC_URL = "static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- اطلاعات پایه کسب‌وکار برای SEO/CTA ---
ZAAD_SITE_URL = os.getenv("ZAAD_SITE_URL", "https://zaad.ir")
ZAAD_PHONE_DISPLAY = os.getenv("ZAAD_PHONE_DISPLAY", "۰۹۱۲ ۱۲۳ ۴۵۶۷")
ZAAD_PHONE_E164 = os.getenv("ZAAD_PHONE_E164", "+989121234567")
ZAAD_WHATSAPP_NUMBER = os.getenv("ZAAD_WHATSAPP_NUMBER", "989121234567")
ZAAD_INSTAGRAM_URL = os.getenv("ZAAD_INSTAGRAM_URL", "https://instagram.com/zaad.store")
ZAAD_OPENING_HOURS_TEXT = os.getenv("ZAAD_OPENING_HOURS_TEXT", "هر روز ۱۰:۰۰ تا ۲۲:۰۰")
ZAAD_RESPONSE_TIME_TEXT = os.getenv("ZAAD_RESPONSE_TIME_TEXT", "زمان متوسط پاسخ‌گویی: حدود ۱۵ دقیقه")
ZAAD_ADDRESS_STREET = os.getenv("ZAAD_ADDRESS_STREET", "بلوار سجاد، پلاک ۲۲")
ZAAD_ADDRESS_LOCALITY = os.getenv("ZAAD_ADDRESS_LOCALITY", "Mashhad")
ZAAD_ADDRESS_REGION = os.getenv("ZAAD_ADDRESS_REGION", "Razavi Khorasan")
ZAAD_ADDRESS_COUNTRY = os.getenv("ZAAD_ADDRESS_COUNTRY", "IR")
ZAAD_ADDRESS_POSTAL_CODE = os.getenv("ZAAD_ADDRESS_POSTAL_CODE", "9183811111")
