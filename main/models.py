import uuid

from django.db import models
from django.db.models import F, Q
from django.urls import reverse
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField("زمان ایجاد", auto_now_add=True)
    updated_at = models.DateTimeField("آخرین ویرایش", auto_now=True)

    class Meta:
        abstract = True


def make_unique_slug(instance, value, slug_field_name="slug", queryset=None):
    slug = slugify(value, allow_unicode=True)

    if not slug:
        slug = f"item-{uuid.uuid4().hex[:8]}"

    if queryset is None:
        queryset = instance.__class__.objects.all()

    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    base_slug = slug
    index = 2

    while queryset.filter(**{slug_field_name: slug}).exists():
        slug = f"{base_slug}-{index}"
        index += 1

    return slug


class Category(TimeStampedModel):
    class Section(models.TextChoices):
        FLOWERS = "flowers", "گل‌ها"
        BAKERY = "bakery", "بیکری"
        GIFTS = "gifts", "هدایا"
        EVENTS = "events", "رویدادها"

    name = models.CharField("نام زیر‌دسته", max_length=100)
    slug = models.SlugField(
        "اسلاگ",
        max_length=120,
        db_index=True,
        blank=True,
        allow_unicode=True,
        help_text="اگر خالی بماند، خودکار از نام ساخته می‌شود. برای لینک بهتر، انگلیسی وارد کن؛ مثل bouquet یا box.",
    )

    section = models.CharField(
        "بخش اصلی",
        max_length=20,
        choices=Section.choices,
        db_index=True,
    )

    description = models.TextField("توضیح کوتاه", blank=True)

    cover_image = models.ImageField(
        "تصویر زیر‌دسته",
        upload_to="categories/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField("فعال باشد؟", default=True, db_index=True)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["section", "sort_order", "name"]
        verbose_name = "زیر‌دسته"
        verbose_name_plural = "زیر‌دسته‌ها"
        constraints = [
            models.UniqueConstraint(
                fields=["section", "slug"],
                name="uniq_category_section_slug",
            ),
            models.UniqueConstraint(
                fields=["section", "name"],
                name="uniq_category_section_name",
            ),
        ]
        indexes = [
            models.Index(fields=["section", "is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.get_section_display()} / {self.name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            queryset = Category.objects.filter(section=self.section)
            self.slug = make_unique_slug(self, self.name, queryset=queryset)
        else:
            self.slug = slugify(self.slug, allow_unicode=True)

        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    name = models.CharField("نام برچسب", max_length=50, unique=True)
    slug = models.SlugField(
        "اسلاگ",
        max_length=80,
        unique=True,
        blank=True,
        allow_unicode=True,
        help_text="اگر خالی بماند، خودکار ساخته می‌شود. برای لینک بهتر، انگلیسی وارد کن؛ مثل birthday یا romantic.",
    )

    description = models.TextField("توضیح کوتاه", blank=True)

    cover_image = models.ImageField(
        "تصویر کارت مناسبتی",
        upload_to="tags/",
        blank=True,
        null=True,
        help_text="برای کارت‌های مناسبتی مثل تولد، تسلیت، عاشقانه و ...",
    )

    is_occasion = models.BooleanField(
        "در کارت‌های مناسبتی نمایش داده شود؟",
        default=True,
        db_index=True,
    )

    is_active = models.BooleanField("فعال باشد؟", default=True, db_index=True)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["sort_order", "name"]
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        indexes = [
            models.Index(fields=["is_occasion", "is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_unique_slug(self, self.name)
        else:
            self.slug = slugify(self.slug, allow_unicode=True)

        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    class PricingType(models.TextChoices):
        FIXED = "fixed", "قیمت ثابت"
        INQUIRY = "inquiry", "استعلام قیمت"

    class StockStatus(models.TextChoices):
        IN_STOCK = "in_stock", "موجود"
        OUT_OF_STOCK = "out_of_stock", "ناموجود"
        PREORDER = "preorder", "پیش‌سفارش"

    class PublishStatus(models.TextChoices):
        DRAFT = "draft", "پیش‌نویس"
        PUBLISHED = "published", "منتشرشده"

    name = models.CharField("نام محصول", max_length=120)
    slug = models.SlugField(
        "اسلاگ",
        max_length=160,
        unique=True,
        blank=True,
        allow_unicode=True,
        help_text="اگر خالی بماند، خودکار از نام محصول ساخته می‌شود.",
    )

    description = models.TextField("توضیحات", blank=True)

    pricing_type = models.CharField(
        "نوع قیمت‌گذاری",
        max_length=20,
        choices=PricingType.choices,
        default=PricingType.INQUIRY,
        db_index=True,
    )

    price = models.DecimalField(
        "قیمت به تومان",
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="فقط عدد وارد کن؛ مثلاً 2500000. اگر قیمت استعلامی باشد، این فیلد خالی می‌ماند.",
    )
    price_usd = models.DecimalField(
    "قیمت دلاری",
    max_digits=8,
    decimal_places=2,
    null=True,
    blank=True,
    )

    cover_image = models.ImageField(
        "تصویر اصلی",
        upload_to="products/covers/",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        Category,
        verbose_name="زیر‌دسته",
        on_delete=models.PROTECT,
        related_name="products",
        help_text="نوع فیزیکی محصول؛ مثل دسته گل، باکس، استند، کیک تولد، شمع و ...",
    )

    tags = models.ManyToManyField(
        Tag,
        verbose_name="برچسب‌ها",
        related_name="products",
        blank=True,
        help_text="مناسبت یا کاربرد محصول؛ مثل تولد، تسلیت، عذرخواهی، خاص، عاشقانه.",
    )

    is_active = models.BooleanField("فعال باشد؟", default=True, db_index=True)

    publish_status = models.CharField(
        "وضعیت انتشار",
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )

    stock_status = models.CharField(
        "وضعیت موجودی",
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
        db_index=True,
    )

    featured = models.BooleanField("ویژه باشد؟", default=False, db_index=True)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["sort_order", "-created_at"]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        constraints = [
            models.CheckConstraint(
                condition=Q(price__isnull=True) | Q(price__gte=0),
                name="product_price_is_positive_or_null",
            ),
        ]
        indexes = [
            models.Index(fields=["category", "is_active", "publish_status"]),
            models.Index(fields=["featured", "sort_order"]),
            models.Index(fields=["sort_order", "-created_at"]),
            models.Index(fields=["pricing_type", "stock_status"]),
        ]

    def __str__(self):
        return self.name

    @property
    def section(self):
        if self.category_id:
            return self.category.section
        return None

    @property
    def section_display(self):
        if self.category_id:
            return self.category.get_section_display()
        return "-"

    @property
    def is_published(self):
        return self.is_active and self.publish_status == self.PublishStatus.PUBLISHED

    @property
    def display_price(self):
        if self.pricing_type == self.PricingType.INQUIRY or self.price is None:
            return "Call for Price"

        price_parts = [f"{int(self.price):,} IRT"]

        if self.price_usd:
            price_parts.append(f"{int(self.price_usd)} USD")

        return " · ".join(price_parts)

    def save(self, *args, **kwargs):
        if self.pricing_type == self.PricingType.INQUIRY:
            self.price = None

        if not self.slug:
            self.slug = make_unique_slug(self, self.name)
        else:
            self.slug = slugify(self.slug, allow_unicode=True)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.pk, self.slug])


class FlowerManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            category__section=Category.Section.FLOWERS,
        )


class BakeryItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            category__section=Category.Section.BAKERY,
        )


class GiftItemManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            category__section=Category.Section.GIFTS,
        )


class Flower(Product):
    objects = FlowerManager()

    class Meta:
        proxy = True
        ordering = ["sort_order", "-created_at"]
        verbose_name = "محصول گل"
        verbose_name_plural = "محصولات گل"


class BakeryItem(Product):
    objects = BakeryItemManager()

    class Meta:
        proxy = True
        ordering = ["sort_order", "-created_at"]
        verbose_name = "محصول بیکری"
        verbose_name_plural = "محصولات بیکری"


class GiftItem(Product):
    objects = GiftItemManager()

    class Meta:
        proxy = True
        ordering = ["sort_order", "-created_at"]
        verbose_name = "هدیه"
        verbose_name_plural = "هدایا"


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(
        Product,
        verbose_name="محصول",
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )

    image = models.ImageField("تصویر", upload_to="products/gallery/")
    alt_text = models.CharField("متن جایگزین", max_length=150, blank=True)
    ordering = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        indexes = [
            models.Index(fields=["product", "ordering"]),
        ]

    def __str__(self) -> str:
        return f"{self.product.name} - image {self.ordering}"


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "پیش‌نویس"
    PUBLISHED = "published", "منتشرشده"


class NewsPost(TimeStampedModel):
    title = models.CharField("عنوان", max_length=180)
    slug = models.SlugField("اسلاگ", max_length=200, unique=True, blank=True, allow_unicode=True)
    excerpt = models.CharField("خلاصه", max_length=300, blank=True)
    body = models.TextField("متن")
    cover_image = models.ImageField("تصویر کاور", upload_to="news/covers/", null=True, blank=True)
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField("تاریخ انتشار", null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "خبر"
        verbose_name_plural = "اخبار"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_unique_slug(self, self.title)
        else:
            self.slug = slugify(self.slug, allow_unicode=True)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.slug])


class Event(TimeStampedModel):
    title = models.CharField("عنوان", max_length=180)
    slug = models.SlugField("اسلاگ", max_length=200, unique=True, blank=True, allow_unicode=True)
    description = models.TextField("توضیحات")
    start_at = models.DateTimeField("شروع")
    end_at = models.DateTimeField("پایان")
    location = models.CharField("مکان", max_length=200)
    cover_image = models.ImageField("تصویر کاور", upload_to="events/covers/", null=True, blank=True)
    status = models.CharField(
        "وضعیت",
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField("تاریخ انتشار", null=True, blank=True)

    class Meta:
        ordering = ["start_at", "-created_at"]
        verbose_name = "رویداد"
        verbose_name_plural = "رویدادها"
        constraints = [
            models.CheckConstraint(
                condition=Q(end_at__gt=F("start_at")),
                name="event_end_after_start",
            ),
        ]

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = make_unique_slug(self, self.title)
        else:
            self.slug = slugify(self.slug, allow_unicode=True)

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("event_detail", args=[self.slug])


class LeadRequest(TimeStampedModel):
    class LeadType(models.TextChoices):
        FLOWER = "flower", "گل"
        BAKERY = "bakery", "بیکری"
        GIFT = "gift", "هدیه"
        EVENT = "event", "رویداد"

    class DeliveryWindow(models.TextChoices):
        TODAY = "today", "امروز"
        TOMORROW = "tomorrow", "فردا"
        PICK_DATE = "pick_date", "تاریخ انتخابی"

    full_name = models.CharField("نام", max_length=120)
    mobile = models.CharField("شماره موبایل", max_length=20)

    lead_type = models.CharField(
        "نوع درخواست",
        max_length=20,
        choices=LeadType.choices,
    )

    product = models.ForeignKey(
        Product,
        verbose_name="محصول",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_requests",
    )

    delivery_window = models.CharField(
        "بازه تحویل",
        max_length=20,
        choices=DeliveryWindow.choices,
    )

    preferred_date = models.DateField("تاریخ انتخابی", null=True, blank=True)
    event_location = models.CharField("مکان رویداد", max_length=180, blank=True)
    note = models.TextField("یادداشت", blank=True)
    source_page = models.CharField("صفحه مبدا", max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "درخواست مشاوره"
        verbose_name_plural = "درخواست‌های مشاوره"

    def __str__(self) -> str:
        base = f"{self.full_name} - {self.get_lead_type_display()}"
        if self.product:
            return f"{base} - {self.product.name}"
        return base


class HomeHeroSlide(TimeStampedModel):
    title = models.CharField("عنوان", max_length=180)
    kicker = models.CharField("متن کوتاه بالا", max_length=100, blank=True)
    description = models.TextField("توضیح", blank=True)

    image = models.ImageField("تصویر اصلی", upload_to="heroes/home/")
    mobile_image = models.ImageField(
        "تصویر موبایل",
        upload_to="heroes/home/mobile/",
        blank=True,
        null=True,
    )

    primary_button_text = models.CharField("متن دکمه اصلی", max_length=60, blank=True)
    primary_button_url = models.CharField("لینک دکمه اصلی", max_length=255, blank=True)

    secondary_button_text = models.CharField("متن دکمه دوم", max_length=60, blank=True)
    secondary_button_url = models.CharField("لینک دکمه دوم", max_length=255, blank=True)

    is_active = models.BooleanField("فعال باشد؟", default=True)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["sort_order", "id"]
        verbose_name = "اسلاید هیروی خانه"
        verbose_name_plural = "اسلایدهای هیروی خانه"

    def __str__(self) -> str:
        return self.title


class SiteHero(TimeStampedModel):
    class TargetPage(models.TextChoices):
        FLOWERS = "flowers", "گل‌ها"
        BAKERY = "bakery", "بیکری"
        GIFTS = "gifts", "هدایا"
        EVENTS = "events", "رویدادها"
        OCCASIONS = "occasions", "مناسبت‌ها"
        CONTACT = "contact", "تماس با ما"
        VISIT = "visit", "بازدید حضوری"
        FAQ = "faq", "سوالات پرتکرار"
        BLOG = "blog", "بلاگ"
        MASHHAD = "mashhad", "سفارش در مشهد"
        SUBCATEGORY = "subcategory", "زیر‌دسته"
        ITEM = "item", "صفحه محصول"

    title = models.CharField("عنوان", max_length=180)
    kicker = models.CharField("متن کوتاه بالا", max_length=100, blank=True)
    description = models.TextField("توضیح", blank=True)

    image = models.ImageField("تصویر اصلی", upload_to="heroes/pages/")
    mobile_image = models.ImageField(
        "تصویر موبایل",
        upload_to="heroes/pages/mobile/",
        blank=True,
        null=True,
    )

    target_page = models.CharField(
        "صفحه هدف",
        max_length=30,
        choices=TargetPage.choices,
    )

    target_slug = models.CharField(
        "اسلاگ هدف",
        max_length=120,
        blank=True,
        help_text="برای زیر‌دسته یا صفحه خاص، اسلاگ را وارد کن. مثال: bouquet",
    )

    is_active = models.BooleanField("فعال باشد؟", default=True)
    sort_order = models.PositiveIntegerField("ترتیب نمایش", default=0)

    class Meta:
        ordering = ["target_page", "sort_order", "id"]
        verbose_name = "هیروی صفحه"
        verbose_name_plural = "هیروهای صفحات"
        constraints = [
            models.UniqueConstraint(
                fields=["target_page", "target_slug", "sort_order"],
                name="uniq_sitehero_target_slug_sort",
            ),
        ]

    def __str__(self) -> str:
        if self.target_slug:
            return f"{self.get_target_page_display()} - {self.target_slug}"
        return self.get_target_page_display()