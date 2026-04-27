from types import MethodType

from django import forms
from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html

from .models import (
    BakeryItem,
    Category,
    Event,
    Flower,
    GiftItem,
    HomeHeroSlide,
    LeadRequest,
    NewsPost,
    Product,
    ProductImage,
    PublishStatus,
    SiteHero,
    Tag,
)


admin.site.site_header = "پنل مدیریت زاد"
admin.site.site_title = "مدیریت زاد"
admin.site.index_title = "مدیریت محتوا، محصولات و درخواست‌ها"


# =========================
# Helpers
# =========================

_ADMIN_METADATA_LOCALIZED = False


def to_persian_digits(value):
    value = str(value)
    english_digits = "0123456789"
    persian_digits = "۰۱۲۳۴۵۶۷۸۹"
    translation_table = str.maketrans(english_digits, persian_digits)
    return value.translate(translation_table)


def format_toman(value):
    if value in (None, ""):
        return "استعلام قیمت"

    try:
        number = int(value)
    except (TypeError, ValueError):
        return "استعلام قیمت"

    formatted = f"{number:,}".replace(",", "٬")
    return f"{to_persian_digits(formatted)} تومان"


def safe_get_field(model, field_name):
    try:
        return model._meta.get_field(field_name)
    except Exception:
        return None


def get_tag_budget_value():
    if hasattr(Tag, "TagType") and hasattr(Tag.TagType, "BUDGET"):
        return Tag.TagType.BUDGET

    if hasattr(Tag, "TagType") and hasattr(Tag.TagType, "PRICE"):
        return Tag.TagType.PRICE

    return "budget"


# =========================
# Persian labels
# =========================

