import json

from django.conf import settings


def site_defaults(request):
    site_url = getattr(settings, "zad_SITE_URL", "https://zad.ir").rstrip("/")
    phone_display = getattr(settings, "zad_PHONE_DISPLAY", "09154203569")
    phone_e164 = getattr(settings, "zad_PHONE_E164", "+989154203569")
    opening_hours_text = getattr(settings, "zad_OPENING_HOURS_TEXT", "هر روز ۱۰:۰۰ تا ۲۲:۰۰")
    response_time_text = getattr(settings, "zad_RESPONSE_TIME_TEXT", "زمان متوسط پاسخ‌گویی: حدود ۱۵ دقیقه")

    address_street = getattr(settings, "zad_ADDRESS_STREET", "بلوار وکیل اباد - نبش فارغ التحصیلان 6 - کانسپت زاد")
    address_locality = getattr(settings, "zad_ADDRESS_LOCALITY", "مشهد")
    address_region = getattr(settings, "zad_ADDRESS_REGION", "خراسان رضوی")
    address_country = getattr(settings, "zad_ADDRESS_COUNTRY", "IR")
    address_postal = getattr(settings, "zad_ADDRESS_POSTAL_CODE", "")

    telegram_url = getattr(settings, "zad_TELEGRAM_URL", "https://t.me/Flowerhouse_pv")
    telegram_display = getattr(settings, "zad_TELEGRAM_DISPLAY", "@Flowerhouse_pv")
    instagram_url = getattr(settings, "zad_INSTAGRAM_URL", "https://www.instagram.com/zad_concept/")
    email = getattr(settings, "zad_EMAIL", "")

    address_schema = {
        "@type": "PostalAddress",
        "streetAddress": address_street,
        "addressLocality": address_locality,
        "addressRegion": address_region,
        "addressCountry": address_country,
    }

    if address_postal:
        address_schema["postalCode"] = address_postal

    local_business_schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "zad",
        "url": site_url,
        "telephone": phone_e164,
        "address": address_schema,
        "areaServed": "Mashhad, Razavi Khorasan, IR",
        "sameAs": [instagram_url, telegram_url],
        "openingHoursSpecification": [
            {
                "@type": "OpeningHoursSpecification",
                "dayOfWeek": [
                    "Saturday",
                    "Sunday",
                    "Monday",
                    "Tuesday",
                    "Wednesday",
                    "Thursday",
                    "Friday",
                ],
                "opens": "10:00",
                "closes": "22:00",
            }
        ],
    }

    return {
        "site_url": site_url,
        "site_call_href": f"tel:{phone_e164}",
        "site_phone_display": phone_display,
        "site_telegram_url": telegram_url,
        "site_telegram_display": telegram_display,
        "site_instagram_url": instagram_url,
        "site_email": email,
        "site_opening_hours_text": opening_hours_text,
        "site_response_time_text": response_time_text,
        "site_address_text": address_street,
        "top_notice_text": f"برای سفارش و هماهنگی سریع زاد، با شماره {phone_display} تماس بگیرید یا در تلگرام {telegram_display} پیام بدهید.",
        "local_business_jsonld": json.dumps(local_business_schema, ensure_ascii=False),
    }
