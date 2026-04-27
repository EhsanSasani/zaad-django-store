import json
from datetime import timedelta
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LeadRequestForm
from .models import (
    Category,
    Event,
    Flower,
    HomeHeroSlide,
    NewsPost,
    Product,
    PublishStatus,
    SiteHero,
    Tag,
)


# =========================
# Page content
# =========================

SECTION_CONTENT = {
    "flowers": {
        "title": "گل‌های زاد",
        "nav": "flowers",
        "lead_type": "flower",
        "meta_title": "سفارش گل لوکس در مشهد | زاد",
        "meta_description": "گل‌های تازه، طراحی لوکس و ارسال سریع در مشهد. برای سفارش تلفنی یا واتساپ با زاد هماهنگ کنید.",
        "intro": "گل‌های زاد با طراحی لوکس، انتخاب دقیق و ارسال سریع در مشهد ارائه می‌شوند. برای شروع، دسته مناسب را انتخاب کنید.",
        "faq": [
            {
                "question": "آیا امکان ارسال فوری گل در مشهد دارید؟",
                "answer": "بله، برای سفارش‌های همان‌روز در بازه کاری، ارسال سریع در بیشتر مناطق مشهد انجام می‌شود.",
            },
            {
                "question": "قبل از سفارش می‌توانم موجودی امروز را بپرسم؟",
                "answer": "بله، با تماس یا واتساپ موجودی روز و گزینه‌های جایگزین سریع اعلام می‌شود.",
            },
            {
                "question": "برای مراسم ترحیم چه گزینه‌هایی پیشنهاد می‌کنید؟",
                "answer": "استند و تاج گل با طراحی رسمی و رنگ‌بندی متناسب با مراسم در دسترس است.",
            },
            {
                "question": "آیا امکان ثبت سفارش زمان‌دار وجود دارد؟",
                "answer": "بله، می‌توانید زمان تحویل امروز، فردا یا تاریخ انتخابی را ثبت کنید.",
            },
        ],
    },
    "bakery": {
        "title": "بیکری زاد",
        "nav": "bakery",
        "lead_type": "bakery",
        "meta_title": "سفارش بیکری خاص در مشهد | زاد",
        "meta_description": "بیکری منتخب زاد با طراحی پریمیوم برای پذیرایی و هدیه. هماهنگی سفارش روزانه از طریق تماس و واتساپ.",
        "intro": "بیکری زاد برای پذیرایی، هدیه و سفارش‌های خاص روزانه آماده می‌شود. برای انتخاب سریع‌تر، آیتم‌های منتخب را ببینید یا برای هماهنگی با ما تماس بگیرید.",
        "faq": [
            {
                "question": "سفارش بیکری برای امروز امکان‌پذیر است؟",
                "answer": "بله، بسته به ظرفیت روزانه امکان ثبت سفارش فوری یا نیم‌روزی وجود دارد.",
            },
            {
                "question": "آیا می‌توانم بیکری را همراه با گل ارسال کنم؟",
                "answer": "بله، امکان هماهنگی سفارش ترکیبی گل و بیکری با یک زمان تحویل وجود دارد.",
            },
            {
                "question": "برای تعداد بالا چطور سفارش بدهم؟",
                "answer": "برای سفارش سازمانی یا تعداد بالا، از طریق فرم مشاوره یا تماس مستقیم هماهنگ کنید.",
            },
            {
                "question": "زمان پاسخ‌گویی برای بیکری چقدر است؟",
                "answer": "در ساعت کاری معمولاً کمتر از ۱۵ دقیقه پاسخ اولیه دریافت می‌کنید.",
            },
        ],
    },
    "gifts": {
        "title": "هدایا و کانسپت‌استور",
        "nav": "gifts",
        "lead_type": "gift",
        "meta_title": "هدیه‌های خاص و کانسپت‌استور زاد | مشهد",
        "meta_description": "انتخاب هدیه‌های مینیمال و لوکس در کانسپت‌استور زاد. هماهنگی سریع برای ست هدیه، گل و ارسال در مشهد.",
        "intro": "هدیه‌های زاد برای انتخابی خاص، مینیمال و پریمیوم گردآوری شده‌اند. اگر برای ست هدیه یا انتخاب مناسب مردد هستی، سریع‌تر با ما هماهنگ کن.",
        "faq": [],
    },
}


