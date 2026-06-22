from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Category, Event, LeadRequest, Product, PublishStatus


class MainViewsTests(TestCase):
    def setUp(self):
        self.flowers_category = Category.objects.create(
            name="Bouquet",
            slug="bouquet",
            section=Category.Section.FLOWERS,
        )
        self.bakery_category = Category.objects.create(
            name="Daily Bakery",
            slug="daily-bakery",
            section=Category.Section.BAKERY,
        )
        self.gifts_category = Category.objects.create(
            name="Gift Box",
            slug="gift-box",
            section=Category.Section.GIFTS,
        )

        self.flower = Product.objects.create(
            name="Red Rose",
            pricing_type=Product.PricingType.FIXED,
            price=450000,
            publish_status=Product.PublishStatus.PUBLISHED,
            category=self.flowers_category,
            description="Test flower product",
        )
        self.bakery = Product.objects.create(
            name="Chocolate Cake",
            pricing_type=Product.PricingType.FIXED,
            price=560000,
            publish_status=Product.PublishStatus.PUBLISHED,
            category=self.bakery_category,
            description="Test bakery product",
        )
        self.gift_product = Product.objects.create(
            name="Gift Box",
            pricing_type=Product.PricingType.FIXED,
            price=320000,
            publish_status=Product.PublishStatus.PUBLISHED,
            category=self.gifts_category,
            description="Test gift product",
        )

        self.published_event = Event.objects.create(
            title="Published Event",
            description="Test event",
            start_at=timezone.now() + timedelta(days=2),
            end_at=timezone.now() + timedelta(days=2, hours=3),
            location="Mashhad",
            status=PublishStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        self.draft_event = Event.objects.create(
            title="Draft Event",
            description="Draft",
            start_at=timezone.now() + timedelta(days=5),
            end_at=timezone.now() + timedelta(days=5, hours=2),
            location="Mashhad",
            status=PublishStatus.DRAFT,
        )

    def test_index_page_loads(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("flowers"))

    def test_legacy_section_redirects_to_new_category(self):
        response = self.client.get(reverse("index"), {"section": "bakery"})
        self.assertRedirects(response, reverse("bakery"), fetch_redirect_response=False)

    def test_flowers_landing_page_loads(self):
        response = self.client.get(reverse("flowers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.flower.product_code)

    def test_category_page_contains_subcategory_link(self):
        response = self.client.get(reverse("bakery"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse("bakery_subcategory", args=["daily-bakery"]))

    def test_bakery_and_gifts_use_the_shared_collection_landing(self):
        for route_name, product, category in (
            ("bakery", self.bakery, self.bakery_category),
            ("gifts", self.gift_product, self.gifts_category),
        ):
            with self.subTest(route_name=route_name):
                response = self.client.get(reverse(route_name))
                self.assertTemplateUsed(response, "flowers_landing.html")
                self.assertContains(response, 'class="flowers-hero"')
                self.assertContains(response, f'data-filter="{category.slug}"')
                self.assertContains(response, f'data-category="{category.slug}"')
                self.assertContains(response, product.product_code)

    def test_subcategory_page_loads(self):
        response = self.client.get(reverse("flower_subcategory", args=["bouquet"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.flower.display_name)

    def test_events_page_shows_only_published(self):
        response = self.client.get(reverse("events"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_event.title)
        self.assertNotContains(response, self.draft_event.title)

    def test_visit_contact_and_faq_pages_load(self):
        self.assertEqual(self.client.get(reverse("visit")).status_code, 200)
        self.assertEqual(self.client.get(reverse("contact")).status_code, 200)
        self.assertEqual(self.client.get(reverse("faq")).status_code, 200)

    def test_detail_redirects_when_slug_is_wrong(self):
        response = self.client.get(reverse("flower_detail", args=[self.flower.pk, "wrong-slug"]))
        self.assertRedirects(
            response,
            reverse("flower_detail", args=[self.flower.pk, self.flower.slug]),
            fetch_redirect_response=False,
        )

    def test_lead_form_submit_creates_row(self):
        response = self.client.post(
            reverse("lead_request"),
            {
                "full_name": "Test User",
                "mobile": "09121234567",
                "lead_type": LeadRequest.LeadType.FLOWER,
                "delivery_window": LeadRequest.DeliveryWindow.TODAY,
                "note": "Test",
                "next": reverse("contact"),
                "source_page": "/contact/",
            },
        )
        self.assertRedirects(response, reverse("contact"), fetch_redirect_response=False)
        self.assertEqual(LeadRequest.objects.count(), 1)

    def test_robots_and_sitemap_routes(self):
        self.assertEqual(self.client.get(reverse("robots_txt")).status_code, 200)
        self.assertEqual(self.client.get(reverse("sitemap")).status_code, 200)
