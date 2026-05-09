import json
from datetime import timedelta
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
        "title": "Flowers",
        "nav": "flowers",
        "lead_type": "flower",
        "meta_title": "Luxury Flowers in Mashhad | ZAAD",
        "meta_description": "Fresh flowers, premium styling, and fast coordination in Mashhad.",
        "intro": "Premium ZAAD flowers with careful styling and fast coordination in Mashhad.",
        "faq": [
            {
                "question": "Do you offer same-day flower delivery in Mashhad?",
                "answer": "Yes. Same-day coordination is available for many orders during working hours.",
            },
            {
                "question": "Can I check today’s availability before ordering?",
                "answer": "Yes. Call ZAAD or message us on Telegram to check available pieces and similar options.",
            },
            {
                "question": "What should I choose for formal or sympathy occasions?",
                "answer": "Stands and formal arrangements can be coordinated based on the occasion and color palette.",
            },
            {
                "question": "Can I schedule an order for later?",
                "answer": "Yes. Orders can be coordinated for today, tomorrow, or a selected date.",
            },
        ],
    },
    "bakery": {
        "title": "Bakery",
        "nav": "bakery",
        "lead_type": "bakery",
        "meta_title": "Premium Bakery Orders in Mashhad | ZAAD",
        "meta_description": "Premium ZAAD bakery pieces for gifting, hosting, and daily coordination by phone or Telegram.",
        "intro": "ZAAD bakery pieces are made for hosting, gifting, and warm daily details.",
        "faq": [
            {
                "question": "Can I order bakery pieces for today?",
                "answer": "In many cases, yes. Availability depends on the day’s capacity.",
            },
            {
                "question": "Can bakery items be sent with flowers?",
                "answer": "Yes. Flowers and bakery pieces can be coordinated for one delivery time.",
            },
            {
                "question": "How should I order larger quantities?",
                "answer": "For larger or corporate orders, use the request form or call directly.",
            },
            {
                "question": "How fast does ZAAD respond?",
                "answer": "During working hours, the first response is usually quick.",
            },
        ],
    },
    "gifts": {
        "title": "Gifts",
        "nav": "gifts",
        "lead_type": "gift",
        "meta_title": "Curated Gifts & Concept Store | ZAAD Mashhad",
        "meta_description": "Minimal curated gifts, concept pieces, and gift coordination in Mashhad.",
        "intro": "Curated ZAAD gifts for thoughtful, minimal, and premium choices.",
        "faq": [],
    },
}


CATEGORY_CONTENT_OVERRIDES = {
    "bouquet": {
        "label": "Bouquets",
        "meta_title": "Luxury Bouquets in Mashhad | ZAAD",
        "meta_description": "Minimal and premium ZAAD bouquets with fast coordination in Mashhad.",
        "intro": "Softly made for gifting.",
        "image": "main/img/sub-bouquet.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "box": {
        "label": "Flower Boxes",
        "meta_title": "Flower Boxes in Mashhad | ZAAD",
        "meta_description": "Premium ZAAD flower boxes with elegant styling and quick coordination.",
        "intro": "Elegant and easy to gift.",
        "image": "main/img/sub-box.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "basket": {
        "label": "Flower Baskets",
        "meta_title": "Flower Baskets in Mashhad | ZAAD",
        "meta_description": "Special ZAAD flower baskets for gifting, events, and warm moments.",
        "intro": "Warm, full and beautifully arranged.",
        "image": "main/img/sub-plant.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "stand": {
        "label": "Stands & Wreaths",
        "meta_title": "Floral Stands & Wreaths in Mashhad | ZAAD",
        "meta_description": "Formal floral stands and wreaths with quick coordination in Mashhad.",
        "intro": "Thoughtful flowers for formal moments.",
        "image": "main/img/sub-stand.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "bridal-car-decoration": {
    "label": "Bridal Car Decoration",
    "meta_title": "Bridal Car Decoration | ZAAD",
    "meta_description": "ZAAD floral styling for bridal cars in Mashhad.",
    "intro": "Floral styling for bridal cars.",
    "image": "main/img/sub-bridal-car.jpg",
    "hero_image": "main/img/hero-subcategory.jpg",
    },
    "bridal-bouquet": {
        "label": "Bridal Bouquet",
        "meta_title": "Bridal Bouquet | ZAAD",
        "meta_description": "ZAAD bridal bouquets with elegant floral styling in Mashhad.",
        "intro": "Soft bridal bouquets for wedding moments.",
        "image": "main/img/sub-bridal-bouquet.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "birthday-cakes": {
        "label": "Birthday Cakes",
        "meta_title": "Birthday Cakes | ZAAD",
        "meta_description": "ZAAD birthday cakes for warm celebrations and soft moments.",
        "intro": "Soft cakes for warm birthday moments.",
        "image": "main/img/sub-birthday-cakes.jpg",
        "hero_image": "main/img/hero-subcategory.jpg",
    },
    "cookies": {
        "label": "Cookies",
        "meta_title": "Cookies | ZAAD",
        "meta_description": "ZAAD cookies for gifting, gatherings and sweet little details.",
        "intro": "Small sweet bites for gentle celebrations.",
        "image": "main/img/sub-cookies.jpg",
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
        "title": "Choose the Mood",
        "text": "Soft choices for the feeling you want to send.",
        "image": "main/img/hero-occasions.jpg",
    },
    "flowers": {
        "kicker": "ZAAD Flowers",
        "title": "For Every Feeling",
        "text": "Flowers for love, care and quiet beautiful moments.",
        "image": "main/img/hero-flowers.jpg",
    },
    "bakery": {
        "kicker": "ZAAD Bakery",
        "title": "Sweet Little Rituals",
        "text": "Small sweet pieces for warmer celebrations.",
        "image": "main/img/hero-bakery.jpg",
    },
    "gifts": {
        "kicker": "ZAAD Gifts",
        "title": "Chosen With Care",
        "text": "Little gifts with warmth, softness and meaning.",
        "image": "main/img/hero-gifts.jpg",
    },
    "subcategory": {
        "kicker": "ZAAD Collection",
        "title": "Curated Softly",
        "text": "A smaller selection for a more exact feeling.",
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
        "title": "Let’s Arrange It",
        "text": "For availability, timing and order details.",
        "image": "main/img/hero-contact.jpg",
    },
    "visit": {
        "kicker": "Visit ZAAD",
        "title": "Come Closer",
        "text": "See the details and choose with more ease.",
        "image": "main/img/hero-visit.jpg",
    },
    "events": {
        "kicker": "ZAAD Events",
        "title": "Gathered With Feeling",
        "text": "Workshops, gatherings and soft ZAAD experiences.",
        "image": "main/img/hero-events.jpg",
    },
    "blog": {
        "kicker": "ZAAD Journal",
        "title": "Soft Notes",
        "text": "Small ideas for flowers, gifts and moments.",
        "image": "main/img/hero-blog.jpg",
    },
    "faq": {
        "kicker": "ZAAD Help",
        "title": "Little Answers",
        "text": "Simple answers before you call or order.",
        "image": "main/img/hero-faq.jpg",
    },
    "mashhad": {
        "kicker": "ZAAD Mashhad",
        "title": "Made for Mashhad",
        "text": "Fast coordination for special orders in Mashhad.",
        "image": "main/img/hero-mashhad.jpg",
    },
    "about": {
        "kicker": "ZAAD Concept Store",
        "title": "The Story of ZAAD",
        "text": "A closer look at the care behind the brand.",
        "image": "main/img/hero-about.jpg",
    },
}


HOME_FAQ = [
    {
        "question": "What can I order from ZAAD?",
        "answer": "Flowers, bakery pieces, curated gifts, and event coordination are available through ZAAD.",
    },
    {
        "question": "Do you offer same-day delivery in Mashhad?",
        "answer": "Yes. Many orders can be coordinated for same-day delivery depending on availability.",
    },
    {
        "question": "What is the fastest way to coordinate an order?",
        "answer": "Calling ZAAD is the fastest path. Telegram is available as the second option.",
    },
    {
        "question": "How do I start an event order?",
        "answer": "Use the events page or the request form and share the date, location, and request type.",
    },
]


VISIT_FAQ = [
    {
        "question": "Should I coordinate before visiting?",
        "answer": "For special orders, it is better to call before visiting so the team can prepare faster.",
    },
    {
        "question": "What are ZAAD’s opening hours?",
        "answer": "ZAAD is available every day from 10:00 to 22:00 unless announced otherwise.",
    },
    {
        "question": "What can I do during an in-person visit?",
        "answer": "You can review samples, receive guidance, and coordinate pickup or delivery.",
    },
    {
        "question": "Can I choose flowers and gifts together?",
        "answer": "Yes. ZAAD can suggest flower and gift combinations for the same occasion.",
    },
]