CATEGORY_CONTENT_OVERRIDES = {
    "bouquet": {
        "label": "Bouquets",
        "meta_title": "دسته‌گل لوکس در مشهد | زاد",
        "meta_description": "دسته‌گل‌های مینیمال و پریمیوم زاد با امکان ارسال سریع در مشهد.",
        "intro": "Softly made for gifting.",
        "image": "main/img/sub-bouquet.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "box": {
        "label": "Flower Boxes",
        "meta_title": "باکس گل خاص در مشهد | زاد",
        "meta_description": "باکس‌گل‌های ویژه زاد با طراحی لوکس و هماهنگی تحویل سریع.",
        "intro": "Elegant and easy to gift.",
        "image": "main/img/sub-box.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "basket": {
        "label": "Flower Baskets",
        "meta_title": "سبد گل خاص در مشهد | زاد",
        "meta_description": "سبد گل‌های خاص زاد برای هدیه، مراسم و لحظه‌های مهم.",
        "intro": "Warm, full and beautifully arranged.",
        "image": "main/img/sub-plant.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "stand": {
        "label": "Stands & Wreaths",
        "meta_title": "استند گل و تاج ترحیم در مشهد | زاد",
        "meta_description": "استند و تاج گل رسمی با هماهنگی سریع برای مراسم در مشهد.",
        "intro": "Thoughtful flowers for formal moments.",
        "image": "main/img/sub-stand.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
}


CATEGORY_SLUG_ALIASES = {
    "plant": "basket",
    "wreath": "stand",
}


PAGE_HERO_CONTENT = {
    "occasions": {
        "kicker": "ZAAD Occasions",
        "title": "برای هر لحظه، یک انتخاب نرم‌تر",
        "text": "مناسبتت را انتخاب کن تا پیشنهادهای هماهنگ‌تر ببینی.",
        "image": "main/img/hero-occasions.jpg",
    },
    "flowers": {
        "kicker": "ZAAD Flowers",
        "title": "Flowers for soft, beautiful moments",
        "text": "Made with warmth, care, and feeling.",
        "image": "main/img/hero-flowers.jpg",
    },
    "bakery": {
        "kicker": "ZAAD Bakery",
        "title": "Sweet pieces for everyday joy",
        "text": "Fresh, warm, and made to share.",
        "image": "main/img/hero-bakery.jpg",
    },
    "gifts": {
        "kicker": "ZAAD Gifts",
        "title": "Gifts with warmth and meaning",
        "text": "Simple pieces, chosen with care.",
        "image": "main/img/hero-gifts.jpg",
    },
    "subcategory": {
        "kicker": "ZAAD Collection",
        "title": "",
        "text": "",
        "image": "main/img/hero-subcategory.jpg",
    },
    "item": {
        "kicker": "ZAAD Item",
        "title": "",
        "text": "",
        "image": "main/img/hero-item.jpg",
    },
    "contact": {
        "kicker": "Contact ZAAD",
        "title": "We’re here to help with your order",
        "text": "Reach out for availability, delivery timing, or a quick recommendation from the ZAAD team.",
        "image": "main/img/hero-contact.jpg",
    },
    "visit": {
        "kicker": "Visit ZAAD",
        "title": "Come by and experience ZAAD in person",
        "text": "Visit our space, explore the collection up close, and choose with more confidence and ease.",
        "image": "main/img/hero-visit.jpg",
    },
    "events": {
        "kicker": "ZAAD Events",
        "title": "Beautiful details for special gatherings",
        "text": "Styled softly, remembered warmly.",
        "image": "main/img/hero-events.jpg",
    },
    "blog": {
        "kicker": "ZAAD Journal",
        "title": "Stories, ideas, and gentle inspiration",
        "text": "Thoughtful notes for choosing flowers, gifts, and beautiful details with more ease.",
        "image": "main/img/hero-blog.jpg",
    },
    "faq": {
        "kicker": "ZAAD Help",
        "title": "Answers to help you order with ease",
        "text": "A quick guide to common questions about ordering, delivery, and choosing the right piece.",
        "image": "main/img/hero-faq.jpg",
    },
    "mashhad": {
        "kicker": "ZAAD Mashhad",
        "title": "سفارش در مشهد",
        "text": "برای سفارش سریع، ارسال فوری و هماهنگی دقیق در مشهد از این بخش استفاده کن.",
        "image": "main/img/hero-mashhad.jpg",
    },
    "about": {
        "kicker": "ZAAD Concept Store",
        "title": "About ZAAD",
        "text": "A closer look at our space, our people, and the care behind every order.",
        "image": "main/img/hero-about.jpg",
    },
}


HOME_FAQ = [
    {
        "question": "زاد در چه حوزه‌هایی سفارش می‌پذیرد؟",
        "answer": "گل، بیکری، هدیه و خدمات مرتبط با رویدادها در زاد ارائه می‌شود.",
    },
    {
        "question": "آیا ارسال همان‌روز در مشهد دارید؟",
        "answer": "بله، برای بخش زیادی از سفارش‌ها امکان ارسال سریع همان‌روز وجود دارد.",
    },
    {
        "question": "سریع‌ترین راه هماهنگی سفارش چیست؟",
        "answer": "تماس فوری یا ارسال پیام در واتساپ سریع‌ترین مسیر هماهنگی است.",
    },
    {
        "question": "برای سفارش رویدادی از کجا شروع کنم؟",
        "answer": "از صفحه رویدادها یا فرم مشاوره سفارش، تاریخ و نوع درخواست را ثبت کنید.",
    },
]


VISIT_FAQ = [
    {
        "question": "آیا قبل از مراجعه باید هماهنگ کنم؟",
        "answer": "برای سفارش‌های خاص بهتر است قبل از مراجعه تماس بگیرید تا هماهنگی سریع انجام شود.",
    },
    {
        "question": "ساعت کاری فروشگاه زاد چیست؟",
        "answer": "هر روز از ساعت ۱۰ تا ۲۲ آماده پاسخ‌گویی و پذیرش مراجعه هستیم.",
    },
    {
        "question": "در بازدید حضوری چه خدماتی می‌گیرم؟",
        "answer": "مشاوره انتخاب گل، مشاهده نمونه‌ها و هماهنگی تحویل یا ارسال در محل انجام می‌شود.",
    },
    {
        "question": "می‌توانم هم‌زمان گل و هدیه انتخاب کنم؟",
        "answer": "بله، تیم زاد ترکیب گل و هدیه را برای همان مناسبت پیشنهاد می‌دهد.",
    },
]


CONTACT_FAQ = [
    {
        "question": "زمان پاسخ‌گویی زاد چقدر است؟",
        "answer": "در ساعات کاری، میانگین پاسخ‌گویی اولیه حدود ۱۵ دقیقه است.",
    },
    {
        "question": "ثبت سفارش از چه مسیرهایی انجام می‌شود؟",
        "answer": "از طریق تماس، واتساپ یا فرم درخواست سفارش می‌توانید هماهنگی را انجام دهید.",
    },
    {
        "question": "برای سفارش فوری چه اطلاعاتی لازم است؟",
        "answer": "نام، شماره موبایل، نوع درخواست و بازه زمانی تحویل کافی است.",
    },
    {
        "question": "آیا ارسال خارج از مشهد هم دارید؟",
        "answer": "تمرکز فعلی روی مشهد است، اما در برخی سفارش‌ها هماهنگی شهرهای دیگر بررسی می‌شود.",
    },
]


FAQ_PAGE_ITEMS = [
    *HOME_FAQ,
    *VISIT_FAQ,
    *CONTACT_FAQ,
]


# =========================
# Generic helpers
# =========================

def _jsonld(data):
    return json.dumps(data, ensure_ascii=False)


def _faq_jsonld(faq_items):
    return {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
            for item in faq_items
        ],
    }


