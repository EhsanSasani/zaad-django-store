from datetime import timedelta

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Category,
    Event,
    HomeHeroSlide,
    LeadRequest,
    Product,
    PublishStatus,
    SiteHero,
    Tag,
)


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

        self.birthday_tag = Tag.objects.create(
            name="تولد",
            slug="birthday",
            is_occasion=True,
        )
        self.condolence_tag = Tag.objects.create(
            name="ترحیم",
            slug="condolence",
            is_occasion=True,
        )
        self.flower.tags.add(self.birthday_tag, self.condolence_tag)
        self.bakery.tags.add(self.birthday_tag)
        self.gift_product.tags.add(self.birthday_tag)

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

    def test_home_hero_uses_all_admin_managed_fields(self):
        HomeHeroSlide.objects.create(
            title="Admin Home Hero",
            kicker="ADMIN KICKER",
            description="Admin home description",
            image="heroes/home/desktop.jpg",
            mobile_image="heroes/home/mobile/mobile.jpg",
            primary_button_text="Primary action",
            primary_button_url="/flowers/",
            secondary_button_text="Secondary action",
            secondary_button_url="/contact/",
        )

        response = self.client.get(reverse("index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "/media/heroes/home/desktop.jpg")
        self.assertContains(response, "/media/heroes/home/mobile/mobile.jpg")
        self.assertContains(response, "Admin Home Hero")
        self.assertContains(response, "Admin home description")
        self.assertContains(response, 'href="/flowers/"')
        self.assertContains(response, 'href="/contact/"')

    def test_legacy_section_redirects_to_new_category(self):
        response = self.client.get(reverse("index"), {"section": "bakery"})
        self.assertRedirects(response, reverse("bakery"), fetch_redirect_response=False)

    def test_flowers_landing_page_loads(self):
        response = self.client.get(reverse("flowers"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.flower.product_code)

    def test_collection_landing_uses_page_hero_from_admin(self):
        SiteHero.objects.create(
            title="Admin Flowers Hero",
            kicker="ADMIN FLOWERS",
            description="Admin flowers description",
            image="heroes/pages/flowers.jpg",
            mobile_image="heroes/pages/mobile/flowers.jpg",
            target_page=SiteHero.TargetPage.FLOWERS,
        )

        response = self.client.get(reverse("flowers"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["landing_hero_title"], "Admin Flowers Hero")
        self.assertEqual(response.context["landing_hero_eyebrow"], "ADMIN FLOWERS")
        self.assertEqual(
            response.context["landing_hero_mobile_image"],
            "/media/heroes/pages/mobile/flowers.jpg",
        )
        self.assertContains(response, "Admin flowers description")
        self.assertContains(response, "/media/heroes/pages/flowers.jpg")
        self.assertContains(response, "/media/heroes/pages/mobile/flowers.jpg")

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

    def test_occasion_tags_share_art_direction_but_keep_distinct_copy(self):
        birthday = self.client.get(reverse("occasion_detail", args=["birthday"]))
        condolence = self.client.get(reverse("occasion_detail", args=["condolence"]))
        flower_birthday = self.client.get(reverse("flower_occasion", args=["birthday"]))

        for response in (birthday, condolence, flower_birthday):
            with self.subTest(path=response.request["PATH_INFO"]):
                self.assertEqual(response.status_code, 200)
                self.assertEqual(
                    response.context["page_hero_image"],
                    "main/img/occasion-detail-hero-v1.webp",
                )
                self.assertEqual(
                    response.context["page_hero_mobile_image"],
                    "main/img/occasion-detail-hero-mobile-v1.webp",
                )
                self.assertContains(response, 'class="page-hero__content container"')
                self.assertContains(response, 'media="(max-width: 760px)"')

        self.assertContains(birthday, "برای لحظه‌ای که باید با گل، رنگ و یک یاد شیرین ماندگار شود.")
        self.assertContains(condolence, "برای ابراز همدلی؛ باوقار، آرام و محترمانه.")
        self.assertNotEqual(
            birthday.context["page_hero_text"],
            condolence.context["page_hero_text"],
        )

    def test_occasion_detail_always_exposes_available_product_filters(self):
        response = self.client.get(reverse("occasion_detail", args=["birthday"]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            [item["label"] for item in response.context["filter_links"]],
            ["All", "Daily Bakery", "Bouquet", "Gift Box"],
        )
        self.assertContains(response, "?category=bouquet&amp;section=flowers")

        filtered = self.client.get(
            reverse("occasion_detail", args=["birthday"]),
            {"category": "bouquet", "section": "flowers"},
        )

        self.assertEqual(filtered.status_code, 200)
        self.assertEqual(filtered.context["products"], [self.flower])
        self.assertTrue(
            next(
                item
                for item in filtered.context["filter_links"]
                if item["label"] == "Bouquet"
            )["is_active"]
        )

    def test_events_page_shows_only_published(self):
        response = self.client.get(reverse("events"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.published_event.title)
        self.assertNotContains(response, self.draft_event.title)

    def test_events_page_uses_page_hero_from_admin(self):
        SiteHero.objects.create(
            title="Admin Events Hero",
            kicker="ADMIN EVENTS",
            description="Admin events description",
            image="heroes/pages/events.jpg",
            mobile_image="heroes/pages/mobile/events.jpg",
            target_page=SiteHero.TargetPage.EVENTS,
        )

        response = self.client.get(reverse("events"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Admin Events Hero")
        self.assertContains(response, "ADMIN EVENTS")
        self.assertContains(response, "Admin events description")
        self.assertContains(response, "/media/heroes/pages/events.jpg")
        self.assertContains(response, "/media/heroes/pages/mobile/events.jpg")

    def test_visit_urls_redirect_to_contact(self):
        contact_url = reverse("contact")

        for visit_url in ("/visit/", "/Visit"):
            with self.subTest(visit_url=visit_url):
                response = self.client.get(visit_url)
                self.assertRedirects(
                    response,
                    contact_url,
                    status_code=301,
                    fetch_redirect_response=False,
                )

    def test_contact_and_faq_pages_load(self):
        self.assertEqual(self.client.get(reverse("contact")).status_code, 200)
        self.assertEqual(self.client.get(reverse("faq")).status_code, 200)

    def test_about_page_uses_the_scoped_editorial_redesign(self):
        response = self.client.get(reverse("about"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'class="about-page"')
        self.assertContains(response, "main/css/about.css")
        self.assertNotContains(response, '<section class="page-hero">')

        for image_name in (
            "zad-store-v1.webp",
            "zad-store-flowers-v1.webp",
            "zad-floral-wall-v1.webp",
            "zad-sweetbar-v1.webp",
            "zad-workshop-making-v1.webp",
            "zad-workshop-talk-v1.webp",
            "zad-workshop-space-v1.webp",
        ):
            with self.subTest(image_name=image_name):
                self.assertContains(response, image_name)

    def test_standard_page_hero_uses_admin_mobile_image(self):
        SiteHero.objects.create(
            title="Admin Contact Hero",
            image="heroes/pages/contact.jpg",
            mobile_image="heroes/pages/mobile/contact.jpg",
            target_page=SiteHero.TargetPage.CONTACT,
        )

        response = self.client.get(reverse("contact"))

        self.assertEqual(
            response.context["page_hero_mobile_image"],
            "/media/heroes/pages/mobile/contact.jpg",
        )
        self.assertContains(response, "/media/heroes/pages/mobile/contact.jpg")

    def test_about_page_is_available_as_a_site_hero_target(self):
        self.assertIn(
            (SiteHero.TargetPage.ABOUT, "درباره زاد"),
            SiteHero.TargetPage.choices,
        )

        SiteHero.objects.create(
            title="Admin About Hero",
            image="heroes/pages/about.jpg",
            target_page=SiteHero.TargetPage.ABOUT,
        )

        response = self.client.get(reverse("about"))

        self.assertEqual(response.context["page_hero_title"], "Admin About Hero")
        self.assertEqual(response.context["about_hero_title"], "Admin About Hero")
        self.assertContains(response, "/media/heroes/pages/about.jpg")

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


class AdminSmokeTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_superuser(
            username="admin-smoke-test",
            email="admin-smoke@example.invalid",
            password="test-password",
        )
        self.client.force_login(self.user)

    def test_every_registered_admin_list_and_add_page_loads(self):
        for model in admin.site._registry:
            model_meta = model._meta
            route_prefix = f"admin:{model_meta.app_label}_{model_meta.model_name}"

            for route_suffix in ("changelist", "add"):
                with self.subTest(model=model_meta.label, page=route_suffix):
                    response = self.client.get(
                        reverse(f"{route_prefix}_{route_suffix}")
                    )
                    self.assertEqual(response.status_code, 200)

    def test_site_hero_can_be_edited_through_admin(self):
        hero = SiteHero.objects.create(
            title="Before edit",
            image="heroes/pages/edit-test.jpg",
            target_page=SiteHero.TargetPage.CONTACT,
        )
        change_url = reverse("admin:main_sitehero_change", args=[hero.pk])

        self.assertEqual(self.client.get(change_url).status_code, 200)

        response = self.client.post(
            change_url,
            {
                "title": "After edit",
                "kicker": "",
                "description": "",
                "target_page": SiteHero.TargetPage.CONTACT,
                "target_slug": "",
                "is_active": "on",
                "sort_order": "0",
                "_save": "Save",
            },
        )

        self.assertEqual(response.status_code, 302)
        hero.refresh_from_db()
        self.assertEqual(hero.title, "After edit")
