from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import BakeryItem, Category, Event, Flower, LeadRequest, PublishStatus


class MainViewsTests(TestCase):
    def setUp(self):
        flowers_category, _ = Category.objects.get_or_create(
            slug="bouquet",
            section=Category.Section.FLOWERS,
            defaults={"name": "دسته گل"},
        )
        bakery_category, _ = Category.objects.get_or_create(
            slug="daily-bakery",
            section=Category.Section.BAKERY,
            defaults={"name": "بیکری روز"},
        )
        gifts_category, _ = Category.objects.get_or_create(
            slug="gift-box",
            section=Category.Section.GIFTS,
            defaults={"name": "هدیه"},
        )

        self.flower = Flower.objects.create(
            name="رز قرمز",
            pack_type=Flower.PackType.BOUQUET,
            price=450000,
            category=flowers_category,
            description="تست محصول",
        )
        self.bakery = BakeryItem.objects.create(
            name="کیک شکلاتی",
            size_or_weight="۱ کیلو",
            price=560000,
            category=bakery_category,
            description="نمونه بیکری",
        )
        self.gift_flower = Flower.objects.create(
            name="گل هدیه",
            pack_type=Flower.PackType.BOX,
            price=320000,
            category=gifts_category,
            description="نمونه هدیه",
        )

        self.published_event = Event.objects.create(
            title="رویداد منتشرشده",
            description="رویداد تست",
            start_at=timezone.now() + timedelta(days=2),
            end_at=timezone.now() + timedelta(days=2, hours=3),
            location="مشهد",
            status=PublishStatus.PUBLISHED,
            published_at=timezone.now(),
        )
        self.draft_event = Event.objects.create(
            title="رویداد پیش‌نویس",
            description="پیش‌نویس",
            start_at=timezone.now() + timedelta(days=5),
            end_at=timezone.now() + timedelta(days=5, hours=2),
            location="مشهد",
            status=PublishStatus.DRAFT,
        )

    def test_index_page_loads(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "دسته‌بندی‌ها")
        self.assertContains(response, reverse("flowers"))

    def test_legacy_section_redirects_to_new_category(self):
        response = self.client.get(reverse("index"), {"section": "bakery"})
        self.assertRedirects(response, reverse("bakery"), fetch_redirect_response=False)

    def test_category_page_contains_lead_form(self):
        response = self.client.get(reverse("flowers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "راهنمایی می‌خواهم")
        self.assertContains(response, reverse("flower_subcategory", args=["bouquet"]))

    def test_subcategory_page_loads(self):
        response = self.client.get(reverse("flower_subcategory", args=["bouquet"]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.flower.name)

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
                "full_name": "کاربر تست",
                "mobile": "09121234567",
                "lead_type": LeadRequest.LeadType.FLOWER,
                "delivery_window": LeadRequest.DeliveryWindow.TODAY,
                "note": "تست",
                "next": reverse("contact"),
                "source_page": "/contact/",
            },
        )
        self.assertRedirects(response, reverse("contact"), fetch_redirect_response=False)
        self.assertEqual(LeadRequest.objects.count(), 1)

    def test_robots_and_sitemap_routes(self):
        self.assertEqual(self.client.get(reverse("robots_txt")).status_code, 200)
        self.assertEqual(self.client.get(reverse("sitemap")).status_code, 200)
