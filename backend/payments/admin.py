from django.contrib import admin

from .models import Order, Product


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "dodo_product_id", "price_display", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "dodo_product_id")


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "product", "customer_email", "status", "checkout_session_id", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("customer_email", "checkout_session_id", "provider_payment_id")
