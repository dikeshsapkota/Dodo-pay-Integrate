from django.db import models


class Product(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    price_display = models.CharField(max_length=40, help_text="Demo label, e.g. $19.00")
    dodo_product_id = models.CharField(max_length=120)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Order(models.Model):
    class Status(models.TextChoices):
        CREATED = "created", "Created"
        CHECKOUT_CREATED = "checkout_created", "Checkout created"
        PAID = "paid", "Paid"
        FAILED = "failed", "Failed"
        CANCELLED = "cancelled", "Cancelled"

    product = models.ForeignKey(Product, on_delete=models.PROTECT, related_name="orders")
    customer_name = models.CharField(max_length=120)
    customer_email = models.EmailField()
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.CREATED)
    checkout_session_id = models.CharField(max_length=160, blank=True)
    checkout_url = models.URLField(blank=True, max_length=500)
    provider_payment_id = models.CharField(max_length=160, blank=True)
    provider_payload = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order #{self.pk} - {self.status}"
