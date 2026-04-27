from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Category(TimeStampedModel):
    class Section(models.TextChoices):
        FLOWERS = "flowers", "Flowers"
        BAKERY = "bakery", "Bakery"
        GIFTS = "gifts", "Gifts"

    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, db_index=True, blank=True)

    section = models.CharField(
        max_length=20,
        choices=Section.choices,
        db_index=True,
    )

    description = models.TextField(blank=True)

    cover_image = models.ImageField(
        upload_to="categories/",
        blank=True,
        null=True,
    )

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["section", "sort_order", "name"]
        verbose_name = "دسته اولیه"
        verbose_name_plural = "دسته‌های اولیه"
        constraints = [
            models.UniqueConstraint(
                fields=["section", "slug"],
                name="uniq_category_section_slug",
            ),
        ]
        indexes = [
            models.Index(fields=["section", "is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_section_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "category"
            slug = base
            index = 2

            while Category.objects.filter(
                section=self.section,
                slug=slug,
            ).exclude(pk=self.pk).exists():
                slug = f"{base}-{index}"
                index += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Tag(TimeStampedModel):
    class TagType(models.TextChoices):
        OCCASION = "occasion", "Occasion"
        BUDGET = "budget", "Budget"
        VIBE = "vibe", "Vibe"

    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=70, unique=True, blank=True)

    tag_type = models.CharField(
        max_length=20,
        choices=TagType.choices,
        default=TagType.OCCASION,
        db_index=True,
    )

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["tag_type", "sort_order", "name"]
        verbose_name = "برچسب"
        verbose_name_plural = "برچسب‌ها"
        constraints = [
            models.UniqueConstraint(
                fields=["tag_type", "name"],
                name="uniq_tag_type_name",
            ),
        ]
        indexes = [
            models.Index(fields=["tag_type", "is_active", "sort_order"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_tag_type_display()})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.name) or "tag"
            slug = base
            index = 2

            while Tag.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{index}"
                index += 1

            self.slug = slug

        super().save(*args, **kwargs)


class Product(TimeStampedModel):
    class PricingType(models.TextChoices):
        FIXED = "fixed", "Fixed Price"
        INQUIRY = "inquiry", "Call / Inquiry"

    class StockStatus(models.TextChoices):
        IN_STOCK = "in_stock", "In stock"
        OUT_OF_STOCK = "out_of_stock", "Out of stock"
        PREORDER = "preorder", "Preorder"

    class PublishStatus(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=160, unique=True, blank=True)

    description = models.TextField(blank=True)

    pricing_type = models.CharField(
        max_length=20,
        choices=PricingType.choices,
        default=PricingType.INQUIRY,
        db_index=True,
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        help_text="قیمت را به تومان و فقط عددی وارد کنید.",
    )

    cover_image = models.ImageField(
        upload_to="products/covers/",
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        "Category",
        on_delete=models.PROTECT,
        related_name="products",
    )

    tags = models.ManyToManyField(
        "Tag",
        related_name="products",
        blank=True,
    )

    is_active = models.BooleanField(default=True, db_index=True)

    publish_status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )

    stock_status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
        db_index=True,
    )

    featured = models.BooleanField(default=False, db_index=True)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "-created_at"]
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        indexes = [
            models.Index(fields=["category", "is_active", "publish_status"]),
            models.Index(fields=["featured", "sort_order"]),
            models.Index(fields=["sort_order", "-created_at"]),
        ]

    def __str__(self):
        return self.name

    @property
    def section(self):
        if self.category_id:
            return self.category.section
        return None

    @property
    def is_published(self):
        return self.is_active and self.publish_status == self.PublishStatus.PUBLISHED

    @property
    def display_price(self):
        if self.pricing_type == self.PricingType.INQUIRY or self.price is None:
            return "استعلام قیمت"

        return f"{int(self.price):,} تومان"

    def save(self, *args, **kwargs):
        if self.pricing_type == self.PricingType.INQUIRY:
            self.price = None

        if not self.slug:
            base = slugify(self.name) or "product"
            slug = base
            index = 2

            while Product.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{index}"
                index += 1

            self.slug = slug

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
        verbose_name = "گل"
        verbose_name_plural = "گل‌ها"


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
        "Product",
        on_delete=models.CASCADE,
        related_name="gallery_images",
    )

    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=150, blank=True)
    ordering = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["ordering", "id"]
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"

    def __str__(self) -> str:
        return f"{self.product.name} - image {self.ordering}"


class PublishStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    PUBLISHED = "published", "Published"


class NewsPost(TimeStampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    excerpt = models.CharField(max_length=300, blank=True)
    body = models.TextField()
    cover_image = models.ImageField(upload_to="news/covers/", null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "خبر"
        verbose_name_plural = "اخبار"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "news"
            slug = base
            index = 2

            while NewsPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{index}"
                index += 1

            self.slug = slug

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("blog_detail", args=[self.slug])


class Event(TimeStampedModel):
    title = models.CharField(max_length=180)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    location = models.CharField(max_length=200)
    cover_image = models.ImageField(upload_to="events/covers/", null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=PublishStatus.choices,
        default=PublishStatus.DRAFT,
        db_index=True,
    )
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["start_at", "-created_at"]
        verbose_name = "رویداد"
        verbose_name_plural = "رویدادها"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title) or "event"
            slug = base
            index = 2

            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{index}"
                index += 1

            self.slug = slug

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

    full_name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=20)

    lead_type = models.CharField(
        max_length=20,
        choices=LeadType.choices,
    )

    product = models.ForeignKey(
        "Product",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_requests",
    )

    delivery_window = models.CharField(
        max_length=20,
        choices=DeliveryWindow.choices,
    )

    preferred_date = models.DateField(null=True, blank=True)
    event_location = models.CharField(max_length=180, blank=True)
    note = models.TextField(blank=True)
    source_page = models.CharField(max_length=255, blank=True)

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
    title = models.CharField(max_length=180)
    kicker = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="heroes/home/")
    mobile_image = models.ImageField(
        upload_to="heroes/home/mobile/",
        blank=True,
        null=True,
    )

    primary_button_text = models.CharField(max_length=60, blank=True)
    primary_button_url = models.CharField(max_length=255, blank=True)

    secondary_button_text = models.CharField(max_length=60, blank=True)
    secondary_button_url = models.CharField(max_length=255, blank=True)

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

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
        SUBCATEGORY = "subcategory", "دسته‌بندی"
        ITEM = "item", "صفحه محصول"

    title = models.CharField(max_length=180)
    kicker = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)

    image = models.ImageField(upload_to="heroes/pages/")
    mobile_image = models.ImageField(
        upload_to="heroes/pages/mobile/",
        blank=True,
        null=True,
    )

    target_page = models.CharField(
        max_length=30,
        choices=TargetPage.choices,
    )

    target_slug = models.CharField(
        max_length=120,
        blank=True,
        help_text="برای دسته‌بندی یا صفحه خاص، اسلاگ را وارد کنید. مثال: bouquet",
    )

    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)

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