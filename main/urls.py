from django.urls import path

from . import views

urlpatterns = [
    # Home
    path("", views.index, name="index"),

    # Flowers
    path("flowers/", views.flowers, name="flowers"),
    path("flowers/all/", views.flowers_all, name="flowers_all"),
    path("flowers/same-day/", views.flowers_same_day, name="flowers_same_day"),
    path("flowers/occasion/<slug:slug>/", views.flower_occasion, name="flower_occasion"),
    path("flowers/<slug:subcategory_slug>/", views.flower_subcategory, name="flower_subcategory"),

    # Bakery
    path("bakery/", views.bakery, name="bakery"),
    path("bakery/all/", views.bakery_all, name="bakery_all"),
    path("bakery/<slug:subcategory_slug>/", views.bakery_subcategory, name="bakery_subcategory"),

    # Gifts
    path("gifts/", views.gifts, name="gifts"),
    path("gifts/all/", views.gifts_all, name="gifts_all"),
    path("gifts/<slug:subcategory_slug>/", views.gift_subcategory, name="gift_subcategory"),

    # Events
    path("events/", views.events, name="events"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),

    # Mashhad landing pages
    path("mashhad/", views.mashhad_hub, name="mashhad_hub"),
    path("mashhad/flower-order/", views.mashhad_flower_order, name="mashhad_flower_order"),
    path("mashhad/flower-delivery/", views.mashhad_flower_delivery, name="mashhad_flower_delivery"),

    # Static pages
    path("visit/", views.visit, name="visit"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("about/", views.about, name="about"),

    # Blog
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),

    # Forms / utility
    path("lead-request/", views.submit_lead_request, name="lead_request"),
    path("robots.txt", views.robots_txt, name="robots_txt"),

    # Product legacy/detail routes
    path("product/<int:pk>/<str:slug>/", views.product_detail, name="product_detail"),
    path("flower/<int:pk>/", views.flower_detail_redirect, name="flower_detail_redirect"),
    path("flower/<int:pk>/<str:slug>/", views.flower_detail, name="flower_detail"),

    # Occasions
    path("occasions/", views.occasions, name="occasions"),
    path("occasions/<slug:slug>/", views.occasion_detail, name="occasion_detail"),

    # Legacy
    path("Visit", views.visit, name="Visit"),
]