def _breadcrumbs_jsonld(request, breadcrumbs):
    items = []

    for position, crumb in enumerate(breadcrumbs, start=1):
        crumb_url = crumb.get("url") or request.path
        items.append(
            {
                "@type": "ListItem",
                "position": position,
                "name": crumb["name"],
                "item": request.build_absolute_uri(crumb_url),
            }
        )

    return {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": items,
    }


def _with_home(items):
    return [{"name": "خانه", "url": reverse("index")}, *items]


def _whatsapp_href(message):
    number = getattr(settings, "ZAAD_WHATSAPP_NUMBER", "989121234567")
    return f"https://wa.me/{number}?text={quote(message)}"


def _item_whatsapp_href(request, product):
    item_url = request.build_absolute_uri(product.get_absolute_url())
    message = (
        f"سلام، این آیتم را می‌خواهم: {product.name} — لطفاً برای موجودی و زمان تحویل راهنمایی کنید. "
        f"{item_url}"
    )
    return _whatsapp_href(message)


def _stock_to_schema(stock_status):
    if stock_status == Product.StockStatus.OUT_OF_STOCK:
        return "https://schema.org/OutOfStock"

    if stock_status == Product.StockStatus.PREORDER:
        return "https://schema.org/PreOrder"

    return "https://schema.org/InStock"


def _product_jsonld(request, product):
    offer = {
        "@type": "Offer",
        "priceCurrency": "IRR",
        "availability": _stock_to_schema(product.stock_status),
        "url": request.build_absolute_uri(product.get_absolute_url()),
    }

    if product.price:
        offer["price"] = str(int(product.price) * 10)

    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "brand": {"@type": "Brand", "name": "زاد"},
        "offers": offer,
    }

    if getattr(product, "cover_image", None):
        schema["image"] = [request.build_absolute_uri(product.cover_image.url)]

    return schema


def _event_to_iso(dt):
    current_tz = timezone.get_current_timezone()

    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, current_tz)
    else:
        dt = timezone.localtime(dt, current_tz)

    return dt.isoformat()


def _hero_defaults(meta_title, meta_description):
    return {
        "page_hero_kicker": "ZAAD",
        "page_hero_title": meta_title,
        "page_hero_text": meta_description,
        "page_hero_image": "main/img/hero-2.jpg",
    }


def _hero_from_key(key, *, title=None, text=None, image=None):
    hero = PAGE_HERO_CONTENT.get(key, {})

    return {
        "page_hero_kicker": hero.get("kicker", "ZAAD"),
        "page_hero_title": title or hero.get("title", "زاد"),
        "page_hero_text": text or hero.get("text", "انتخابی دقیق برای گل، هدیه و سفارش‌های خاص"),
        "page_hero_image": image or hero.get("image", "main/img/hero-2.jpg"),
    }


def _get_active_home_hero_slides():
    slides = list(
        HomeHeroSlide.objects.filter(is_active=True).order_by("sort_order", "id")
    )

    if slides:
        return slides

    return [
        {
            "title": "سفارش گل، بیکری و هدیه با ارسال سریع",
            "kicker": "ZAAD Concept Store",
            "description": "ترکیب لوکس گل، بیکری و هدیه با هماهنگی سریع در مشهد.",
            "image_url": settings.STATIC_URL + "main/img/hero-1.jpg",
            "primary_button_text": "تماس فوری",
            "primary_button_url": "",
            "secondary_button_text": "واتساپ برای سفارش",
            "secondary_button_url": "",
        },
        {
            "title": "چیدمان خاص برای مناسبت‌های مهم",
            "kicker": "لوکس و مینیمال",
            "description": "سفارش گل، بیکری و هدیه با تجربه‌ای یک‌دست و حرفه‌ای.",
            "image_url": settings.STATIC_URL + "main/img/hero-2.jpg",
            "primary_button_text": "",
            "primary_button_url": "",
            "secondary_button_text": "",
            "secondary_button_url": "",
        },
        {
            "title": "ارسال سریع در مشهد",
            "kicker": "زاد مشهد",
            "description": "هماهنگی سریع برای سفارش‌های فوری و انتخاب‌های روز.",
            "image_url": settings.STATIC_URL + "main/img/hero-3.jpg",
            "primary_button_text": "",
            "primary_button_url": "",
            "secondary_button_text": "",
            "secondary_button_url": "",
        },
    ]


