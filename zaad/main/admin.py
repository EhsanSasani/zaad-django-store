from types import MethodType

from django.contrib import admin
from django.utils import timezone

from .models import (
    BakeryItem,
    Category,
    Event,
    Flower,
    GiftItem,
    LeadRequest,
    NewsPost,
    Product,
    ProductImage,
    PublishStatus,
    Tag,
)

admin.site.site_header = "پنل مدیریت زاد"
admin.site.site_title = "مدیریت زاد"
admin.site.index_title = "مدیریت محتوا و محصولات"

_ADMIN_METADATA_LOCALIZED = False


def _localize_admin_metadata():
    model_labels = {
        Category: ("دسته‌بندی", "دسته‌بندی‌ها"),
        Tag: ("برچسب", "برچسب‌ها"),
        Product: ("محصول", "محصولات"),
        Flower: ("گل", "گل‌ها"),
        BakeryItem: ("محصول بیکری", "محصولات بیکری"),
        GiftItem: ("هدیه", "هدایا"),
        ProductImage: ("تصویر محصول", "تصاویر محصول"),
        NewsPost: ("خبر", "اخبار"),
        Event: ("رویداد", "رویدادها"),
        LeadRequest: ("درخواست مشاوره", "درخواست‌های مشاوره"),
    }
    for model, (singular, plural) in model_labels.items():
        model._meta.verbose_name = singular
        model._meta.verbose_name_plural = plural

    field_metadata = {
        Category: {
            "name": ("نام دسته", ""),
            "slug": ("اسلاگ", "برای URL استفاده می‌شود؛ با حروف لاتین و خط تیره وارد کنید."),
            "section": ("بخش", "نوع بخش فروشگاه را انتخاب کنید."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین به‌روزرسانی", ""),
        },
        Tag: {
            "name": ("نام برچسب", ""),
            "slug": ("اسلاگ", "برای URL استفاده می‌شود؛ یکتا و کوتاه باشد."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین به‌روزرسانی", ""),
        },
        Product: {
            "name": ("نام محصول", ""),
            "slug": ("اسلاگ", "در صورت خالی بودن، به‌صورت خودکار از نام ساخته می‌شود."),
            "description": ("توضیحات", ""),
            "price": ("قیمت", "قیمت را به‌صورت عددی وارد کنید."),
            "cover_image": ("تصویر اصلی", "تصویر شاخص محصول برای نمایش در لیست‌ها."),
            "category": ("دسته‌بندی", "دسته محصول را برای مسیر نمایش درست انتخاب کنید."),
            "tags": ("برچسب‌ها", ""),
            "is_active": ("فعال", "در صورت غیرفعال بودن، محصول در سایت نمایش داده نمی‌شود."),
            "stock_status": ("وضعیت موجودی", "وضعیت فعلی دسترسی محصول را مشخص کنید."),
            "featured": ("ویژه", "برای نمایش برجسته در بخش‌های منتخب فعال کنید."),
            "sort_order": ("ترتیب نمایش", "عدد کمتر یعنی نمایش بالاتر."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین به‌روزرسانی", ""),
        },
        Flower: {
            "pack_type": ("نوع بسته‌بندی", "نوع ارائه گل را انتخاب کنید."),
        },
        BakeryItem: {
            "size_or_weight": ("اندازه یا وزن", "مثال: ۱ کیلوگرم یا قطر ۲۰ سانتی‌متر."),
            "is_vegan": ("وگان", "اگر محصول وگان است این گزینه را فعال کنید."),
        },
        GiftItem: {
            "material": ("جنس", "جنس اصلی محصول را کوتاه وارد کنید."),
            "handmade": ("دست‌ساز", "اگر محصول دست‌ساز است این گزینه را فعال کنید."),
        },
        ProductImage: {
            "product": ("محصول", ""),
            "image": ("تصویر", "تصویر را با کیفیت مناسب بارگذاری کنید."),
            "alt_text": ("متن جایگزین", "یک توضیح کوتاه برای دسترس‌پذیری تصویر."),
            "ordering": ("ترتیب", "عدد کمتر یعنی نمایش زودتر در گالری."),
            "is_cover": ("تصویر کاور", "این گزینه را فقط برای یک تصویر اصلی فعال کنید."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین به‌روزرسانی", ""),
        },
        NewsPost: {
            "title": ("عنوان", ""),
            "slug": ("اسلاگ", "برای URL خبر استفاده می‌شود؛ خالی بماند خودکار ساخته می‌شود."),
            "excerpt": ("خلاصه کوتاه", "خلاصه یک‌خطی برای لیست خبرها."),
            "body": ("متن خبر", ""),
            "cover_image": ("تصویر کاور", "تصویر اصلی خبر در صفحه لیست و جزئیات."),
            "status": ("وضعیت انتشار", "پیش‌نویس یا منتشرشده بودن خبر را تعیین کنید."),
            "published_at": ("تاریخ انتشار", "برای زمان‌بندی انتشار، تاریخ را مشخص کنید."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین به‌روزرسانی", ""),
        },
        Event: {
            "title": ("عنوان", ""),
            "slug": ("اسلاگ", "برای URL رویداد استفاده می‌شود؛ خالی بماند خودکار ساخته می‌شود."),
            "description": ("توضیحات", ""),
            "start_at": ("شروع رویداد", ""),
            "end_at": ("پایان رویداد", ""),
            "location": ("مکان", "آدرس یا نام محل برگزاری رویداد."),
            "cover_image": ("تصویر کاور", "تصویر اصلی رویداد برای نمایش در لیست."),
            "status": ("وضعیت انتشار", "پیش‌نویس یا منتشرشده بودن رویداد را تعیین کنید."),
            "published_at": ("تاریخ انتشار", "برای زمان‌بندی انتشار، تاریخ را مشخص کنید."),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین به‌روزرسانی", ""),
        },
        LeadRequest: {
            "full_name": ("نام", ""),
            "mobile": ("شماره موبایل", ""),
            "lead_type": ("نوع درخواست", ""),
            "delivery_window": ("بازه زمانی تحویل", ""),
            "preferred_date": ("تاریخ انتخابی", ""),
            "event_location": ("مکان رویداد", ""),
            "note": ("توضیح کوتاه", ""),
            "source_page": ("صفحه مبدا", ""),
            "created_at": ("زمان ایجاد", ""),
            "updated_at": ("آخرین به‌روزرسانی", ""),
        },
    }
    for model, metadata in field_metadata.items():
        for field_name, (label, help_text) in metadata.items():
            field = model._meta.get_field(field_name)
            field.verbose_name = label
            if help_text:
                field.help_text = help_text

    Category._meta.get_field("section").choices = [
        (Category.Section.FLOWERS, "گل‌ها"),
        (Category.Section.BAKERY, "بیکری"),
        (Category.Section.GIFTS, "هدایا"),
    ]
    Product._meta.get_field("stock_status").choices = [
        (Product.StockStatus.IN_STOCK, "موجود"),
        (Product.StockStatus.OUT_OF_STOCK, "ناموجود"),
        (Product.StockStatus.PREORDER, "پیش‌سفارش"),
    ]
    Flower._meta.get_field("pack_type").choices = [
        (Flower.PackType.BOX, "باکس"),
        (Flower.PackType.BOUQUET, "دسته‌گل"),
        (Flower.PackType.BASKET, "سبد"),
        (Flower.PackType.STEM, "شاخه‌ای"),
        (Flower.PackType.STAND, "استند"),
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

    def history_view(self, request, object_id, extra_context=None):
        _ensure_admin_metadata()
        return super().history_view(request, object_id, extra_context)

    def delete_view(self, request, object_id, extra_context=None):
        _ensure_admin_metadata()
        return super().delete_view(request, object_id, extra_context)


class LocalizedInlineMixin:
    def get_formset(self, request, obj=None, **kwargs):
        _ensure_admin_metadata()
        return super().get_formset(request, obj, **kwargs)


class ProductActionsMixin:
    actions = ("activate_selected", "deactivate_selected", "mark_featured", "remove_featured")

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


class PublishActionsMixin:
    actions = ("publish_selected", "unpublish_selected")

    @admin.action(description="انتشار موارد انتخاب‌شده")
    def publish_selected(self, request, queryset):
        updated = queryset.update(status=PublishStatus.PUBLISHED, published_at=timezone.now())
        self.message_user(request, f"{updated} مورد منتشر شد.")

    @admin.action(description="بازگردانی به پیش‌نویس")
    def unpublish_selected(self, request, queryset):
        updated = queryset.update(status=PublishStatus.DRAFT, published_at=None)
        self.message_user(request, f"{updated} مورد به پیش‌نویس برگشت.")


# --- اینلاین تصاویر محصول در فرم ادمین ---
class ProductImageInline(LocalizedInlineMixin, admin.TabularInline):
    model = ProductImage
    extra = 0
    fields = ("image", "alt_text", "ordering", "is_cover", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("ordering", "id")
    verbose_name = "تصویر گالری"
    verbose_name_plural = "تصاویر گالری"


# --- ادمین داده‌های مرجع: دسته‌بندی ---
@admin.register(Category)
class CategoryAdmin(LocalizedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "section", "slug", "updated_at")
    list_filter = ("section", "created_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("section", "name")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("name", "section", "slug")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# --- ادمین داده‌های مرجع: برچسب ---
@admin.register(Tag)
class TagAdmin(LocalizedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "slug", "updated_at")
    search_fields = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("name",)
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("name", "slug")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


class BaseProductAdmin(ProductActionsMixin, LocalizedAdminMixin, admin.ModelAdmin):
    list_display = (
        "name",
        "category",
        "price",
        "stock_status",
        "is_active",
        "featured",
        "sort_order",
        "updated_at",
    )
    list_filter = ("is_active", "featured", "stock_status", "category__section", "category")
    search_fields = ("name", "slug", "description", "category__name", "tags__name")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("name",)}
    ordering = ("sort_order", "-updated_at")
    list_editable = ("is_active", "featured", "sort_order")
    inlines = [ProductImageInline]
    date_hierarchy = "created_at"
    list_select_related = ("category",)
    autocomplete_fields = ("category", "tags")
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("name", "slug", "description")}),
        ("دسته‌بندی و برچسب", {"fields": ("category", "tags")}),
        ("قیمت و موجودی", {"fields": ("price", "stock_status", "is_active")}),
        ("نمایش", {"fields": ("cover_image", "featured", "sort_order")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# --- ادمین محصول پایه ---
@admin.register(Product)
class ProductAdmin(BaseProductAdmin):
    list_display = (
        "name",
        "product_type",
        "category",
        "price",
        "stock_status",
        "is_active",
        "featured",
        "sort_order",
        "updated_at",
    )

    @admin.display(description="نوع محصول")
    def product_type(self, obj):
        if hasattr(obj, "flower"):
            return "گل"
        if hasattr(obj, "bakeryitem"):
            return "بیکری"
        if hasattr(obj, "giftitem"):
            return "هدیه"
        return "پایه"


# --- ادمین انواع محصول: گل ---
@admin.register(Flower)
class FlowerAdmin(BaseProductAdmin):
    list_display = (
        "name",
        "pack_type",
        "category",
        "price",
        "stock_status",
        "is_active",
        "featured",
        "sort_order",
        "updated_at",
    )
    list_filter = ("pack_type",) + BaseProductAdmin.list_filter
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("name", "slug", "description")}),
        ("ویژگی گل", {"fields": ("pack_type",)}),
        ("دسته‌بندی و برچسب", {"fields": ("category", "tags")}),
        ("قیمت و موجودی", {"fields": ("price", "stock_status", "is_active")}),
        ("نمایش", {"fields": ("cover_image", "featured", "sort_order")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# --- ادمین انواع محصول: بیکری ---
@admin.register(BakeryItem)
class BakeryItemAdmin(BaseProductAdmin):
    list_display = (
        "name",
        "size_or_weight",
        "is_vegan",
        "category",
        "price",
        "stock_status",
        "is_active",
        "featured",
        "sort_order",
        "updated_at",
    )
    list_filter = ("is_vegan",) + BaseProductAdmin.list_filter
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("name", "slug", "description")}),
        ("ویژگی بیکری", {"fields": ("size_or_weight", "is_vegan")}),
        ("دسته‌بندی و برچسب", {"fields": ("category", "tags")}),
        ("قیمت و موجودی", {"fields": ("price", "stock_status", "is_active")}),
        ("نمایش", {"fields": ("cover_image", "featured", "sort_order")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# --- ادمین انواع محصول: کانسپت‌استور ---
@admin.register(GiftItem)
class GiftItemAdmin(BaseProductAdmin):
    list_display = (
        "name",
        "material",
        "handmade",
        "category",
        "price",
        "stock_status",
        "is_active",
        "featured",
        "sort_order",
        "updated_at",
    )
    list_filter = ("handmade",) + BaseProductAdmin.list_filter
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("name", "slug", "description")}),
        ("ویژگی هدیه", {"fields": ("material", "handmade")}),
        ("دسته‌بندی و برچسب", {"fields": ("category", "tags")}),
        ("قیمت و موجودی", {"fields": ("price", "stock_status", "is_active")}),
        ("نمایش", {"fields": ("cover_image", "featured", "sort_order")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# --- ادمین گالری تصاویر ---
@admin.register(ProductImage)
class ProductImageAdmin(LocalizedAdminMixin, admin.ModelAdmin):
    list_display = ("product", "ordering", "is_cover", "created_at", "updated_at")
    list_filter = ("is_cover", "created_at")
    search_fields = ("product__name", "product__slug", "alt_text")
    ordering = ("product", "ordering")
    list_editable = ("ordering", "is_cover")
    autocomplete_fields = ("product",)
    readonly_fields = ("created_at", "updated_at")
    list_select_related = ("product",)
    fieldsets = (
        ("اطلاعات تصویر", {"fields": ("product", "image", "alt_text")}),
        ("نمایش", {"fields": ("ordering", "is_cover")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# --- ادمین محتوایی: خبر ---
@admin.register(NewsPost)
class NewsPostAdmin(PublishActionsMixin, LocalizedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "status", "published_at", "created_at", "updated_at")
    list_filter = ("status", "published_at", "created_at")
    search_fields = ("title", "slug", "excerpt", "body")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("-published_at", "-created_at")
    date_hierarchy = "published_at"
    list_editable = ("status",)
    save_on_top = True
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "slug", "excerpt", "body")}),
        ("رسانه و انتشار", {"fields": ("cover_image", "status", "published_at")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


# --- ادمین محتوایی: رویداد ---
@admin.register(Event)
class EventAdmin(PublishActionsMixin, LocalizedAdminMixin, admin.ModelAdmin):
    list_display = ("title", "status", "start_at", "end_at", "location", "published_at")
    list_filter = ("status", "start_at", "end_at", "published_at")
    search_fields = ("title", "slug", "description", "location")
    readonly_fields = ("created_at", "updated_at")
    prepopulated_fields = {"slug": ("title",)}
    ordering = ("start_at", "-created_at")
    date_hierarchy = "start_at"
    list_editable = ("status",)
    save_on_top = True
    fieldsets = (
        ("اطلاعات اصلی", {"fields": ("title", "slug", "description")}),
        ("زمان و مکان", {"fields": ("start_at", "end_at", "location")}),
        ("رسانه و انتشار", {"fields": ("cover_image", "status", "published_at")}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )


@admin.register(LeadRequest)
class LeadRequestAdmin(LocalizedAdminMixin, admin.ModelAdmin):
    list_display = (
        "full_name",
        "mobile",
        "lead_type",
        "delivery_window",
        "preferred_date",
        "created_at",
    )
    list_filter = ("lead_type", "delivery_window", "created_at")
    search_fields = ("full_name", "mobile", "note", "event_location", "source_page")
    readonly_fields = ("created_at", "updated_at")
    ordering = ("-created_at",)
    fieldsets = (
        ("اطلاعات متقاضی", {"fields": ("full_name", "mobile", "lead_type")}),
        ("جزئیات سفارش", {"fields": ("delivery_window", "preferred_date", "event_location", "note")}),
        ("فنی", {"fields": ("source_page",)}),
        ("زمان‌ها", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )
