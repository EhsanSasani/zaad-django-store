import json
from datetime import timedelta
from urllib.parse import quote

from django.conf import settings
from django.contrib import messages
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from .forms import LeadRequestForm
from .models import Event, Flower, NewsPost, Product, PublishStatus


SECTION_CONTENT = {
    "flowers": {
        "title": "گل‌های زاد",
        "nav": "flowers",
        "lead_type": "flower",
        "meta_title": "سفارش گل لوکس در مشهد | زاد",
        "meta_description": "گل‌های تازه، طراحی لوکس و ارسال فوری در مشهد. برای سفارش تلفنی یا واتساپ با زاد هماهنگ کنید.",
        "intro": "گل‌های زاد برای هدیه و مناسبت با تمرکز روی تازگی، هارمونی رنگ و ارائه لوکس آماده می‌شوند. هر سفارش قبل از ارسال از نظر کیفیت و بسته‌بندی بررسی می‌شود تا تجربه‌ای دقیق و قابل اعتماد داشته باشید. اگر زمان شما محدود است، می‌توانید موجودی امروز را سریع استعلام بگیرید و برای ارسال همان‌روز در محدوده‌های اصلی مشهد هماهنگ کنید.",
        "faq": [
            {
                "question": "آیا امکان ارسال فوری گل در مشهد دارید؟",
                "answer": "بله، برای سفارش‌های همان‌روز در بازه کاری، ارسال فوری در بیشتر مناطق مشهد انجام می‌شود.",
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
        "intro": "بیکری زاد برای سفارش‌هایی طراحی شده که هم کیفیت طعم و هم ظاهر ارائه اهمیت دارد. محصولات روزانه با انتخاب مواد اولیه مناسب آماده می‌شوند و می‌توانند به‌صورت مستقل یا همراه سفارش گل ارسال شوند. برای ثبت سریع، بهتر است ابتدا موجودی همان روز و بازه آماده‌سازی را استعلام کنید تا انتخاب نهایی با زمان تحویل شما کاملاً هماهنگ باشد.",
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
        "intro": "هدیه‌های کانسپت‌استور زاد برای انتخابی مینیمال، کاربردی و در عین حال لوکس گردآوری شده‌اند. این بخش برای مناسبت‌های شخصی و سازمانی طراحی شده تا بتوانید با زمان کم، گزینه‌ای دقیق پیدا کنید. اگر نیاز به ست هدیه همراه گل دارید، تیم زاد ترکیب‌های هماهنگ را پیشنهاد می‌دهد و زمان تحویل را متناسب با برنامه شما نهایی می‌کند.",
        "faq": [],
    },
}

FLOWER_SUBCATEGORIES = {
    "bouquet": {
        "label": "دسته‌گل",
        "pack_types": [Flower.PackType.BOUQUET],
        "meta_title": "دسته‌گل لوکس در مشهد | زاد",
        "meta_description": "دسته‌گل‌های مینیمال و پریمیوم زاد با امکان ارسال فوری در مشهد.",
        "intro": "دسته‌گل‌های این بخش برای هدیه، قرار رسمی و مناسبت‌های روزمره طراحی شده‌اند. تمرکز زاد روی هارمونی رنگ و تازگی گل است تا نتیجه نهایی حرفه‌ای و شیک بماند.",
    },
    "box": {
        "label": "باکس گل",
        "pack_types": [Flower.PackType.BOX],
        "meta_title": "باکس گل خاص در مشهد | زاد",
        "meta_description": "باکس‌گل‌های ویژه زاد با طراحی لوکس و هماهنگی تحویل سریع.",
        "intro": "باکس‌گل‌های زاد انتخابی مناسب برای هدیه رسمی و سورپرایزهای روزانه است. هر باکس با چیدمان دقیق و بسته‌بندی تمیز آماده می‌شود.",
    },
    "stand": {
        "label": "استند و تاج",
        "pack_types": [Flower.PackType.STAND],
        "meta_title": "استند گل و تاج ترحیم در مشهد | زاد",
        "meta_description": "استند و تاج گل رسمی با هماهنگی سریع برای مراسم در مشهد.",
        "intro": "برای مراسم رسمی و ترحیم، استند و تاج گل با طراحی متناسب و رنگ‌بندی محترمانه آماده می‌شود. قبل از ارسال، جزئیات متن یا سبک موردنظر شما هماهنگ می‌گردد.",
    },
    "plant": {
        "label": "گیاه",
        "pack_types": [Flower.PackType.STEM, Flower.PackType.BASKET],
        "meta_title": "گیاه آپارتمانی و هدیه سبز در مشهد | زاد",
        "meta_description": "گیاه‌های منتخب برای هدیه یا دکور فضای داخلی با هماهنگی ارسال در مشهد.",
        "intro": "این بخش برای انتخاب گیاه‌های کاربردی و زیبا در فضای خانه یا محل کار طراحی شده است. گزینه‌ها بر اساس نگهداری آسان و ظاهر لوکس انتخاب می‌شوند.",
    },
}

HOME_FAQ = [
    {
        "question": "زاد در چه حوزه‌هایی سفارش می‌پذیرد؟",
        "answer": "گل، بیکری، هدیه و خدمات مرتبط با رویدادها در زاد ارائه می‌شود.",
    },
    {
        "question": "آیا ارسال همان‌روز در مشهد دارید؟",
        "answer": "بله، برای بخش زیادی از سفارش‌ها امکان ارسال فوری همان‌روز وجود دارد.",
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
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": items}


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
    }

    if breadcrumbs:
        context["breadcrumbs"] = breadcrumbs
        context["breadcrumbs_jsonld"] = _jsonld(_breadcrumbs_jsonld(request, breadcrumbs))

    if faq_items:
        context["faq_items"] = faq_items
        context["faq_jsonld"] = _jsonld(_faq_jsonld(faq_items))

    return context


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
    schema = {
        "@context": "https://schema.org",
        "@type": "Product",
        "name": product.name,
        "brand": {"@type": "Brand", "name": "زاد"},
        "offers": {
            "@type": "Offer",
            "priceCurrency": "IRR",
            "price": str(product.price or 0),
            "availability": _stock_to_schema(product.stock_status),
            "url": request.build_absolute_uri(product.get_absolute_url()),
        },
    }
    if product.cover:
        schema["image"] = [request.build_absolute_uri(product.cover.url)]
    return schema


def _event_to_iso(dt):
    current_tz = timezone.get_current_timezone()
    if timezone.is_naive(dt):
        dt = timezone.make_aware(dt, current_tz)
    else:
        dt = timezone.localtime(dt, current_tz)
    return dt.isoformat()


def index(request):
    legacy_section = (request.GET.get("section") or "").lower()
    if legacy_section in SECTION_CONTENT:
        return redirect(legacy_section)

    featured_today = list(
        Product.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-featured", "sort_order", "-created_at")[:8]
    )

    context = _default_context(
        request,
        page_type="home",
        active_nav="home",
        meta_title="زاد | سفارش گل، بیکری و هدیه در مشهد",
        meta_description="زاد کانسپت‌استور مشهد برای سفارش گل، بیکری، هدیه و هماهنگی رویداد با ارسال فوری.",
        faq_items=HOME_FAQ,
    )
    context.update(
        {
            "featured_today": featured_today,
            "sections": SECTION_CONTENT,
            "hero_call_text": "تماس فوری",
            "hero_whatsapp_text": "واتساپ برای سفارش",
            "home_subtitle": "ترکیب لوکس گل، بیکری و هدیه با ارسال سریع در مشهد",
        }
    )
    return render(request, "index.html", context)


def _category_page(request, section):
    config = SECTION_CONTENT[section]
    products_qs = (
        Product.objects.filter(is_active=True, category__section=section)
        .select_related("category")
        .order_by("-featured", "sort_order", "-created_at")
    )

    featured_items = list(products_qs[:8])

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

    subcategories = []
    if section == "flowers":
        for slug, sub in FLOWER_SUBCATEGORIES.items():
            subcategories.append(
                {
                    "slug": slug,
                    "label": sub["label"],
                    "url": reverse("flower_subcategory", args=[slug]),
                }
            )

    context.update(
        {
            "section": section,
            "section_title": config["title"],
            "section_intro": config["intro"],
            "featured_items": featured_items,
            "all_items": list(products_qs[:16]),
            "subcategory_links": subcategories,
            "lead_form": LeadRequestForm(initial_lead_type=config["lead_type"]),
            "lead_default_type": config["lead_type"],
            "category_call_text": "هماهنگی تلفنی",
            "category_whatsapp_text": "مشاوره در واتساپ",
        }
    )
    return render(request, "category.html", context)


def flowers(request):
    return _category_page(request, "flowers")


def bakery(request):
    return _category_page(request, "bakery")


def gifts(request):
    return _category_page(request, "gifts")


def flower_subcategory(request, subcategory_slug):
    config = FLOWER_SUBCATEGORIES.get(subcategory_slug)
    if not config:
        raise Http404("Subcategory not found")

    queryset = Flower.objects.filter(is_active=True).select_related("category")
    if subcategory_slug == "plant":
        queryset = queryset.filter(Q(pack_type__in=config["pack_types"]) | Q(category__slug="plant"))
    else:
        queryset = queryset.filter(pack_type__in=config["pack_types"])

    items = list(queryset.order_by("-featured", "sort_order", "-created_at")[:12])
    related_posts = list(
        NewsPost.objects.filter(status=PublishStatus.PUBLISHED).order_by("-published_at", "-created_at")[:3]
    )

    breadcrumbs = _with_home(
        [
            {"name": "گل‌های زاد", "url": reverse("flowers")},
            {"name": config["label"], "url": None},
        ]
    )
    context = _default_context(
        request,
        page_type="category",
        active_nav="flowers",
        meta_title=config["meta_title"],
        meta_description=config["meta_description"],
        breadcrumbs=breadcrumbs,
    )
    context.update(
        {
            "subcategory_slug": subcategory_slug,
            "subcategory_label": config["label"],
            "subcategory_intro": config["intro"],
            "items": items,
            "related_posts": related_posts,
            "lead_form": LeadRequestForm(initial_lead_type="flower"),
            "lead_default_type": "flower",
        }
    )
    return render(request, "subcategory.html", context)


def _item_detail_context(request, product):
    category_name = product.category.name if product.category else "محصول"
    section = product.category.section if product.category else ""
    active_nav = section if section in {"flowers", "bakery", "gifts"} else ""

    subcategory_url = None
    subcategory_label = None
    if isinstance(product, Flower):
        pack_to_slug = {
            Flower.PackType.BOUQUET: "bouquet",
            Flower.PackType.BOX: "box",
            Flower.PackType.STAND: "stand",
            Flower.PackType.BASKET: "plant",
            Flower.PackType.STEM: "plant",
        }
        sub_slug = pack_to_slug.get(product.pack_type)
        if sub_slug:
            subcategory_url = reverse("flower_subcategory", args=[sub_slug])
            subcategory_label = FLOWER_SUBCATEGORIES[sub_slug]["label"]

    breadcrumbs = [{"name": "خانه", "url": reverse("index")}]
    if section:
        breadcrumbs.append({"name": SECTION_CONTENT[section]["title"], "url": reverse(section)})
    if subcategory_url and subcategory_label:
        breadcrumbs.append({"name": subcategory_label, "url": subcategory_url})
    breadcrumbs.append({"name": product.name, "url": None})

    similar_items = list(
        Product.objects.filter(is_active=True, category__section=section)
        .exclude(pk=product.pk)
        .select_related("category")
        .order_by("-featured", "sort_order", "-created_at")[:3]
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
    context.update(
        {
            "product": product,
            "category_name": category_name,
            "category_url": reverse(section) if section else reverse("index"),
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
    product = get_object_or_404(Product.objects.select_related("category"), pk=pk)
    if slug != product.slug:
        return redirect("product_detail", pk=product.pk, slug=product.slug)
    return render(request, "item_detail.html", _item_detail_context(request, product))


def flower_detail(request, pk: int, slug: str):
    flower = get_object_or_404(Flower.objects.select_related("category"), pk=pk)
    if slug != flower.slug:
        return redirect("flower_detail", pk=flower.pk, slug=flower.slug)
    return render(request, "item_detail.html", _item_detail_context(request, flower))


def flower_detail_redirect(request, pk: int):
    flower = get_object_or_404(Flower, pk=pk)
    return redirect("flower_detail", pk=flower.pk, slug=flower.slug)


def events(request):
    published_events_qs = Event.objects.filter(status=PublishStatus.PUBLISHED).order_by("start_at", "-created_at")
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

    if not published_events:
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
            "lead_form": LeadRequestForm(initial_lead_type="event", include_event_fields=True),
            "lead_default_type": "event",
            "events_are_demo": not published_events_qs.exists(),
        }
    )
    return render(request, "events.html", context)


def event_detail(request, slug: str):
    event = get_object_or_404(Event, slug=slug, status=PublishStatus.PUBLISHED)
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
            "lead_form": LeadRequestForm(initial_lead_type="event", include_event_fields=True),
            "lead_default_type": "event",
        }
    )
    context["extra_jsonld"].append(_jsonld(event_schema))
    return render(request, "event_detail.html", context)


def mashhad_hub(request):
    curated_items = list(
        Product.objects.filter(is_active=True, category__section="flowers")
        .select_related("category")
        .order_by("-featured", "sort_order", "-created_at")[:6]
    )
    breadcrumbs = _with_home([{"name": "سفارش در مشهد", "url": None}])
    context = _default_context(
        request,
        page_type="local",
        active_nav="mashhad",
        meta_title="سفارش در مشهد | زاد",
        meta_description="مرکز سفارش زاد در مشهد برای گل، ارسال فوری و هماهنگی سریع.",
        breadcrumbs=breadcrumbs,
    )
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
        Product.objects.filter(is_active=True, category__section="flowers")
        .select_related("category")
        .order_by("-featured", "sort_order", "-created_at")[:8]
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
            "question": "آیا عکس محصول قبل از ارسال ارسال می‌شود؟",
            "answer": "در صورت درخواست، پیش از خروج سفارش امکان ارسال تصویر نهایی وجود دارد.",
        },
        {
            "question": "اگر آیتم انتخابی موجود نباشد چه می‌شود؟",
            "answer": "گزینه‌های نزدیک با همان سطح کیفیت پیشنهاد می‌شود و پس از تایید شما ارسال انجام می‌گردد.",
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
            "occasion_links": [
                {"label": "تولد", "url": reverse("flower_subcategory", args=["bouquet"])},
                {"label": "سالگرد", "url": reverse("flower_subcategory", args=["box"])},
                {"label": "ترحیم", "url": reverse("flower_subcategory", args=["stand"])},
                {"label": "رویداد", "url": reverse("events")},
            ],
            "lead_form": LeadRequestForm(initial_lead_type="flower"),
            "lead_default_type": "flower",
        }
    )
    return render(request, "local_landing.html", context)


def mashhad_flower_order(request):
    return _local_landing(request, "order")


def mashhad_flower_delivery(request):
    return _local_landing(request, "delivery")


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
        meta_description="پاسخ سوالات رایج درباره سفارش گل، ارسال فوری، ساعات کاری و هماهنگی رویداد در زاد.",
        breadcrumbs=breadcrumbs,
        faq_items=FAQ_PAGE_ITEMS,
    )
    context["faq_page_items"] = FAQ_PAGE_ITEMS
    return render(request, "faq.html", context)


def blog(request):
    posts = list(
        NewsPost.objects.filter(status=PublishStatus.PUBLISHED).order_by("-published_at", "-created_at")
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
    context["posts"] = posts
    return render(request, "blog_list.html", context)


def blog_detail(request, slug):
    post = get_object_or_404(NewsPost, slug=slug, status=PublishStatus.PUBLISHED)
    recommended_items = list(
        Product.objects.filter(is_active=True)
        .select_related("category")
        .order_by("-featured", "sort_order", "-created_at")[:3]
    )

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
        meta_description=post.excerpt or "مطالعه مطلب بلاگ زاد و دسترسی به لینک‌های مرتبط با سفارش.",
        breadcrumbs=breadcrumbs,
    )
    context.update(
        {
            "post": post,
            "recommended_category": {"label": "گل‌ها", "url": reverse("flowers")},
            "recommended_subcategory": {
                "label": "دسته‌گل",
                "url": reverse("flower_subcategory", args=["bouquet"]),
            },
            "recommended_items": recommended_items,
        }
    )
    return render(request, "blog_detail.html", context)


@require_POST
def submit_lead_request(request):
    include_event_fields = request.POST.get("lead_type") == "event"
    form = LeadRequestForm(request.POST, include_event_fields=include_event_fields)

    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("index")
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = reverse("index")

    if form.is_valid():
        lead = form.save(commit=False)
        lead.source_page = request.POST.get("source_page", "")
        lead.save()
        messages.success(request, "درخواست شما ثبت شد. به‌زودی با شما تماس می‌گیریم.")
    else:
        messages.error(request, "لطفاً اطلاعات فرم را کامل و صحیح وارد کنید.")

    return redirect(next_url)


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
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")