def _get_site_hero(target_page, target_slug=""):
    hero = (
        SiteHero.objects.filter(
            is_active=True,
            target_page=target_page,
            target_slug=target_slug,
        )
        .order_by("sort_order", "id")
        .first()
    )

    if hero:
        return {
            "page_hero_kicker": hero.kicker or "ZAAD",
            "page_hero_title": hero.title,
            "page_hero_text": hero.description,
            "page_hero_image": hero.image.url if hero.image else "main/img/hero-2.jpg",
        }

    if target_slug:
        fallback = (
            SiteHero.objects.filter(
                is_active=True,
                target_page=target_page,
                target_slug="",
            )
            .order_by("sort_order", "id")
            .first()
        )

        if fallback:
            return {
                "page_hero_kicker": fallback.kicker or "ZAAD",
                "page_hero_title": fallback.title,
                "page_hero_text": fallback.description,
                "page_hero_image": fallback.image.url if fallback.image else "main/img/hero-2.jpg",
            }

    return None


def _default_context(
    request,
    *,
    page_type,
    active_nav,
    meta_title,
    meta_description,
    breadcrumbs=None,
    faq_items=None,
    item_id=None,
):
    context = {
        "page_type": page_type,
        "active_nav": active_nav,
        "meta_title": meta_title,
        "meta_description": meta_description,
        "canonical_url": request.build_absolute_uri(request.path),
        "item_id": item_id,
        "extra_jsonld": [],
        "is_homepage": False,
        **_hero_defaults(meta_title, meta_description),
    }

    if breadcrumbs:
        context["breadcrumbs"] = breadcrumbs
        context["breadcrumbs_jsonld"] = _jsonld(
            _breadcrumbs_jsonld(request, breadcrumbs)
        )

    if faq_items:
        context["faq_items"] = faq_items
        context["faq_jsonld"] = _jsonld(_faq_jsonld(faq_items))

    return context


# =========================
# Product / category helpers
# =========================

def _published_products():
    return Product.objects.filter(
        is_active=True,
        publish_status=Product.PublishStatus.PUBLISHED,
    )


def _published_products_for_section(section):
    return (
        _published_products()
        .filter(category__section=section)
        .select_related("category")
        .prefetch_related("tags")
    )


def _active_categories_for_section(section):
    return Category.objects.filter(
        section=section,
        is_active=True,
    ).order_by("sort_order", "name")


def _category_content(category):
    override = CATEGORY_CONTENT_OVERRIDES.get(category.slug, {})

    return {
        "label": override.get("label") or category.name,
        "meta_title": override.get("meta_title") or f"{category.name} | زاد",
        "meta_description": (
            override.get("meta_description")
            or category.description
            or f"مشاهده محصولات دسته {category.name} در زاد."
        ),
        "intro": override.get("intro") or category.description or "انتخاب‌هایی هماهنگ برای همین حال‌وهوا.",
        "image": override.get("image") or "main/img/sub-bouquet.jpg",
        "hero_image": override.get("hero_image") or "main/img/hero-subcategory.jpg",
    }


def _category_card(category):
    content = _category_content(category)

    return {
        "slug": category.slug,
        "label": category.name,
        "url": reverse("flower_subcategory", args=[category.slug]),
        "image": category.cover_image.url if category.cover_image else content["image"],
        "intro": category.description or content["intro"],
    }


def _occasion_links(limit=4):
    tags = list(
        Tag.objects.filter(
            is_occasion=True,
            is_active=True,
        ).order_by("sort_order", "name")[:limit]
    )

    return [
        {
            "label": tag.name,
            "url": reverse("occasion_detail", args=[tag.slug]),
        }
        for tag in tags
    ]


# =========================
# Home
# =========================

def index(request):
    legacy_section = (request.GET.get("section") or "").lower()

    if legacy_section in SECTION_CONTENT:
        return redirect(legacy_section)

    featured_today = list(
        _published_products()
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-featured", "sort_order", "-created_at")[:8]
    )

    occasion_tags = list(
    Tag.objects.filter(
        is_occasion=True,
        is_active=True,
        ).order_by("sort_order", "name")[:8]
    )

    context = _default_context(
        request,
        page_type="home",
        active_nav="home",
        meta_title="زاد | سفارش گل، بیکری و هدیه در مشهد",
        meta_description="زاد کانسپت‌استور مشهد برای سفارش گل، بیکری، هدیه و هماهنگی رویداد با ارسال سریع.",
        faq_items=HOME_FAQ,
    )

    context.update(
        {
            "featured_today": featured_today,
            "occasion_tags": occasion_tags,
            "sections": SECTION_CONTENT,
            "hero_call_text": "تماس فوری",
            "hero_whatsapp_text": "واتساپ برای سفارش",
            "home_subtitle": "ترکیب لوکس گل، بیکری و هدیه با ارسال سریع در مشهد",
            "is_homepage": True,
            "home_hero_slides": _get_active_home_hero_slides(),
        }
    )

    return render(request, "index.html", context)


# =========================
# Section pages
# =========================

def _category_page(request, section):
    config = SECTION_CONTENT[section]

    products_qs = _published_products_for_section(section).order_by(
        "-featured",
        "sort_order",
        "-created_at",
    )

    featured_items = list(products_qs[:8])
    all_items = list(products_qs[:16])

    breadcrumbs = _with_home([{"name": config["title"], "url": None}])

    context = _default_context(
        request,
        page_type="category",
        active_nav=config["nav"],
        meta_title=config["meta_title"],
        meta_description=config["meta_description"],
        breadcrumbs=breadcrumbs,
        faq_items=config["faq"] or None,
    )

    hero_data = _hero_from_key(section)
    db_hero = _get_site_hero(section)

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)

    subcategories = []

    if section == Category.Section.FLOWERS:
        subcategories = [
            _category_card(category)
            for category in _active_categories_for_section(Category.Section.FLOWERS)
        ]

    context.update(
        {
            "section": section,
            "section_title": config["title"],
            "section_intro": config["intro"],
            "featured_items": featured_items,
            "all_items": all_items,
            "subcategory_links": subcategories,
            "lead_form": LeadRequestForm(initial_lead_type=config["lead_type"]),
            "lead_default_type": config["lead_type"],
            "category_call_text": "هماهنگی تلفنی",
            "category_whatsapp_text": "مشاوره در واتساپ",
        }
    )

    return render(request, "category.html", context)


