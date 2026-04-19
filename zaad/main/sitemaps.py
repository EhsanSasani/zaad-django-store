from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import Event, NewsPost, Product, PublishStatus


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return [
            "index",
            "flowers",
            "bakery",
            "gifts",
            "events",
            "blog",
            "visit",
            "contact",
            "faq",
            "mashhad_hub",
            "mashhad_flower_order",
            "mashhad_flower_delivery",
        ]

    def location(self, item):
        return reverse(item)


class FlowerSubcategorySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return ["bouquet", "box", "stand", "plant"]

    def location(self, item):
        return reverse("flower_subcategory", args=[item])


class ProductSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Product.objects.filter(is_active=True).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at


class EventSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Event.objects.filter(status=PublishStatus.PUBLISHED).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return NewsPost.objects.filter(status=PublishStatus.PUBLISHED).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "flower_subcategories": FlowerSubcategorySitemap,
    "products": ProductSitemap,
    "events": EventSitemap,
    "blog": BlogSitemap,
}