CONTACT_FAQ = [
    {
        "question": "How fast does ZAAD respond?",
        "answer": "During working hours, the first response is usually quick.",
    },
    {
        "question": "How can I place an order?",
        "answer": "Call ZAAD, message on Telegram, or submit the short request form.",
    },
    {
        "question": "What information is needed for urgent orders?",
        "answer": "Name, mobile number, request type, delivery window, and a short note are enough to start.",
    },
    {
        "question": "Do you deliver outside Mashhad?",
        "answer": "The current focus is Mashhad, but special requests can be reviewed case by case.",
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
    return [{"name": "Home", "url": reverse("index")}, *items]


def _telegram_href():
    return getattr(settings, "ZAAD_TELEGRAM_URL", "https://t.me/zaad_store")


def _item_telegram_href(request, product):
    return _telegram_href()


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
        "brand": {"@type": "Brand", "name": "ZAAD"},
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
        "page_hero_title": title or hero.get("title", "ZAAD"),
        "page_hero_text": text or hero.get("text", "A thoughtful ZAAD selection for flowers, gifts, and special orders"),
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
            "title": "Flowers, Bakery & Gifts in Mashhad",
            "kicker": "ZAAD Concept Store",
            "description": "Premium flowers, bakery, and gifts with fast coordination in Mashhad.",
            "image_url": settings.STATIC_URL + "main/img/hero-1.jpg",
            "primary_button_text": "Call Now",
            "primary_button_url": "",
            "secondary_button_text": "Telegram",
            "secondary_button_url": "",
        },
        {
            "title": "Styled Details for Special Moments",
            "kicker": "Minimal & Premium",
            "description": "A polished ZAAD experience across flowers, bakery, and gifts.",
            "image_url": settings.STATIC_URL + "main/img/hero-2.jpg",
            "primary_button_text": "",
            "primary_button_url": "",
            "secondary_button_text": "",
            "secondary_button_url": "",
        },
        {
            "title": "Fast Coordination in Mashhad",
            "kicker": "ZAAD Mashhad",
            "description": "Quick coordination for urgent orders and daily selections.",
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
        "meta_title": override.get("meta_title") or f"{category.name} | ZAAD",
        "meta_description": (
            override.get("meta_description")
            or category.description
            or f"Explore {category.name} products at ZAAD."
        ),
        "intro": override.get("intro") or category.description or "A curated selection for this mood.",
        "image": override.get("image") or "main/img/sub-bouquet.jpg",
        "hero_image": override.get("hero_image") or "main/img/hero-subcategory.jpg",
    }


SECTION_ALL_ROUTE_NAMES = {
    Category.Section.FLOWERS: "flowers_all",
    Category.Section.BAKERY: "bakery_all",
    Category.Section.GIFTS: "gifts_all",
}

SECTION_CATEGORY_ROUTE_NAMES = {
    Category.Section.FLOWERS: "flower_subcategory",
    Category.Section.BAKERY: "bakery_subcategory",
    Category.Section.GIFTS: "gift_subcategory",
}

OCCASION_CARD_CONTENT = {
    "birthday": {
        "title": "Birthday",
        "hero_title": "Birthday Mood",
        "intro": "A soft little joy for a beautiful birthday.",
        "image": "main/img/occasions/birthday.jpg",
    },
    "romantic": {
        "title": "Romantic",
        "hero_title": "Romantic Mood",
        "intro": "For words that feel softer with flowers.",
        "image": "main/img/occasions/romantic.jpg",
    },
    "apology": {
        "title": "Apology",
        "hero_title": "Gentle Apology",
        "intro": "A quiet way to say sorry with care.",
        "image": "main/img/occasions/apology.jpg",
    },
    "condolence": {
        "title": "Condolence",
        "hero_title": "Quiet Sympathy",
        "intro": "Graceful flowers for difficult moments.",
        "image": "main/img/occasions/condolence.jpg",
    },
    "special": {
        "title": "Special",
        "hero_title": "Something Special",
        "intro": "For moments that need a little more care.",
        "image": "main/img/occasions/special.jpg",
    },
    "wedding": {
        "title": "Wedding",
        "hero_title": "Wedding Flowers",
        "intro": "Soft floral details for bridal moments.",
        "image": "main/img/occasions/wedding.jpg",
    },
}


def _section_all_url(section):
    route_name = SECTION_ALL_ROUTE_NAMES.get(section)

    if route_name:
        return reverse(route_name)

    return reverse(section)


def _section_category_url(category):
    route_name = SECTION_CATEGORY_ROUTE_NAMES.get(category.section)

    if route_name:
        return reverse(route_name, args=[category.slug])

    return reverse(category.section)


def _category_card(category):
    content = _category_content(category)

    return {
        "slug": category.slug,
        "label": category.name,
        "url": _section_category_url(category),
        "image": category.cover_image.url if category.cover_image else content["image"],
        "intro": category.description or content["intro"],
    }


def _occasion_card(tag, *, for_flowers=False):
    content = OCCASION_CARD_CONTENT.get(tag.slug, {})
    url_name = "flower_occasion" if for_flowers else "occasion_detail"

    return {
        "slug": tag.slug,
        "label": content.get("title") or tag.name,
        "url": reverse(url_name, args=[tag.slug]),
        "image": tag.cover_image.url if tag.cover_image else content.get("image", "main/img/occasions/special.jpg"),
        "intro": tag.description or content.get("intro", "Curated ideas for this occasion."),
    }


def _active_occasion_tags(limit=None):
    queryset = Tag.objects.filter(
        is_occasion=True,
        is_active=True,
    ).order_by("sort_order", "name")

    if limit:
        queryset = queryset[:limit]

    return list(queryset)


def _occasion_links(limit=4):
    return [
        {
            "label": tag.name,
            "url": reverse("occasion_detail", args=[tag.slug]),
        }
        for tag in _active_occasion_tags(limit=limit)
    ]


def _featured_selection(queryset, limit=10):
    featured = list(queryset.filter(featured=True)[:limit])

    if len(featured) >= limit:
        return featured

    excluded_ids = [item.pk for item in featured]
    fallback = list(queryset.exclude(pk__in=excluded_ids)[: limit - len(featured)])

    return featured + fallback


def _filter_links_for_categories(base_url, categories, selected_slug=None):
    links = [
        {
            "label": "All",
            "url": base_url,
            "is_active": not selected_slug,
        }
    ]

    for category in categories:
        links.append(
            {
                "label": category.name,
                "url": f"{base_url}?category={category.slug}",
                "is_active": selected_slug == category.slug,
            }
        )

    return links


# =========================
# Home
# =========================

def index(request):
    legacy_section = (request.GET.get("section") or "").lower()

    if legacy_section in SECTION_CONTENT:
        return redirect(legacy_section)

    def pick_home_products(section, limit=2):
        return list(
            _published_products()
            .filter(category__section=section)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-featured", "sort_order", "-created_at")[:limit]
        )

    featured_today = (
        pick_home_products(Category.Section.FLOWERS, 2)
        + pick_home_products(Category.Section.BAKERY, 2)
        + pick_home_products(Category.Section.GIFTS, 2)
    )

    if len(featured_today) < 6:
        used_ids = [product.id for product in featured_today]

        fallback_products = list(
            _published_products()
            .exclude(id__in=used_ids)
            .select_related("category")
            .prefetch_related("tags")
            .order_by("-featured", "sort_order", "-created_at")[: 6 - len(featured_today)]
        )

        featured_today += fallback_products

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
        meta_title="ZAAD | Flowers, Bakery & Gifts in Mashhad",
        meta_description="ZAAD Concept Store in Mashhad for flowers, bakery, gifts, events, and fast coordination.",
        faq_items=HOME_FAQ,
    )

    context.update(
        {
            "featured_today": featured_today,
            "occasion_tags": occasion_tags,
            "sections": SECTION_CONTENT,
            "hero_call_text": "Call Now",
            "hero_telegram_text": "Telegram",
            "home_subtitle": "Premium flowers, bakery, and gifts with fast coordination in Mashhad",
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

    products_qs = _published_products_for_section(section)

    if section == Category.Section.FLOWERS:
        products_qs = products_qs.exclude(tags__slug="condolence").distinct()

    products_qs = products_qs.order_by(
    "-featured",
    "sort_order",
    "-created_at",
)

    featured_items = _featured_selection(products_qs, limit=10)

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

    occasion_cards = []
    subcategory_links = []

    if section == Category.Section.FLOWERS:
        occasion_cards = [
            _occasion_card(tag, for_flowers=True)
            for tag in _active_occasion_tags(limit=8)
        ]
    else:
        subcategory_links = [
            _category_card(category)
            for category in _active_categories_for_section(section)
        ]

    context.update(
        {
            "section": section,
            "section_title": config["title"],
            "section_intro": config["intro"],
            "featured_items": featured_items,
            "occasion_cards": occasion_cards,
            "subcategory_links": subcategory_links,
            "section_more_url": _section_all_url(section),
            "featured_title": "Our Selection",
            "lead_form": LeadRequestForm(initial_lead_type=config["lead_type"]),
            "lead_default_type": config["lead_type"],
            "category_call_text": "Call for Guidance",
            "category_telegram_text": "Telegram",
        }
    )

    return render(request, "category.html", context)


def flowers(request):
    return _category_page(request, Category.Section.FLOWERS)


def bakery(request):
    return _category_page(request, Category.Section.BAKERY)


def gifts(request):
    return _category_page(request, Category.Section.GIFTS)


def _section_all_products(request, section):
    config = SECTION_CONTENT[section]
    products_qs = _published_products_for_section(section).order_by(
        "-featured",
        "sort_order",
        "-created_at",
    )

    categories = list(_active_categories_for_section(section))
    selected_category = None
    selected_slug = request.GET.get("category") or ""

    if selected_slug:
        selected_category = get_object_or_404(
            Category,
            section=section,
            slug=selected_slug,
            is_active=True,
        )
        products_qs = products_qs.filter(category=selected_category)

    items = list(products_qs[:48])
    title = config["title"]

    if selected_category:
        title = f"{config['title']} / {selected_category.name}"

    breadcrumbs = _with_home(
        [
            {"name": config["title"], "url": reverse(section)},
            {"name": "All Products", "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="subcategory",
        active_nav=config["nav"],
        meta_title=f"{title} | ZAAD",
        meta_description=f"View all {config['title']} products at ZAAD.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key(
        section,
        title=title,
        text="Explore all active products in this section.",
    )

    db_hero = _get_site_hero(section)

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "collection_title": title,
            "collection_intro": config["intro"],
            "items": items,
            "filter_links": _filter_links_for_categories(
                _section_all_url(section),
                categories,
                selected_slug=selected_slug,
            ),
            "related_posts": [],
            "lead_form": LeadRequestForm(initial_lead_type=config["lead_type"]),
            "lead_default_type": config["lead_type"],
        }
    )

    return render(request, "subcategory.html", context)


def flowers_all(request):
    return _section_all_products(request, Category.Section.FLOWERS)


def bakery_all(request):
    return _section_all_products(request, Category.Section.BAKERY)


def gifts_all(request):
    return _section_all_products(request, Category.Section.GIFTS)





def _section_subcategory(request, section, subcategory_slug):
    category = get_object_or_404(
        Category,
        section=section,
        slug=subcategory_slug,
        is_active=True,
    )

    config = SECTION_CONTENT[section]
    content = _category_content(category)

    items = list(
        _published_products()
        .filter(category=category)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("-featured", "sort_order", "-created_at")[:48]
    )

    related_posts = list(
        NewsPost.objects.filter(status=PublishStatus.PUBLISHED).order_by(
            "-published_at",
            "-created_at",
        )[:3]
    )

    breadcrumbs = _with_home(
        [
            {"name": config["title"], "url": reverse(section)},
            {"name": category.name, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="subcategory",
        active_nav=config["nav"],
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
            "collection_title": category.name,
            "collection_intro": content["intro"],
            "items": items,
            "related_posts": related_posts if section == Category.Section.FLOWERS else [],
            "lead_form": LeadRequestForm(initial_lead_type=config["lead_type"]),
            "lead_default_type": config["lead_type"],
        }
    )

    return render(request, "subcategory.html", context)


def flower_subcategory(request, subcategory_slug):
    canonical_slug = CATEGORY_SLUG_ALIASES.get(subcategory_slug, subcategory_slug)

    if canonical_slug != subcategory_slug:
        return redirect("flower_subcategory", subcategory_slug=canonical_slug)

    return _section_subcategory(request, Category.Section.FLOWERS, canonical_slug)


def bakery_subcategory(request, subcategory_slug):
    return _section_subcategory(request, Category.Section.BAKERY, subcategory_slug)


def gift_subcategory(request, subcategory_slug):
    return _section_subcategory(request, Category.Section.GIFTS, subcategory_slug)


def flower_occasion(request, slug):
    occasion = get_object_or_404(
        Tag,
        slug=slug,
        is_occasion=True,
        is_active=True,
    )

    card = OCCASION_CARD_CONTENT.get(occasion.slug, {})

    base_products_qs = (
        _published_products_for_section(Category.Section.FLOWERS)
        .filter(tags=occasion)
        .order_by("-featured", "sort_order", "-created_at")
    )

    available_category_ids = list(
        base_products_qs.values_list("category_id", flat=True).distinct()
    )

    available_categories = list(
        Category.objects.filter(
            pk__in=available_category_ids,
            is_active=True,
        ).order_by("sort_order", "name")
    )

    selected_slug = request.GET.get("category") or ""
    selected_category = None
    products_qs = base_products_qs

    if selected_slug:
        selected_category = get_object_or_404(
            Category,
            section=Category.Section.FLOWERS,
            slug=selected_slug,
            is_active=True,
            pk__in=available_category_ids,
        )
        products_qs = products_qs.filter(category=selected_category)

    products = list(products_qs[:48])
    suggested_sections = []

    for suggestion_section, title in (
        (Category.Section.BAKERY, "Matching Bakery"),
        (Category.Section.GIFTS, "Complementary Gifts"),
    ):
        section_products = list(
            _published_products_for_section(suggestion_section)
            .filter(tags=occasion)
            .order_by("-featured", "sort_order", "-created_at")[:6]
        )

        if section_products:
            suggested_sections.append(
                {
                    "title": title,
                    "products": section_products,
                    "more_url": reverse("occasion_detail", args=[occasion.slug]),
                }
            )

    title = card.get("hero_title") or f"{occasion.name} Flowers"

    if selected_category:
        title = f"{selected_category.name} / {card.get('title') or occasion.name}"

    breadcrumbs = _with_home(
        [
            {"name": "Flowers", "url": reverse("flowers")},
            {"name": occasion.name, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="flower-occasion",
        active_nav="flowers",
        meta_title=f"{title} | ZAAD",
        meta_description=f"View {title} at ZAAD with fast order coordination.",
        breadcrumbs=breadcrumbs,
    )

    context.update(
        _hero_from_key(
            "flowers",
            title=title,
            text=occasion.description or card.get("intro", "A soft ZAAD selection for this mood."),
            image=card.get("image", "main/img/hero-flowers.jpg"),
        )
    )

    db_hero = _get_site_hero("occasions", occasion.slug)

    if db_hero:
        context.update(db_hero)

    base_url = reverse("flower_occasion", args=[occasion.slug])

    context.update(
        {
            "occasion": occasion,
            "products": products,
            "filter_links": _filter_links_for_categories(
                base_url,
                available_categories,
                selected_slug=selected_slug,
            ),
            "selected_category": selected_category,
            "suggested_sections": suggested_sections,
            "global_occasion_url": reverse("occasion_detail", args=[occasion.slug]),
            "is_flower_occasion": True,
        }
    )

    return render(request, "occasion_detail.html", context)


# =========================
# Product detail
# =========================

def _item_detail_context(request, product):
    category = product.category
    category_name = category.name if category else "Product"
    section = category.section if category else ""
    active_nav = section if section in SECTION_CONTENT else ""

    subcategory_url = None
    subcategory_label = None

    if category and category.section in SECTION_CATEGORY_ROUTE_NAMES:
        subcategory_url = _section_category_url(category)
        subcategory_label = category.name

    breadcrumbs = [{"name": "Home", "url": reverse("index")}]

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
        else "Call ZAAD for availability, delivery timing, and order coordination."
    )

    context = _default_context(
        request,
        page_type="item",
        active_nav=active_nav,
        meta_title=f"{product.name} | ZAAD",
        meta_description=f"View {product.name} at ZAAD. Call for availability, delivery timing, and order coordination.",
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
            "section_label": SECTION_CONTENT[section]["nav"].title() if section in SECTION_CONTENT else "Collection",
            "category_url": reverse(section) if section in SECTION_CONTENT else reverse("index"),
            "subcategory_url": subcategory_url,
            "subcategory_label": subcategory_label,
            "similar_items": similar_items,
            "item_telegram_href": _item_telegram_href(request, product),
            "item_call_text": "Call",
            "item_telegram_text": "Telegram",
            "mashhad_order_url": reverse("mashhad_flower_order"),
        }
    )

    context["extra_jsonld"].append(_jsonld(_product_jsonld(request, product)))

    return context


def product_detail(request, pk: int, slug: str):
    product = get_object_or_404(
        _published_products().select_related("category").prefetch_related("tags", "gallery_images"),
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
        .prefetch_related("tags", "gallery_images"),
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
    occasion_tags = _active_occasion_tags(limit=12)
    occasion_cards = [_occasion_card(tag) for tag in occasion_tags]

    breadcrumbs = _with_home(
        [
            {
                "name": "Occasions",
                "url": None,
            }
        ]
    )

    context = _default_context(
        request,
        page_type="occasions",
        active_nav="occasions",
        meta_title="Occasions | ZAAD",
        meta_description="Explore ZAAD flowers, bakery, and gifts by occasion.",
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
            "occasion_cards": occasion_cards,
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

    card = OCCASION_CARD_CONTENT.get(occasion.slug, {})

    products = list(
        _published_products()
        .filter(tags=occasion)
        .select_related("category")
        .prefetch_related("tags")
        .order_by("category__section", "-featured", "sort_order", "-created_at")[:48]
    )

    suggested_sections = []

    for section, title in (
        (Category.Section.FLOWERS, "Flowers for this Mood"),
        (Category.Section.BAKERY, "Matching Bakery"),
        (Category.Section.GIFTS, "Complementary Gifts"),
    ):
        section_products = [
            product
            for product in products
            if product.category and product.category.section == section
        ][:8]

        if section_products:
            suggested_sections.append(
                {
                    "title": title,
                    "products": section_products,
                    "more_url": reverse(section) if section in SECTION_CONTENT else None,
                }
            )

    breadcrumbs = _with_home(
        [
            {
                "name": "Occasions",
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
        meta_title=f"{occasion.name} | ZAAD",
        meta_description=f"ZAAD suggestions for {occasion.name}.",
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
                "page_hero_text": occasion.description or card.get("intro", "Curated selections for this mood."),
                "page_hero_image": card.get("image", "main/img/hero-occasions.jpg"),
            }
        )

    context.update(
        {
            "occasion": occasion,
            "products": products,
            "suggested_sections": suggested_sections,
            "is_flower_occasion": False,
            "flower_occasion_url": reverse("flower_occasion", args=[occasion.slug]),
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

    breadcrumbs = _with_home([{"name": "Events", "url": None}])

    context = _default_context(
        request,
        page_type="category",
        active_nav="events",
        meta_title="ZAAD Events | Workshops & Experiences",
        meta_description="ZAAD events in Mashhad for workshops, launches, and in-person experiences.",
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
                "title": "Floral Styling Workshop",
                "description": "A short floral styling session with a minimal ZAAD approach.",
                "start_at": now + timedelta(days=7),
                "end_at": now + timedelta(days=7, hours=2),
                "location": "ZAAD Store, Mashhad",
                "is_demo": True,
            },
            {
                "title": "Gift Collection Preview",
                "description": "A preview of ZAAD’s new curated gifts and occasion sets.",
                "start_at": now + timedelta(days=14),
                "end_at": now + timedelta(days=14, hours=3),
                "location": "ZAAD Store, Mashhad",
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
            {"name": "Events", "url": reverse("events")},
            {"name": event.title, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="category",
        active_nav="events",
        meta_title=f"{event.title} | ZAAD Events",
        meta_description=f"Details for {event.title} at ZAAD: time, location, and visit coordination.",
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
            "name": "ZAAD",
            "address": event.location,
        },
        "organizer": {
            "@type": "Organization",
            "name": "ZAAD",
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

    breadcrumbs = _with_home([{"name": "Mashhad Orders", "url": None}])

    context = _default_context(
        request,
        page_type="local",
        active_nav="mashhad",
        meta_title="Mashhad Orders | ZAAD",
        meta_description="ZAAD Mashhad order hub for flowers, same-day delivery, and fast coordination.",
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
        title = "Flower Orders in Mashhad"
        subtitle = "Premium flower selection with fast, clear coordination."
        meta_title = "Flower Orders in Mashhad | ZAAD"
        meta_description = "Flower orders in Mashhad with quick response, premium styling, and phone coordination."
    elif landing_type == "delivery":
        title = "Same-day Flower Delivery"
        subtitle = "Same-day delivery with ZAAD packaging standards."
        meta_title = "Same-day Flower Delivery in Mashhad | ZAAD"
        meta_description = "Same-day flower delivery in Mashhad with phone support and curated daily options."
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
            "question": "Which Mashhad areas are covered for urgent orders?",
            "answer": "Most central and high-demand areas are covered during working hours.",
        },
        {
            "question": "How early should I coordinate?",
            "answer": "For same-day delivery, it is better to coordinate at least 2–3 hours ahead.",
        },
        {
            "question": "Can I see the final item before delivery?",
            "answer": "When requested, the final image can be coordinated before dispatch.",
        },
        {
            "question": "What happens if my selected item is unavailable?",
            "answer": "Similar options with the same quality level will be suggested before delivery.",
        },
        {
            "question": "Can I coordinate quickly by phone?",
            "answer": "Yes. The call button is available across the site for direct coordination.",
        },
        {
            "question": "What do you need for an occasion order?",
            "answer": "Occasion type, delivery time, approximate budget, and address are enough to start.",
        },
    ]

    breadcrumbs = _with_home(
        [
            {"name": "Mashhad Orders", "url": reverse("mashhad_hub")},
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
                "Premium, minimal styling for the occasion",
                "Fast response and clear coordination before delivery",
                "Same-day delivery in key Mashhad areas",
                "Professional, gift-ready packaging",
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
    breadcrumbs = _with_home([{"name": "Visit ZAAD", "url": None}])

    context = _default_context(
        request,
        page_type="contact",
        active_nav="",
        meta_title="Visit ZAAD | Mashhad",
        meta_description="Address, opening hours, and visit coordination for ZAAD in Mashhad.",
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
    breadcrumbs = _with_home([{"name": "Contact", "url": None}])

    context = _default_context(
        request,
        page_type="contact",
        active_nav="",
        meta_title="Contact ZAAD | Order Coordination",
        meta_description="Contact ZAAD for ordering, guidance, availability, and delivery timing.",
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
    breadcrumbs = _with_home([{"name": "FAQ", "url": None}])

    context = _default_context(
        request,
        page_type="category",
        active_nav="",
        meta_title="FAQ | ZAAD",
        meta_description="Common questions about ZAAD orders, delivery, opening hours, and event coordination.",
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
    breadcrumbs = _with_home([{"name": "About", "url": None}])

    context = _default_context(
        request,
        page_type="about",
        active_nav="about",
        meta_title="About ZAAD",
        meta_description="A closer look at ZAAD, the store experience, order preparation, and brand details.",
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

    breadcrumbs = _with_home([{"name": "Journal", "url": None}])

    context = _default_context(
        request,
        page_type="category",
        active_nav="",
        meta_title="ZAAD Journal | Ideas & Guides",
        meta_description="ZAAD journal notes about flowers, gifts, and occasion planning.",
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
            {"name": "Journal", "url": reverse("blog")},
            {"name": post.title, "url": None},
        ]
    )

    context = _default_context(
        request,
        page_type="category",
        active_nav="",
        meta_title=f"{post.title} | ZAAD Journal",
        meta_description=post.excerpt or "Read a note from the ZAAD Journal.",
        breadcrumbs=breadcrumbs,
    )

    hero_data = _hero_from_key(
        "blog",
        title=post.title,
        text=post.excerpt or "Read a note from the ZAAD Journal.",
        image=post.cover_image.url if post.cover_image else "main/img/hero-blog.jpg",
    )

    db_hero = _get_site_hero("blog", post.slug)

    if db_hero:
        hero_data = db_hero

    context.update(hero_data)
    context.update(
        {
            "post": post,
            "recommended_category": {"label": "Flowers", "url": reverse("flowers")},
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
        messages.success(request, "Your request has been submitted. ZAAD will contact you soon.")
    else:
        messages.error(request, "Please complete the form correctly and try again.")

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