def flowers(request):
    return _category_page(request, Category.Section.FLOWERS)


def bakery(request):
    return _category_page(request, Category.Section.BAKERY)


def gifts(request):
    return _category_page(request, Category.Section.GIFTS)


def flower_subcategory(request, subcategory_slug):
    canonical_slug = CATEGORY_SLUG_ALIASES.get(subcategory_slug, subcategory_slug)

    if canonical_slug != subcategory_slug:
        return redirect("flower_subcategory", subcategory_slug=canonical_slug)

    category = get_object_or_404(
        Category,
        section=Category.Section.FLOWERS,
        slug=canonical_slug,
        is_active=True,
    )

    content = _category_content(category)

    items = list(
        _published_products()
        .filter(category=category)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-featured", "sort_order", "-created_at")[:24]
    )

    related_posts = list(
        NewsPost.objects.filter(status=PublishStatus.PUBLISHED).order_by(
            "-published_at",
            "-created_at",
        )[:3]
    )

    breadcrumbs = _with_home(
        [
            {"name": "گل‌های زاد", "url": reverse("flowers")},
            {"name": category.name, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="category",
        active_nav="flowers",
        meta_title=content["meta_title"],
        meta_description=content["meta_description"],
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key(
        "subcategory",
        title=content["label"],
        text=content["intro"],
        image=category.cover_image.url if category.cover_image else content["hero_image"],
    )

    db_hero = _get_site_hero("subcategory", category.slug)

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "subcategory_slug": category.slug,
            "subcategory_label": category.name,
            "subcategory_intro": category.description or content["intro"],
            "items": items,
            "related_posts": related_posts,
            "lead_form": LeadRequestForm(initial_lead_type="flower"),
            "lead_default_type": "flower",
        }
    )

    return render(request, "subcategory.html", context)


# =========================
# Product detail
# =========================

def _item_detail_context(request, product):
    category = product.category
    category_name = category.name if category else "محصول"
    section = category.section if category else ""
    active_nav = section if section in SECTION_CONTENT else ""

    subcategory_url = None
    subcategory_label = None

    if category and category.section == Category.Section.FLOWERS:
        subcategory_url = reverse("flower_subcategory", args=[category.slug])
        subcategory_label = category.name

    breadcrumbs = [{"name": "خانه", "url": reverse("index")}]

    if section and section in SECTION_CONTENT:
        breadcrumbs.append(
            {
                "name": SECTION_CONTENT[section]["title"],
                "url": reverse(section),
            }
        )

    if subcategory_url and subcategory_label:
        breadcrumbs.append(
            {
                "name": subcategory_label,
                "url": subcategory_url,
            }
        )

    breadcrumbs.append({"name": product.name, "url": None})

    similar_items = list(
        _published_products()
        .filter(category=category)
        .exclude(pk=product.pk)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-featured", "sort_order", "-created_at")[:6]
    )

    if len(similar_items) < 3 and section:
        extra_items = list(
            _published_products()
            .filter(category__section=section)
            .exclude(pk=product.pk)
            .exclude(pk__in=[item.pk for item in similar_items])
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-featured", "sort_order", "-created_at")[: 6 - len(similar_items)]
        )
        similar_items.extend(extra_items)

    description = (
        product.description[:140]
        if product.description
        else "برای استعلام موجودی، زمان تحویل و هماهنگی سفارش با تیم زاد تماس بگیرید."
    )

    context = _default_context(
        request,
        page_type="item",
        active_nav=active_nav,
        meta_title=f"{product.name} | زاد",
        meta_description=f"مشاهده جزئیات {product.name} در زاد. هماهنگی موجودی و زمان تحویل با تماس یا واتساپ.",
        breadcrumbs=breadcrumbs,
        item_id=product.pk,
    )

    hero_data = _hero_from_key(
        "item",
        title=product.name,
        text=description,
        image=product.cover_image.url if getattr(product, "cover_image", None) else "main/img/hero-item.jpg",
    )

    db_hero = _get_site_hero("item", product.slug)

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "product": product,
            "category_name": category_name,
            "category_url": reverse(section) if section in SECTION_CONTENT else reverse("index"),
            "subcategory_url": subcategory_url,
            "subcategory_label": subcategory_label,
            "similar_items": similar_items,
            "item_whatsapp_href": _item_whatsapp_href(request, product),
            "item_call_text": "تماس",
            "item_whatsapp_text": "واتساپ",
            "mashhad_order_url": reverse("mashhad_flower_order"),
        }
    )

    context["extra_jsonld"].append(_jsonld(_product_jsonld(request, product)))

    return context


def product_detail(request, pk: int, slug: str):
    product = get_object_or_404(
        _published_products().select_related("category").prefetch_related("tags"),
        pk=pk,
    )

    if slug != product.slug:
        return redirect("product_detail", pk=product.pk, slug=product.slug)

    return render(request, "item_detail.html", _item_detail_context(request, product))


def flower_detail(request, pk: int, slug: str):
    flower = get_object_or_404(
        Flower.objects.filter(
            is_active=True,
            publish_status=Product.PublishStatus.PUBLISHED,
        )
        .select_related("category")
        .prefetch_related("tags"),
        pk=pk,
    )

    if slug != flower.slug:
        return redirect("flower_detail", pk=flower.pk, slug=flower.slug)

    return render(request, "item_detail.html", _item_detail_context(request, flower))


