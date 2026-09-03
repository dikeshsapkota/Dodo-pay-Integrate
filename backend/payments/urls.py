from django.urls import path

from . import views

urlpatterns = [
    path("products/", views.product_list),
    path("checkout/", views.create_checkout),
    path("orders/<int:order_id>/", views.order_detail),
    path("webhooks/dodo/", views.dodo_webhook),
]
