import json

from django.conf import settings


def site_defaults(request):
    site_url = getattr(settings, "zad_SITE_URL", "https://zad.ir").rstrip("/")
    phone_display = getattr(settings, "zad_PHONE_DISPLAY", "۰۹۱۲ ۱۲۳ ۴۵۶۷")
    phone_e164 = getattr(settings, "zad_PHONE_E164", "+989121234567")
    opening_hours_text = getattr(settings, "zad_OPENING_HOURS_TEXT", "Every day, 10:00–22:00")
    response_time_text = getattr(settings, "zad_RESPONSE_TIME_TEXT", "Average response time: about 15 minutes")

    address_street = getattr(settings, "zad_ADDRESS_STREET", "Sajjad Blvd, No. 22")
    address_locality = getattr(settings, "zad_ADDRESS_LOCALITY", "Mashhad")
    address_region = getattr(settings, "zad_ADDRESS_REGION", "Razavi Khorasan")
    address_country = getattr(settings, "zad_ADDRESS_COUNTRY", "IR")
    address_postal = getattr(settings, "zad_ADDRESS_POSTAL_CODE", "9183811111")

    telegram_url = getattr(settings, "zad_TELEGRAM_URL", "https://t.me/zad_store")
    instagram_url = getattr(settings, "zad_INSTAGRAM_URL", "https://instagram.com/zad.store")
    email = getattr(settings, "zad_EMAIL", "info@zadconcept.com")

    local_business_schema = {
        "@context": "https://schema.org",
        "@type": "LocalBusiness",
        "name": "zad",
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
        "site_instagram_url": instagram_url,
        "site_email": email,
        "site_opening_hours_text": opening_hours_text,
        "site_response_time_text": response_time_text,
        "site_address_text": f"{address_street}, {address_locality}",
       "top_notice_text": "چنانچه قصد خرید محصولات زاد از خارج از ایران از طریق PayPal را دارید، از طریق شماره +989374999505 در Telegram با ما در ارتباط باشید.",
        "local_business_jsonld": json.dumps(local_business_schema, ensure_ascii=False),
    }
