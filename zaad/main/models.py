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
    slug = models.SlugField(max_length=120)
    section = models.CharField(max_length=20, choices=Section.choices)

    class Meta:
        ordering = ["section", "name"]
        constraints = [
            models.UniqueConstraint(fields=["section", "slug"], name="uniq_category_section_slug"),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.get_section_display()})"


class Tag(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=70, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class Product(TimeStampedModel):
    class StockStatus(models.TextChoices):
        IN_STOCK = "in_stock", "In stock"
        OUT_OF_STOCK = "out_of_stock", "Out of stock"
        PREORDER = "preorder", "Preorder"

    name = models.CharField(max_length=120)
    slug = models.SlugField(max_length=160, unique=True, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cover_image = models.ImageField(upload_to="products/covers/", null=True, blank=True)

    category = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name="products",
        null=True,
        blank=True,
    )
    tags = models.ManyToManyField(Tag, related_name="products", blank=True)

    is_active = models.BooleanField(default=True)
    stock_status = models.CharField(
        max_length=20,
        choices=StockStatus.choices,
        default=StockStatus.IN_STOCK,
    )
    featured = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["sort_order", "-created_at"]

    def __str__(self) -> str:
        return self.name

    def save(self, *args, **kwargs):
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
        if hasattr(self, "flower"):
            return reverse("flower_detail", args=[self.pk, self.slug])
        return reverse("product_detail", args=[self.pk, self.slug])

    @property
    def about(self):
        return self.description

    @property
    def cover(self):
        return self.cover_image

    def get_category_display(self):
        return self.category.name if self.category else ""


class Flower(Product):
    class PackType(models.TextChoices):
        BOX = "box", "Box"
        BOUQUET = "bouquet", "Bouquet"
        BASKET = "basket", "Basket"
        STEM = "stem", "Stem"
        STAND = "stand", "Stand"

    pack_type = models.CharField(max_length=20, choices=PackType.choices)

    class Meta:
        ordering = ["sort_order", "-created_at"]


class BakeryItem(Product):
    size_or_weight = models.CharField(max_length=60, blank=True)
    is_vegan = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "-created_at"]


class GiftItem(Product):
    material = models.CharField(max_length=100, blank=True)
    handmade = models.BooleanField(default=False)

    class Meta:
        ordering = ["sort_order", "-created_at"]


class ProductImage(TimeStampedModel):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="gallery_images")
    image = models.ImageField(upload_to="products/gallery/")
    alt_text = models.CharField(max_length=150, blank=True)
    ordering = models.PositiveIntegerField(default=0)
    is_cover = models.BooleanField(default=False)

    class Meta:
        ordering = ["ordering", "id"]

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
    status = models.CharField(max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]

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
    status = models.CharField(max_length=20, choices=PublishStatus.choices, default=PublishStatus.DRAFT)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["start_at", "-created_at"]

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
    lead_type = models.CharField(max_length=20, choices=LeadType.choices)
    delivery_window = models.CharField(max_length=20, choices=DeliveryWindow.choices)
    preferred_date = models.DateField(null=True, blank=True)
    event_location = models.CharField(max_length=180, blank=True)
    note = models.TextField(blank=True)
    source_page = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.full_name} - {self.get_lead_type_display()}"