def flower_detail_redirect(request, pk: int):
    flower = get_object_or_404(
        Flower.objects.filter(
            is_active=True,
            publish_status=Product.PublishStatus.PUBLISHED,
        ),
        pk=pk,
    )

    return redirect("flower_detail", pk=flower.pk, slug=flower.slug)


# =========================
# Occasions
# =========================

def occasions(request):
    occasion_tags = list(
    Tag.objects.filter(
        is_occasion=True,
        is_active=True,
    ).order_by("sort_order", "name")[:8]
)

    breadcrumbs = _with_home(
        [
            {
                "name": "مناسبت‌ها",
                "url": None,
            }
        ]
    )

    context = _default_context(
        request,
        page_type="occasions",
        active_nav="occasions",
        meta_title="مناسبت‌ها | زاد",
        meta_description="انتخاب گل، بیکری و هدیه بر اساس مناسبت در زاد.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key("occasions")
    db_hero = _get_site_hero("occasions")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "occasion_tags": occasion_tags,
        }
    )

    return render(request, "occasions.html", context)


def occasion_detail(request, slug):
    occasion = get_object_or_404(
        Tag,
        slug=slug,
        is_occasion=True,
        is_active=True,
    )

    products = list(
        _published_products()
        .filter(tags=occasion)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-featured", "sort_order", "-created_at")[:24]
    )

    breadcrumbs = _with_home(
        [
            {
                "name": "مناسبت‌ها",
                "url": reverse("occasions"),
            },
            {
                "name": occasion.name,
                "url": None,
            },
        ]
    )

    context = _default_context(
        request,
        page_type="occasion-detail",
        active_nav="occasions",
        meta_title=f"{occasion.name} | زاد",
        meta_description=f"پیشنهادهای زاد برای مناسبت {occasion.name}.",
        breadcrumbs=breadcrumbs,
    )

    db_hero = _get_site_hero("occasions", occasion.slug)

    if db_hero:
        context.update(db_hero)
    else:
        context.update(
            {
                "page_hero_kicker": "ZAAD Occasion",
                "page_hero_title": occasion.name,
                "page_hero_text": "انتخاب‌هایی هماهنگ برای همین حال‌وهوا.",
                "page_hero_image": "main/img/hero-occasions.jpg",
            }
        )

    context.update(
        {
            "occasion": occasion,
            "products": products,
        }
    )

    return render(request, "occasion_detail.html", context)


# =========================
# Events
# =========================

def events(request):
    published_events_qs = Event.objects.filter(
        status=PublishStatus.PUBLISHED,
    ).order_by("start_at", "-created_at")

    published_events = list(published_events_qs)

    breadcrumbs = _with_home([{"name": "رویدادها", "url": None}])

    context = _default_context(
        request,
        page_type="category",
        active_nav="events",
        meta_title="رویدادهای زاد | ورکشاپ و تجربه حضوری",
        meta_description="تقویم رویدادهای زاد در مشهد برای ورکشاپ، رونمایی و تجربه‌های حضوری.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key("events")
    db_hero = _get_site_hero("events")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)

    events_are_demo = not published_events_qs.exists()

    if events_are_demo:
        now = timezone.now()
        published_events = [
            {
                "title": "ورکشاپ چیدمان گل",
                "description": "جلسه کوتاه آموزش چیدمان گل با رویکرد مینیمال و لوکس.",
                "start_at": now + timedelta(days=7),
                "end_at": now + timedelta(days=7, hours=2),
                "location": "مشهد، فروشگاه زاد",
                "is_demo": True,
            },
            {
                "title": "رونمایی کالکشن هدیه",
                "description": "معرفی مجموعه جدید هدایا و ست‌های مناسبتی زاد.",
                "start_at": now + timedelta(days=14),
                "end_at": now + timedelta(days=14, hours=3),
                "location": "مشهد، فروشگاه زاد",
                "is_demo": True,
            },
        ]

    context.update(
        {
            "events": published_events,
            "lead_form": LeadRequestForm(
                initial_lead_type="event",
                include_event_fields=True,
            ),
            "lead_default_type": "event",
            "events_are_demo": events_are_demo,
        }
    )

    return render(request, "events.html", context)


def event_detail(request, slug: str):
    event = get_object_or_404(
        Event,
        slug=slug,
        status=PublishStatus.PUBLISHED,
    )

    breadcrumbs = _with_home(
        [
            {"name": "رویدادها", "url": reverse("events")},
            {"name": event.title, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="category",
        active_nav="events",
        meta_title=f"{event.title} | رویدادهای زاد",
        meta_description=f"جزئیات رویداد {event.title} در زاد: زمان برگزاری، مکان و هماهنگی حضور.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key(
        "events",
        title=event.title,
        text=event.description,
        image=event.cover_image.url if event.cover_image else "main/img/hero-events.jpg",
    )

    db_hero = _get_site_hero("events", event.slug)

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)

    event_schema = {
        "@context": "https://schema.org",
        "@type": "Event",
        "name": event.title,
        "description": event.description,
        "startDate": _event_to_iso(event.start_at),
        "endDate": _event_to_iso(event.end_at),
        "eventAttendanceMode": "https://schema.org/OfflineEventAttendanceMode",
        "eventStatus": "https://schema.org/EventScheduled",
        "location": {
            "@type": "Place",
            "name": "زاد",
            "address": event.location,
        },
        "organizer": {
            "@type": "Organization",
            "name": "زاد",
            "url": getattr(settings, "ZAAD_SITE_URL", "https://zaad.ir"),
        },
        "url": request.build_absolute_uri(event.get_absolute_url()),
    }

    if event.cover_image:
        event_schema["image"] = [request.build_absolute_uri(event.cover_image.url)]

    context.update(
        {
            "event": event,
            "lead_form": LeadRequestForm(
                initial_lead_type="event",
                include_event_fields=True,
            ),
            "lead_default_type": "event",
        }
    )

    context["extra_jsonld"].append(_jsonld(event_schema))

    return render(request, "event_detail.html", context)


# =========================
# Local SEO pages
# =========================

def mashhad_hub(request):
    curated_items = list(
        _published_products_for_section(Category.Section.FLOWERS).order_by(
            "-featured",
            "sort_order",
            "-created_at",
        )[:6]
    )

    breadcrumbs = _with_home([{"name": "سفارش در مشهد", "url": None}])

    context = _default_context(
        request,
        page_type="local",
        active_nav="mashhad",
        meta_title="سفارش در مشهد | زاد",
        meta_description="مرکز سفارش زاد در مشهد برای گل، ارسال سریع و هماهنگی فوری.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key("mashhad")
    db_hero = _get_site_hero("mashhad")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "curated_items": curated_items,
            "lead_form": LeadRequestForm(initial_lead_type="flower"),
            "lead_default_type": "flower",
        }
    )

    return render(request, "mashhad_hub.html", context)


def _local_landing(request, landing_type):
    if landing_type == "order":
        title = "سفارش گل در مشهد"
        subtitle = "انتخاب لوکس گل با هماهنگی سریع و دقیق"
        meta_title = "سفارش گل در مشهد | زاد"
        meta_description = "ثبت سفارش گل در مشهد با پاسخ سریع، طراحی پریمیوم و هماهنگی تلفنی یا واتساپ."
    elif landing_type == "delivery":
        title = "ارسال فوری گل در مشهد"
        subtitle = "تحویل سریع همان‌روز با استاندارد بسته‌بندی زاد"
        meta_title = "ارسال فوری گل در مشهد | زاد"
        meta_description = "ارسال فوری گل در مشهد با پشتیبانی تلفنی، زمان‌بندی دقیق و انتخاب‌های پیشنهادی امروز."
    else:
        raise Http404("Landing page not found")

    curated_items = list(
        _published_products_for_section(Category.Section.FLOWERS).order_by(
            "-featured",
            "sort_order",
            "-created_at",
        )[:8]
    )

    local_faq = [
        {
            "question": "سفارش فوری در کدام مناطق مشهد پوشش دارد؟",
            "answer": "بیشتر مناطق مرکزی و پرتردد مشهد در بازه کاری تحت پوشش ارسال فوری هستند.",
        },
        {
            "question": "چقدر قبل از زمان تحویل سفارش بدهم؟",
            "answer": "برای تحویل همان‌روز بهتر است حداقل ۲ تا ۳ ساعت زودتر هماهنگ کنید.",
        },
        {
            "question": "آیا عکس محصول قبل از ارسال فرستاده می‌شود؟",
            "answer": "در صورت درخواست، پیش از خروج سفارش امکان ارسال تصویر نهایی وجود دارد.",
        },
        {
            "question": "اگر آیتم انتخابی موجود نباشد چه می‌شود؟",
            "answer": "گزینه‌های نزدیک با همان سطح کیفیت پیشنهاد می‌شود و پس از تأیید شما ارسال انجام می‌گردد.",
        },
        {
            "question": "امکان هماهنگی تلفنی سریع دارید؟",
            "answer": "بله، دکمه تماس فوری برای هماهنگی مستقیم در تمام صفحات فعال است.",
        },
        {
            "question": "برای سفارش مناسبتی چه اطلاعاتی لازم است؟",
            "answer": "نوع مناسبت، زمان تحویل، بودجه تقریبی و آدرس کافی است تا پیشنهاد دقیق ارائه شود.",
        },
    ]

    breadcrumbs = _with_home(
        [
            {"name": "سفارش در مشهد", "url": reverse("mashhad_hub")},
            {"name": title, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="local",
        active_nav="mashhad",
        meta_title=meta_title,
        meta_description=meta_description,
        breadcrumbs=breadcrumbs,
        faq_items=local_faq,
    )

    hero_data = _hero_from_key("mashhad", title=title, text=subtitle)
    db_hero = _get_site_hero("mashhad")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)

    occasion_links = _occasion_links(limit=4)

    if not occasion_links:
        occasion_links = [
            _category_card(category)
            for category in _active_categories_for_section(Category.Section.FLOWERS)[:4]
        ]

    context.update(
        {
            "landing_title": title,
            "landing_subtitle": subtitle,
            "curated_items": curated_items,
            "why_zaad": [
                "طراحی لوکس و مینیمال مطابق مناسبت",
                "پاسخ‌گویی سریع و هماهنگی شفاف قبل از ارسال",
                "ارسال همان‌روز در محدوده‌های اصلی مشهد",
                "بسته‌بندی حرفه‌ای و مناسب هدیه",
            ],
            "occasion_links": occasion_links,
            "lead_form": LeadRequestForm(initial_lead_type="flower"),
            "lead_default_type": "flower",
        }
    )

    return render(request, "local_landing.html", context)


def mashhad_flower_order(request):
    return _local_landing(request, "order")


def mashhad_flower_delivery(request):
    return _local_landing(request, "delivery")


# =========================
# Static content pages
# =========================

def visit(request):
    breadcrumbs = _with_home([{"name": "بازدید حضوری", "url": None}])

    context = _default_context(
        request,
        page_type="contact",
        active_nav="",
        meta_title="بازدید حضوری فروشگاه زاد | مشهد",
        meta_description="آدرس، ساعت کاری و راهنمای بازدید حضوری فروشگاه زاد در مشهد.",
        breadcrumbs=breadcrumbs,
        faq_items=VISIT_FAQ,
    )

    hero_data = _hero_from_key("visit")
    db_hero = _get_site_hero("visit")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "lead_form": LeadRequestForm(initial_lead_type="flower"),
            "lead_default_type": "flower",
        }
    )

    return render(request, "visit.html", context)