def _localize_admin_metadata():
    model_labels = {
        Category: ("دسته‌بندی", "دسته‌بندی‌ها"),
        Tag: ("برچسب", "برچسب‌ها"),
        Product: ("همه محصولات", "همه محصولات"),
        Flower: ("گل", "گل‌ها"),
        BakeryItem: ("محصول بیکری", "محصولات بیکری"),
        GiftItem: ("هدیه", "هدایا"),
        ProductImage: ("تصویر محصول", "تصاویر محصول"),
        LeadRequest: ("درخواست سفارش", "درخواست‌های سفارش"),
        HomeHeroSlide: ("اسلاید صفحه خانه", "اسلایدهای صفحه خانه"),
        SiteHero: ("بنر صفحات", "بنرهای صفحات"),
    }

    for model, (singular, plural) in model_labels.items():
        model._meta.verbose_name = singular
        model._meta.verbose_name_plural = plural

    field_metadata = {
        Category: {
            "name": ("نام دسته", "مثلاً دسته‌گل، باکس گل، سبد گل، کیک، شمع یا سرامیک."),
            "slug": ("اسلاگ", "برای لینک تمیز بهتر است انگلیسی باشد؛ مثل bouquet یا box."),
            "section": ("بخش اصلی", "مشخص می‌کند این دسته مربوط به گل، بیکری یا هدیه است."),
            "description": ("توضیح کوتاه", "اختیاری است؛ برای توضیح صفحه دسته استفاده می‌شود."),
            "cover_image": ("تصویر دسته", "تصویر کاور دسته."),
            "is_active": ("فعال", "اگر خاموش باشد در سایت نمایش داده نمی‌شود."),
            "sort_order": ("ترتیب نمایش", "عدد کمتر یعنی نمایش بالاتر."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        Tag: {
            "name": ("نام برچسب", "مثلاً تولد، عاشقانه، اقتصادی، مینیمال یا لوکس."),
            "slug": ("اسلاگ", "برای لینک تمیز بهتر است انگلیسی باشد؛ مثل birthday یا luxury."),
            "tag_type": ("نوع برچسب", "مشخص می‌کند این برچسب برای مناسبت، بودجه یا حال‌وهواست."),
            "is_active": ("فعال", "اگر خاموش باشد در سایت استفاده نمی‌شود."),
            "sort_order": ("ترتیب نمایش", "عدد کمتر یعنی نمایش بالاتر."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        Product: {
            "name": ("نام محصول", "نام کوتاه و قابل فهم بنویس."),
            "slug": ("اسلاگ", "اگر خالی باشد خودکار ساخته می‌شود."),
            "description": ("توضیحات", "اختیاری است؛ کوتاه، احساسی و فروش‌محور بنویس."),
            "pricing_type": ("نوع قیمت‌گذاری", "قیمت ثابت یا استعلامی."),
            "price": ("قیمت به تومان", "فقط عدد وارد کن؛ مثلاً ۲۵۰۰۰۰۰."),
            "cover_image": ("تصویر اصلی", "عکس اصلی محصول؛ مثل کاور پست اینستاگرام."),
            "category": ("دسته اولیه", "دسته مشخص می‌کند محصول واقعاً چیست."),
            "tags": ("برچسب‌ها", "برای مناسبت، بودجه و حال‌وهوای محصول."),
            "is_active": ("فعال", "برای نمایش در سایت روشن باشد."),
            "publish_status": ("وضعیت انتشار", "منتشرشده یعنی در سایت قابل نمایش است."),
            "stock_status": ("وضعیت موجودی", "موجود، ناموجود یا پیش‌سفارش."),
            "featured": ("ویژه", "برای نمایش در بخش‌های پیشنهادی و صفحه اول."),
            "sort_order": ("ترتیب نمایش", "عدد کمتر یعنی نمایش بالاتر."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        ProductImage: {
            "product": ("محصول", ""),
            "image": ("تصویر", ""),
            "alt_text": ("متن جایگزین", "اختیاری است؛ برای سئو و دسترس‌پذیری."),
            "ordering": ("ترتیب", "عدد کمتر یعنی نمایش بالاتر."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        NewsPost: {
            "title": ("عنوان", ""),
            "slug": ("اسلاگ", ""),
            "excerpt": ("خلاصه", ""),
            "body": ("متن", ""),
            "cover_image": ("تصویر کاور", ""),
            "status": ("وضعیت", ""),
            "published_at": ("تاریخ انتشار", ""),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        Event: {
            "title": ("عنوان", ""),
            "slug": ("اسلاگ", ""),
            "description": ("توضیحات", ""),
            "start_at": ("شروع", ""),
            "end_at": ("پایان", ""),
            "location": ("مکان", ""),
            "cover_image": ("تصویر کاور", ""),
            "status": ("وضعیت", ""),
            "published_at": ("تاریخ انتشار", ""),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        LeadRequest: {
            "full_name": ("نام", ""),
            "mobile": ("شماره موبایل", ""),
            "lead_type": ("نوع درخواست", ""),
            "product": ("محصول", ""),
            "delivery_window": ("بازه تحویل", ""),
            "preferred_date": ("تاریخ انتخابی", ""),
            "event_location": ("مکان رویداد", ""),
            "note": ("یادداشت", ""),
            "source_page": ("صفحه مبدا", ""),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        HomeHeroSlide: {
            "title": ("عنوان", ""),
            "kicker": ("متن کوتاه بالا", ""),
            "description": ("توضیح", ""),
            "image": ("تصویر اصلی", ""),
            "mobile_image": ("تصویر موبایل", ""),
            "primary_button_text": ("متن دکمه اصلی", ""),
            "primary_button_url": ("لینک دکمه اصلی", ""),
            "secondary_button_text": ("متن دکمه دوم", ""),
            "secondary_button_url": ("لینک دکمه دوم", ""),
            "is_active": ("فعال", ""),
            "sort_order": ("ترتیب نمایش", ""),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
        SiteHero: {
            "title": ("عنوان", ""),
            "kicker": ("متن کوتاه بالا", ""),
            "description": ("توضیح", ""),
            "image": ("تصویر اصلی", ""),
            "mobile_image": ("تصویر موبایل", ""),
            "target_page": ("صفحه هدف", ""),
            "target_slug": ("اسلاگ هدف", ""),
            "is_active": ("فعال", ""),
            "sort_order": ("ترتیب نمایش", ""),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین ویرایش", ""),
        },
    }

    for model, metadata in field_metadata.items():
        for field_name, (label, help_text) in metadata.items():
            field = safe_get_field(model, field_name)
            if not field:
                continue

            field.verbose_name = label
            if help_text:
                field.help_text = help_text

    Category._meta.get_field("section").choices = [
        (Category.Section.FLOWERS, "گل‌ها"),
        (Category.Section.BAKERY, "بیکری"),
        (Category.Section.GIFTS, "هدایا"),
    ]

    Product._meta.get_field("pricing_type").choices = [
        (Product.PricingType.FIXED, "قیمت ثابت"),
        (Product.PricingType.INQUIRY, "استعلامی"),
    ]

    Product._meta.get_field("publish_status").choices = [
        (Product.PublishStatus.DRAFT, "پیش‌نویس"),
        (Product.PublishStatus.PUBLISHED, "منتشرشده"),
    ]

    Product._meta.get_field("stock_status").choices = [
        (Product.StockStatus.IN_STOCK, "موجود"),
        (Product.StockStatus.OUT_OF_STOCK, "ناموجود"),
        (Product.StockStatus.PREORDER, "پیش‌سفارش"),
    ]

    tag_type_field = safe_get_field(Tag, "tag_type")
    if tag_type_field and hasattr(Tag, "TagType"):
        tag_type_field.choices = [
            (Tag.TagType.OCCASION, "مناسبت"),
            (get_tag_budget_value(), "بودجه"),
            (Tag.TagType.VIBE, "حال‌وهوا"),
        ]

    publish_choices = [
        (PublishStatus.DRAFT, "پیش‌نویس"),
        (PublishStatus.PUBLISHED, "منتشرشده"),
    ]

    NewsPost._meta.get_field("status").choices = publish_choices
    Event._meta.get_field("status").choices = publish_choices

    LeadRequest._meta.get_field("lead_type").choices = [
        (LeadRequest.LeadType.FLOWER, "گل"),
        (LeadRequest.LeadType.BAKERY, "بیکری"),
        (LeadRequest.LeadType.GIFT, "هدیه"),
        (LeadRequest.LeadType.EVENT, "رویداد"),
    ]

    LeadRequest._meta.get_field("delivery_window").choices = [
        (LeadRequest.DeliveryWindow.TODAY, "امروز"),
        (LeadRequest.DeliveryWindow.TOMORROW, "فردا"),
        (LeadRequest.DeliveryWindow.PICK_DATE, "تاریخ انتخابی"),
    ]


def _ensure_admin_metadata():
    global _ADMIN_METADATA_LOCALIZED

    if not _ADMIN_METADATA_LOCALIZED:
        _localize_admin_metadata()
        _ADMIN_METADATA_LOCALIZED = True


_original_get_app_list = admin.site.get_app_list


def _localized_get_app_list(self, request, app_label=None):
    _ensure_admin_metadata()
    return _original_get_app_list(request, app_label)


admin.site.get_app_list = MethodType(_localized_get_app_list, admin.site)


# =========================
# Mixins
# =========================

class LocalizedAdminMixin:
    def get_queryset(self, request):
        _ensure_admin_metadata()
        return super().get_queryset(request)

    def get_form(self, request, obj=None, change=False, **kwargs):
        _ensure_admin_metadata()
        return super().get_form(request, obj, change, **kwargs)

    def get_fieldsets(self, request, obj=None):
        _ensure_admin_metadata()
        return super().get_fieldsets(request, obj)


class LocalizedInlineMixin:
    def get_formset(self, request, obj=None, **kwargs):
        _ensure_admin_metadata()
        return super().get_formset(request, obj, **kwargs)


class AdminImagePreviewMixin:
    @admin.display(description="تصویر")
    def image_preview(self, obj):
        image = None

        if hasattr(obj, "cover_image") and obj.cover_image:
            image = obj.cover_image
        elif hasattr(obj, "image") and obj.image:
            image = obj.image

        if not image:
            return format_html(
                '<span style="display:inline-flex;width:40px;height:40px;align-items:center;justify-content:center;border-radius:8px;border:1px dashed #999;font-size:10px;color:#999;">{}</span>',
                "بدون عکس",
            )

        return format_html(
            '''
            <img src="{}" style="
                width: 40px !important;
                height: 40px !important;
                max-width: 40px !important;
                max-height: 40px !important;
                min-width: 40px !important;
                min-height: 40px !important;
                object-fit: cover !important;
                border-radius: 8px !important;
                display: block !important;
            " />
            ''',
            image.url,
        )


class ProductActionsMixin:
    actions = (
        "activate_selected",
        "deactivate_selected",
        "mark_featured",
        "remove_featured",
        "publish_selected_products",
        "draft_selected_products",
        "mark_in_stock",
        "mark_out_of_stock",
        "make_inquiry_pricing",
    )

    @admin.action(description="فعال‌کردن موارد انتخاب‌شده")
    def activate_selected(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f"{updated} مورد فعال شد.")

    @admin.action(description="غیرفعال‌کردن موارد انتخاب‌شده")
    def deactivate_selected(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f"{updated} مورد غیرفعال شد.")

    @admin.action(description="ویژه‌کردن موارد انتخاب‌شده")
    def mark_featured(self, request, queryset):
        updated = queryset.update(featured=True)
        self.message_user(request, f"{updated} مورد ویژه شد.")

    @admin.action(description="حذف از موارد ویژه")
    def remove_featured(self, request, queryset):
        updated = queryset.update(featured=False)
        self.message_user(request, f"{updated} مورد از ویژه‌ها حذف شد.")

    @admin.action(description="انتشار موارد انتخاب‌شده")
    def publish_selected_products(self, request, queryset):
        updated = queryset.update(publish_status=Product.PublishStatus.PUBLISHED)
        self.message_user(request, f"{updated} مورد منتشر شد.")

    @admin.action(description="بازگردانی به پیش‌نویس")
    def draft_selected_products(self, request, queryset):
        updated = queryset.update(publish_status=Product.PublishStatus.DRAFT)
        self.message_user(request, f"{updated} مورد به پیش‌نویس برگشت.")

    @admin.action(description="علامت‌گذاری به عنوان موجود")
    def mark_in_stock(self, request, queryset):
        updated = queryset.update(stock_status=Product.StockStatus.IN_STOCK)
        self.message_user(request, f"{updated} مورد موجود شد.")

    @admin.action(description="علامت‌گذاری به عنوان ناموجود")
    def mark_out_of_stock(self, request, queryset):
        updated = queryset.update(stock_status=Product.StockStatus.OUT_OF_STOCK)
        self.message_user(request, f"{updated} مورد ناموجود شد.")

    @admin.action(description="قیمت‌گذاری به حالت استعلامی")
    def make_inquiry_pricing(self, request, queryset):
        updated = queryset.update(pricing_type=Product.PricingType.INQUIRY, price=None)
        self.message_user(request, f"{updated} مورد استعلامی شد.")


class PublishActionsMixin:
    actions = ("publish_selected", "unpublish_selected")

    @admin.action(description="انتشار موارد انتخاب‌شده")
    def publish_selected(self, request, queryset):
        updated = queryset.update(
            status=PublishStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        self.message_user(request, f"{updated} مورد منتشر شد.")

    @admin.action(description="بازگردانی به پیش‌نویس")
    def unpublish_selected(self, request, queryset):
        updated = queryset.update(
            status=PublishStatus.DRAFT,
            published_at=None,
        )
        self.message_user(request, f"{updated} مورد به پیش‌نویس برگشت.")


# =========================
# Forms
# =========================

class ProductAdminForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        widgets = {
            "tags": forms.CheckboxSelectMultiple,
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "توضیح کوتاه و احساسی بنویس؛ اگر خالی بماند سایت متن پیش‌فرض نشان می‌دهد.",
                }
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "category" in self.fields:
            self.fields["category"].help_text = "دسته‌بندی محصول را انتخاب کن."

        if "tags" in self.fields:
            queryset = Tag.objects.all()

            if safe_get_field(Tag, "is_active"):
                queryset = queryset.filter(is_active=True)

            if safe_get_field(Tag, "tag_type"):
                queryset = queryset.order_by("tag_type", "sort_order", "name")
            else:
                queryset = queryset.order_by("name")

            self.fields["tags"].queryset = queryset
            self.fields["tags"].help_text = "برچسب‌ها برای مناسبت، بودجه و حال‌وهوا هستند."

        if "cover_image" in self.fields:
            self.fields["cover_image"].help_text = "عکس اصلی محصول؛ مثل عکس کاور پست اینستاگرام."

        if "name" in self.fields:
            self.fields["name"].help_text = "نام کوتاه و قابل فهم بنویس."

        if "price" in self.fields:
            self.fields["price"].help_text = "فقط عدد وارد کن؛ مثلاً 2500000."

        if "sort_order" in self.fields:
            self.fields["sort_order"].help_text = "عدد کمتر یعنی محصول بالاتر نمایش داده می‌شود."

    def clean(self):
        cleaned_data = super().clean()

        pricing_type = cleaned_data.get("pricing_type")
        price = cleaned_data.get("price")

        if pricing_type == Product.PricingType.INQUIRY:
            cleaned_data["price"] = None

        if pricing_type == Product.PricingType.FIXED and price is None:
            self.add_error(
                "price",
                "برای قیمت ثابت، وارد کردن قیمت الزامی است. اگر قیمت قطعی نیست، نوع قیمت‌گذاری را استعلامی بگذار.",
            )

        if price is not None and price < 0:
            self.add_error("price", "قیمت نمی‌تواند منفی باشد.")

        return cleaned_data


class CategoryAdminForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 3,
                    "placeholder": "یک توضیح کوتاه برای این دسته بنویس.",
                }
            ),
        }


class NewsPostAdminForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        widgets = {
            "excerpt": forms.Textarea(attrs={"rows": 3}),
            "body": forms.Textarea(attrs={"rows": 8}),
        }


class EventAdminForm(forms.ModelForm):
    class Meta:
        fields = "__all__"
        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
        }


# =========================
# Inlines
# =========================

class ProductImageInline(LocalizedInlineMixin, AdminImagePreviewMixin, admin.StackedInline):
    model = ProductImage
    extra = 1
    fields = (
        "image",
        "image_preview",
        "alt_text",
        "ordering",
        "created_at",
        "updated_at",
    )
    readonly_fields = (
        "image_preview",
        "created_at",
        "updated_at",
    )
    ordering = (
        "ordering",
        "id",
    )
    verbose_name = "عکس گالری"
    verbose_name_plural = "گالری محصول"


# =========================
# Category / Tag
# =========================

@admin.register(Category)
class CategoryAdmin(AdminImagePreviewMixin, LocalizedAdminMixin, admin.ModelAdmin):
    form = CategoryAdminForm

    list_display = (
        "image_preview",
        "name",
        "section",
        "is_active",
        "sort_order",
        "updated_at",
    )
    list_filter = (
        "section",
        "is_active",
    )
    search_fields = (
        "name",
        "slug",
        "description",
    )
    ordering = (
        "section",
        "sort_order",
        "name",
    )
    list_editable = (
        "is_active",
        "sort_order",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
    )
    save_on_top = True
    list_per_page = 30

    fieldsets = (
        (
            "۱.دسته‌بندی",
            {
                "description": "دسته اولیه مشخص می‌کند محصول چیست؛ مثلاً باکس گل، دسته‌گل، کیک یا شمع.",
                "fields": (
                    "cover_image",
                    "image_preview",
                    "name",
                    "section",
                ),
            },
        ),
        (
            "۲. توضیح کوتاه",
            {
                "description": "این متن می‌تواند در صفحه دسته نمایش داده شود.",
                "fields": (
                    "description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "۳. نمایش",
            {
                "description": "برای مخفی کردن یک دسته، فعال را خاموش کن. عدد کمتر یعنی نمایش بالاتر.",
                "fields": (
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "تنظیمات پیشرفته",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Tag)
class TagAdmin(LocalizedAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "tag_type",
        "is_active",
        "sort_order",
        "slug",
        "updated_at",
    )
    list_filter = (
        "tag_type",
        "is_active",
    )
    search_fields = (
        "name",
        "slug",
    )
    ordering = (
        "tag_type",
        "sort_order",
        "name",
    )
    list_editable = (
        "is_active",
        "sort_order",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    list_per_page = 40

    fieldsets = (
        (
            "برچسب",
            {
                "description": "برچسب یعنی محصول برای چه مناسبت، بودجه یا حال‌وهوایی مناسب است.",
                "fields": (
                    "name",
                    "slug",
                    "tag_type",
                ),
            },
        ),
        (
            "نمایش",
            {
                "description": "برچسب‌های غیرفعال در سایت استفاده نمی‌شوند.",
                "fields": (
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


# =========================
# Product
# =========================

class BaseProductAdmin(ProductActionsMixin, AdminImagePreviewMixin, LocalizedAdminMixin, admin.ModelAdmin):
    form = ProductAdminForm
    section_filter = None

    list_display = (
        "image_preview",
        "name",
        "category",
        "price_toman",
        "pricing_type",
        "stock_status",
        "publish_status",
        "is_active",
        "featured",
        "sort_order",
        "updated_at",
    )

    list_filter = (
        "publish_status",
        "is_active",
        "featured",
        "pricing_type",
        "stock_status",
        "category__section",
        "category",
        "tags",
    )

    search_fields = (
        "name",
        "slug",
        "description",
        "category__name",
        "tags__name",
    )

    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
    )

    ordering = (
        "sort_order",
        "-updated_at",
    )

    list_editable = (
        "pricing_type",
        "stock_status",
        "publish_status",
        "is_active",
        "featured",
        "sort_order",
    )

    inlines = [ProductImageInline]

    date_hierarchy = "updated_at"
    list_select_related = ("category",)
    list_per_page = 25
    save_on_top = True
    actions_on_top = True
    actions_on_bottom = False

    fieldsets = (
        (
            "۱. عکس و نام محصول",
            {
                "description": "این بخش مثل کاور پست اینستاگرام است؛ اول عکس و اسم محصول را وارد کن.",
                "fields": (
                    "cover_image",
                    "image_preview",
                    "name",
                ),
            },
        ),
        (
            "۲. قیمت و فروش",
            {
                "description": "قیمت را فقط عددی و به تومان وارد کن. اگر قیمت قطعی نیست، نوع قیمت‌گذاری را استعلامی بگذار.",
                "fields": (
                    "pricing_type",
                    "price",
                    "stock_status",
                ),
            },
        ),
        (
            "۳. انتشار در سایت",
            {
                "description": "برای نمایش محصول در سایت، منتشرشده و فعال باید روشن باشند.",
                "fields": (
                    "publish_status",
                    "is_active",
                    "featured",
                    "sort_order",
                ),
            },
        ),
        (
            "۴. دسته اولیه و برچسب‌ها",
            {
                "description": "دسته مشخص می‌کند محصول چیست؛ برچسب‌ها مشخص می‌کنند برای چه مناسبت، بودجه و حال‌وهوا مناسب است.",
                "fields": (
                    "category",
                    "tags",
                ),
            },
        ),
        (
            "۵. توضیح کوتاه",
            {
                "description": "اختیاری است. کوتاه، احساسی و قابل فهم بنویس.",
                "fields": (
                    "description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "تنظیمات پیشرفته",
            {
                "description": "این بخش معمولاً لازم نیست تغییر کند.",
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )

    @admin.display(description="قیمت", ordering="price")
    def price_toman(self, obj):
        if obj.pricing_type == Product.PricingType.INQUIRY or not obj.price:
            return format_html(
                '<span class="zaad-price zaad-price--inquiry">{}</span>',
                "استعلام قیمت",
            )

        return format_html(
            '<span class="zaad-price">{}</span>',
            format_toman(obj.price),
        )

    def get_changeform_initial_data(self, request):
        initial = {
            "pricing_type": Product.PricingType.INQUIRY,
            "stock_status": Product.StockStatus.IN_STOCK,
            "publish_status": Product.PublishStatus.PUBLISHED,
            "is_active": True,
            "featured": False,
            "sort_order": 0,
        }

        if self.section_filter:
            first_category = (
                Category.objects.filter(
                    section=self.section_filter,
                    is_active=True,
                )
                .order_by("sort_order", "name")
                .first()
            )

            if first_category:
                initial["category"] = first_category.pk

        return initial

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category":
            queryset = Category.objects.filter(is_active=True)

            if self.section_filter:
                queryset = queryset.filter(section=self.section_filter)

            kwargs["queryset"] = queryset.order_by("section", "sort_order", "name")

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def get_queryset(self, request):
        queryset = super().get_queryset(request).select_related("category").prefetch_related("tags")

        if self.section_filter:
            queryset = queryset.filter(category__section=self.section_filter)

        return queryset

    def save_model(self, request, obj, form, change):
        if obj.pricing_type == Product.PricingType.INQUIRY:
            obj.price = None

        super().save_model(request, obj, form, change)


@admin.register(Product)
class ProductAdmin(BaseProductAdmin):
    list_display = (
        "image_preview",
        "name",
        "product_type",
        "category",
        "price_toman",
        "pricing_type",
        "stock_status",
        "publish_status",
        "is_active",
        "featured",
        "sort_order",
        "updated_at",
    )

    @admin.display(description="نوع")
    def product_type(self, obj):
        if not obj.category:
            return "عمومی"

        if obj.category.section == Category.Section.FLOWERS:
            return "گل"

        if obj.category.section == Category.Section.BAKERY:
            return "بیکری"

        if obj.category.section == Category.Section.GIFTS:
            return "هدیه"

        return "عمومی"


@admin.register(Flower)
class FlowerAdmin(BaseProductAdmin):
    section_filter = Category.Section.FLOWERS

    fieldsets = (
        (
            "۱. عکس و نام گل",
            {
                "description": "عکس اصلی و نام محصول را مثل پست اینستاگرام وارد کن.",
                "fields": (
                    "cover_image",
                    "image_preview",
                    "name",
                ),
            },
        ),
        (
            "۲. قیمت و فروش",
            {
                "description": "قیمت را فقط عددی و به تومان وارد کن. اگر قیمت قطعی نیست، نوع قیمت‌گذاری را استعلامی بگذار.",
                "fields": (
                    "pricing_type",
                    "price",
                    "stock_status",
                ),
            },
        ),
        (
            "۳. انتشار در سایت",
            {
                "fields": (
                    "publish_status",
                    "is_active",
                    "featured",
                    "sort_order",
                ),
            },
        ),
        (
            "۴. دسته گل و حال‌وهوا",
            {
                "description": "دسته گل را انتخاب کن؛ مثل دسته‌گل، باکس گل، سبد گل یا استند. برچسب‌ها برای مناسبت، بودجه و حال‌وهوا هستند.",
                "fields": (
                    "category",
                    "tags",
                ),
            },
        ),
        (
            "توضیح کوتاه",
            {
                "fields": (
                    "description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "تنظیمات پیشرفته",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(BakeryItem)
class BakeryItemAdmin(BaseProductAdmin):
    section_filter = Category.Section.BAKERY

    fieldsets = (
        (
            "۱. عکس و نام محصول بیکری",
            {
                "description": "عکس اصلی و نام محصول را مثل پست اینستاگرام وارد کن.",
                "fields": (
                    "cover_image",
                    "image_preview",
                    "name",
                ),
            },
        ),
        (
            "۲. قیمت و فروش",
            {
                "description": "قیمت را فقط عددی و به تومان وارد کن. اگر قیمت قطعی نیست، نوع قیمت‌گذاری را استعلامی بگذار.",
                "fields": (
                    "pricing_type",
                    "price",
                    "stock_status",
                ),
            },
        ),
        (
            "۳. انتشار در سایت",
            {
                "fields": (
                    "publish_status",
                    "is_active",
                    "featured",
                    "sort_order",
                ),
            },
        ),
        (
            "۴. دسته بیکری و حال‌وهوا",
            {
                "description": "دسته بیکری را انتخاب کن؛ مثل کیک، شیرینی، کوکی یا ست پذیرایی. برچسب‌ها برای مناسبت، بودجه و حال‌وهوا هستند.",
                "fields": (
                    "category",
                    "tags",
                ),
            },
        ),
        (
            "توضیح کوتاه",
            {
                "fields": (
                    "description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "تنظیمات پیشرفته",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(GiftItem)
class GiftItemAdmin(BaseProductAdmin):
    section_filter = Category.Section.GIFTS

    fieldsets = (
        (
            "۱. عکس و نام هدیه",
            {
                "description": "عکس اصلی و نام محصول را مثل پست اینستاگرام وارد کن.",
                "fields": (
                    "cover_image",
                    "image_preview",
                    "name",
                ),
            },
        ),
        (
            "۲. قیمت و فروش",
            {
                "description": "قیمت را فقط عددی و به تومان وارد کن. اگر قیمت قطعی نیست، نوع قیمت‌گذاری را استعلامی بگذار.",
                "fields": (
                    "pricing_type",
                    "price",
                    "stock_status",
                ),
            },
        ),
        (
            "۳. انتشار در سایت",
            {
                "fields": (
                    "publish_status",
                    "is_active",
                    "featured",
                    "sort_order",
                ),
            },
        ),
        (
            "۴. دسته هدیه و حال‌وهوا",
            {
                "description": "دسته هدیه را انتخاب کن؛ مثل شمع، سرامیک، اکسسوری یا ست هدیه. برچسب‌ها برای مناسبت، بودجه و حال‌وهوا هستند.",
                "fields": (
                    "category",
                    "tags",
                ),
            },
        ),
        (
            "توضیح کوتاه",
            {
                "fields": (
                    "description",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "تنظیمات پیشرفته",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(ProductImage)
class ProductImageAdmin(AdminImagePreviewMixin, LocalizedAdminMixin, admin.ModelAdmin):
    list_display = (
        "image_preview",
        "product",
        "ordering",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "created_at",
    )
    search_fields = (
        "product__name",
        "product__slug",
        "alt_text",
    )
    ordering = (
        "product",
        "ordering",
    )
    list_editable = (
        "ordering",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
    )
    list_select_related = (
        "product",
    )
    save_on_top = True

    fieldsets = (
        (
            "تصویر",
            {
                "fields": (
                    "product",
                    "image",
                    "image_preview",
                    "alt_text",
                ),
            },
        ),
        (
            "نمایش",
            {
                "fields": (
                    "ordering",
                ),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )
    def has_module_permission(self, request):
        return False


# =========================
# News / Events / Leads
# =========================

@admin.register(NewsPost)
class NewsPostAdmin(PublishActionsMixin, AdminImagePreviewMixin, LocalizedAdminMixin, admin.ModelAdmin):
    form = NewsPostAdminForm

    list_display = (
        "image_preview",
        "title",
        "status",
        "published_at",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "status",
        "published_at",
        "created_at",
    )
    search_fields = (
        "title",
        "slug",
        "excerpt",
        "body",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
    )
    ordering = (
        "-published_at",
        "-created_at",
    )
    date_hierarchy = "published_at"
    list_editable = (
        "status",
    )
    save_on_top = True

    fieldsets = (
        (
            "محتوا",
            {
                "fields": (
                    "title",
                    "excerpt",
                    "body",
                ),
            },
        ),
        (
            "رسانه و انتشار",
            {
                "fields": (
                    "cover_image",
                    "image_preview",
                    "status",
                    "published_at",
                ),
            },
        ),
        (
            "تنظیمات پیشرفته",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(Event)
class EventAdmin(PublishActionsMixin, AdminImagePreviewMixin, LocalizedAdminMixin, admin.ModelAdmin):
    form = EventAdminForm

    list_display = (
        "image_preview",
        "title",
        "status",
        "start_at",
        "end_at",
        "location",
        "published_at",
    )
    list_filter = (
        "status",
        "start_at",
        "end_at",
        "published_at",
    )
    search_fields = (
        "title",
        "slug",
        "description",
        "location",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
    )
    ordering = (
        "start_at",
        "-created_at",
    )
    date_hierarchy = "start_at"
    list_editable = (
        "status",
    )
    save_on_top = True

    fieldsets = (
        (
            "محتوا",
            {
                "fields": (
                    "title",
                    "description",
                ),
            },
        ),
        (
            "زمان و مکان",
            {
                "fields": (
                    "start_at",
                    "end_at",
                    "location",
                ),
            },
        ),
        (
            "رسانه و انتشار",
            {
                "fields": (
                    "cover_image",
                    "image_preview",
                    "status",
                    "published_at",
                ),
            },
        ),
        (
            "تنظیمات پیشرفته",
            {
                "fields": (
                    "slug",
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(LeadRequest)
class LeadRequestAdmin(LocalizedAdminMixin, admin.ModelAdmin):
    list_display = (
        "full_name",
        "mobile",
        "lead_type",
        "product",
        "delivery_window",
        "preferred_date",
        "created_at",
    )
    list_filter = (
        "lead_type",
        "delivery_window",
        "created_at",
    )
    search_fields = (
        "full_name",
        "mobile",
        "product__name",
        "note",
        "event_location",
        "source_page",
    )
    readonly_fields = (
        "created_at",
        "updated_at",
    )
    ordering = (
        "-created_at",
    )
    list_select_related = (
        "product",
    )
    list_per_page = 30

    fieldsets = (
        (
            "اطلاعات متقاضی",
            {
                "fields": (
                    "full_name",
                    "mobile",
                    "lead_type",
                    "product",
                ),
            },
        ),
        (
            "جزئیات سفارش",
            {
                "fields": (
                    "delivery_window",
                    "preferred_date",
                    "event_location",
                    "note",
                ),
            },
        ),
        (
            "فنی",
            {
                "fields": (
                    "source_page",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


# =========================
# Heroes
# =========================

class HeroAdminBase(LocalizedAdminMixin, admin.ModelAdmin):
    list_per_page = 20
    save_on_top = True

    readonly_fields = (
        "created_at",
        "updated_at",
        "image_preview",
        "mobile_image_preview",
    )

    search_fields = (
        "title",
        "kicker",
        "description",
    )

    ordering = (
        "sort_order",
        "id",
    )

    @admin.display(description="پیش‌نمایش تصویر")
    def image_preview(self, obj):
        if obj and obj.image:
            return format_html(
                '''
                <img src="{}" style="
                    width: 72px !important;
                    height: 42px !important;
                    max-width: 72px !important;
                    max-height: 42px !important;
                    object-fit: cover !important;
                    border-radius: 8px !important;
                    display: block !important;
                " />
                ''',
                obj.image.url,
            )

        return format_html(
            '<span style="display:inline-flex;width:72px;height:42px;align-items:center;justify-content:center;border:1px dashed #999;border-radius:8px;font-size:10px;color:#999;">{}</span>',
            "بدون عکس",
        )

    @admin.display(description="پیش‌نمایش موبایل")
    def mobile_image_preview(self, obj):
        if obj and obj.mobile_image:
            return format_html(
                '''
                <img src="{}" style="
                    width: 32px !important;
                    height: 54px !important;
                    max-width: 32px !important;
                    max-height: 54px !important;
                    object-fit: cover !important;
                    border-radius: 8px !important;
                    display: block !important;
                " />
                ''',
                obj.mobile_image.url,
            )

        return format_html(
            '<span style="display:inline-flex;width:32px;height:54px;align-items:center;justify-content:center;border:1px dashed #999;border-radius:8px;font-size:9px;color:#999;">{}</span>',
            "ندارد",
        )


@admin.register(HomeHeroSlide)
class HomeHeroSlideAdmin(HeroAdminBase):
    list_display = (
        "image_preview",
        "title",
        "is_active",
        "sort_order",
        "updated_at",
    )

    list_filter = (
        "is_active",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
        "sort_order",
    )

    fieldsets = (
        (
            "۱. متن اسلاید صفحه خانه",
            {
                "description": "این بخش برای اسلایدهای بزرگ صفحه اصلی سایت است.",
                "fields": (
                    "title",
                    "kicker",
                    "description",
                ),
            },
        ),
        (
            "۲. عکس اسلاید",
            {
                "description": "تصویر اصلی برای دسکتاپ است. تصویر موبایل اختیاری است و فقط برای نمایش بهتر در موبایل استفاده می‌شود.",
                "fields": (
                    "image",
                    "image_preview",
                    "mobile_image",
                    "mobile_image_preview",
                ),
            },
        ),
        (
            "۳. دکمه‌ها",
            {
                "description": "اختیاری است. اگر متن و لینک دکمه‌ها خالی باشد، دکمه‌ای روی اسلاید نمایش داده نمی‌شود.",
                "fields": (
                    "primary_button_text",
                    "primary_button_url",
                    "secondary_button_text",
                    "secondary_button_url",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "۴. نمایش در سایت",
            {
                "description": "اگر فعال خاموش باشد، این اسلاید در صفحه خانه نمایش داده نمی‌شود. عدد کمتر یعنی نمایش زودتر.",
                "fields": (
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )


@admin.register(SiteHero)
class SiteHeroAdmin(HeroAdminBase):
    list_display = (
        "image_preview",
        "title",
        "target_page_display",
        "target_slug_display",
        "is_active",
        "sort_order",
        "updated_at",
    )

    list_filter = (
        "target_page",
        "is_active",
        "created_at",
        "updated_at",
    )

    list_editable = (
        "is_active",
        "sort_order",
    )

    search_fields = (
        "title",
        "kicker",
        "description",
        "target_slug",
    )

    @admin.display(description="صفحه")
    def target_page_display(self, obj):
        return obj.get_target_page_display()

    @admin.display(description="برای کدام دسته؟")
    def target_slug_display(self, obj):
        if obj.target_slug:
            return obj.target_slug

        return "کل صفحه"

    fieldsets = (
        (
            "۱. این بنر برای کجاست؟",
            {
                "description": "اینجا مشخص می‌کنی این عکس بزرگ بالای کدام صفحه نمایش داده شود.",
                "fields": (
                    "target_page",
                    "target_slug",
                ),
            },
        ),
        (
            "۲. متن بنر",
            {
                "description": "این متن‌ها روی بنر بزرگ صفحه نمایش داده می‌شوند.",
                "fields": (
                    "title",
                    "kicker",
                    "description",
                ),
            },
        ),
        (
            "۳. عکس بنر",
            {
                "description": "این عکس، تصویر بزرگ بالای صفحه است. برای صفحات داخلی بهتر است عکس عریض و سینمایی باشد.",
                "fields": (
                    "image",
                    "image_preview",
                    "mobile_image",
                    "mobile_image_preview",
                ),
            },
        ),
        (
            "۴. نمایش در سایت",
            {
                "description": "اگر فعال خاموش باشد، این بنر استفاده نمی‌شود. اگر چند بنر برای یک صفحه ساختی، عدد کمتر اولویت بالاتر دارد.",
                "fields": (
                    "is_active",
                    "sort_order",
                ),
            },
        ),
        (
            "زمان‌ها",
            {
                "fields": (
                    "created_at",
                    "updated_at",
                ),
                "classes": ("collapse",),
            },
        ),
    )