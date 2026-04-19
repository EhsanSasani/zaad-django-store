import json
from urllib.parse import quote

from django.conf import settings


def site_defaults(request):
    site_url = getattr(settings, "ZAAD_SITE_URL", "https://zaad.ir").rstrip("/")
    phone_display = getattr(settings, "ZAAD_PHONE_DISPLAY", "۰۹۱۲ ۱۲۳ ۴۵۶۷")
    phone_e164 = getattr(settings, "ZAAD_PHONE_E164", "+989121234567")
    whatsapp_number = getattr(settings, "ZAAD_WHATSAPP_NUMBER", "989121234567")
    opening_hours_text = getattr(settings, "ZAAD_OPENING_HOURS_TEXT", "هر روز ۱۰:۰۰ تا ۲۲:۰۰")
    response_time_text = getattr(settings, "ZAAD_RESPONSE_TIME_TEXT", "زمان متوسط پاسخ‌گویی: حدود ۱۵ دقیقه")

    address_street = getattr(settings, "ZAAD_ADDRESS_STREET", "بلوار سجاد، پلاک ۲۲")
    address_locality = getattr(settings, "ZAAD_ADDRESS_LOCALITY", "Mashhad")
    address_region = getattr(settings, "ZAAD_ADDRESS_REGION", "Razavi Khorasan")
    address_country = getattr(settings, "ZAAD_ADDRESS_COUNTRY", "IR")
    address_postal = getattr(settings, "ZAAD_ADDRESS_POSTAL_CODE", "9183811111")

    whatsapp_message = "سلام، برای هماهنگی سفارش نیاز به راهنمایی دارم."
    whatsapp_href = f"https://wa.me/{whatsapp_number}?text={quote(whatsapp_message)}"

    local_business_schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "زاد",
        "url": site_url,
        "telephone": phone_e164,
        "address": {
            "@type": "PostalAddress",
            "streetAddress": address_street,
            "addressLocality": address_locality,
            "addressRegion": address_region,
            "postalCode": address_postal,
            "addressCountry": address_country,
        },
        "areaServed": "Mashhad, Razavi Khorasan, IR",
        "sameAs": [getattr(settings, "ZAAD_INSTAGRAM_URL", "https://instagram.com/zaad.store")],
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
        "site_whatsapp_base": f"https://wa.me/{whatsapp_number}",
        "site_whatsapp_href": whatsapp_href,
        "site_instagram_url": getattr(settings, "ZAAD_INSTAGRAM_URL", "https://instagram.com/zaad.store"),
        "site_opening_hours_text": opening_hours_text,
        "site_response_time_text": response_time_text,
        "site_address_text": f"{address_street}، {address_locality}",
        "site_whatsapp_default_message": whatsapp_message,
        "local_business_jsonld": json.dumps(local_business_schema, ensure_ascii=False),
    }