def contact(request):
    breadcrumbs = _with_home([{"name": "تماس با ما", "url": None}])

    context = _default_context(
        request,
        page_type="contact",
        active_nav="",
        meta_title="تماس با زاد | هماهنگی سفارش و مشاوره",
        meta_description="برای سفارش یا مشاوره با زاد تماس بگیرید، در واتساپ پیام بدهید یا فرم کوتاه ثبت کنید.",
        breadcrumbs=breadcrumbs,
        faq_items=CONTACT_FAQ,
    )

    hero_data = _hero_from_key("contact")
    db_hero = _get_site_hero("contact")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "lead_form": LeadRequestForm(initial_lead_type="flower"),
            "lead_default_type": "flower",
        }
    )

    return render(request, "contact.html", context)


def faq(request):
    breadcrumbs = _with_home([{"name": "سوالات پرتکرار", "url": None}])

    context = _default_context(
        request,
        page_type="category",
        active_nav="",
        meta_title="سوالات پرتکرار | زاد",
        meta_description="پاسخ سوالات رایج درباره سفارش گل، ارسال سریع، ساعات کاری و هماهنگی رویداد در زاد.",
        breadcrumbs=breadcrumbs,
        faq_items=FAQ_PAGE_ITEMS,
    )

    hero_data = _hero_from_key("faq")
    db_hero = _get_site_hero("faq")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context["faq_page_items"] = FAQ_PAGE_ITEMS

    return render(request, "faq.html", context)


def about(request):
    breadcrumbs = _with_home([{"name": "درباره ما", "url": None}])

    context = _default_context(
        request,
        page_type="about",
        active_nav="about",
        meta_title="درباره ما | زاد",
        meta_description="آشنایی با زاد، فضای فروشگاه، روند آماده‌سازی سفارش و جزئیات برند.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key("about")
    db_hero = _get_site_hero("about")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)

    return render(request, "about.html", context)


# =========================
# Blog
# =========================

def blog(request):
    posts = list(
        NewsPost.objects.filter(
            status=PublishStatus.PUBLISHED,
        ).order_by("-published_at", "-created_at")
    )

    breadcrumbs = _with_home([{"name": "بلاگ", "url": None}])

    context = _default_context(
        request,
        page_type="category",
        active_nav="",
        meta_title="بلاگ زاد | ایده‌ها و راهنمای انتخاب",
        meta_description="مطالب بلاگ زاد درباره انتخاب گل، هدیه و برنامه‌ریزی مناسبت‌ها.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key("blog")
    db_hero = _get_site_hero("blog")

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context["posts"] = posts

    return render(request, "blog_list.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(
        NewsPost,
        slug=slug,
        status=PublishStatus.PUBLISHED,
    )

    recommended_items = list(
        _published_products()
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-featured", "sort_order", "-created_at")[:3]
    )

    flower_category = (
        Category.objects.filter(
            section=Category.Section.FLOWERS,
            is_active=True,
        )
        .order_by("sort_order", "name")
        .first()
    )

    recommended_subcategory = None

    if flower_category:
        recommended_subcategory = {
            "label": flower_category.name,
            "url": reverse("flower_subcategory", args=[flower_category.slug]),
        }

    breadcrumbs = _with_home(
        [
            {"name": "بلاگ", "url": reverse("blog")},
            {"name": post.title, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="category",
        active_nav="",
        meta_title=f"{post.title} | بلاگ زاد",
        meta_description=post.excerpt or "مطالعه مطلبی از بلاگ زاد.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key(
        "blog",
        title=post.title,
        text=post.excerpt or "مطالعه مطلبی از بلاگ زاد.",
        image=post.cover_image.url if post.cover_image else "main/img/hero-blog.jpg",
    )

    db_hero = _get_site_hero("blog", post.slug)

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "post": post,
            "recommended_category": {"label": "گل‌ها", "url": reverse("flowers")},
            "recommended_subcategory": recommended_subcategory,
            "recommended_items": recommended_items,
        }
    )

    return render(request, "blog_detail.html", context)


# =========================
# Leads
# =========================

@require_POST
def submit_lead_request(request):
    include_event_fields = request.POST.get("lead_type") == "event"
    form = LeadRequestForm(request.POST, include_event_fields=include_event_fields)

    next_url = (
        request.POST.get("next")
        or request.META.get("HTTP_REFERER")
        or reverse("index")
    )

    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
    ):
        next_url = reverse("index")

    if form.is_valid():
        lead = form.save(commit=False)
        lead.source_page = request.POST.get("source_page", "")
        lead.save()
        messages.success(request, "درخواست شما ثبت شد. به‌زودی با شما تماس می‌گیریم.")
    else:
        messages.error(request, "لطفاً اطلاعات فرم را کامل و صحیح وارد کنید.")

    return redirect(next_url)


# =========================
# SEO
# =========================

def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /auth/",
        "Disallow: /search/",
        f"Sitemap: {request.build_absolute_uri(reverse('sitemap'))}",
    ]

    return HttpResponse(
        "\n".join(lines),
        content_type="text/plain; charset=utf-8",
    )