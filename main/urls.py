from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("flowers/", views.flowers, name="flowers"),
    path("flowers/<slug:subcategory_slug>/", views.flower_subcategory, name="flower_subcategory"),
    path("bakery/", views.bakery, name="bakery"),
    path("gifts/", views.gifts, name="gifts"),
    path("events/", views.events, name="events"),
    path("events/<slug:slug>/", views.event_detail, name="event_detail"),
    path("mashhad/", views.mashhad_hub, name="mashhad_hub"),
    path("mashhad/flower-order/", views.mashhad_flower_order, name="mashhad_flower_order"),
    path("mashhad/flower-delivery/", views.mashhad_flower_delivery, name="mashhad_flower_delivery"),
    path("visit/", views.visit, name="visit"),
    path("contact/", views.contact, name="contact"),
    path("faq/", views.faq, name="faq"),
    path("blog/", views.blog, name="blog"),
    path("blog/<slug:slug>/", views.blog_detail, name="blog_detail"),
    path("lead-request/", views.submit_lead_request, name="lead_request"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("about/", views.about, name="about"),
    # مسیرهای legacy برای حفظ سازگاری
    path("Visit", views.visit, name="Visit"),
    path("product/<int:pk>/<slug:slug>/", views.product_detail, name="product_detail"),
    path("flower/<int:pk>/", views.flower_detail_redirect, name="flower_detail_redirect"),
    path("flower/<int:pk>/<slug:slug>/", views.flower_detail, name="flower_detail"),
    path("occasions/", views.occasions, name="occasions"),
    path("occasions/<slug:slug>/", views.occasion_detail, name="occasion_detail"),
]
