import os

from django.core.management.base import BaseCommand

from payments.models import Product


class Command(BaseCommand):
    help = "Create or update the single demo product."

    def handle(self, *args, **options):
        product, _ = Product.objects.update_or_create(
            id=1,
            defaults={
                "name": os.getenv("DEMO_PRODUCT_NAME", "Dodo Demo Product"),
                "description": "A single item for demonstrating Dodo hosted checkout.",
                "price_display": os.getenv("DEMO_PRODUCT_PRICE", "$19.00"),
                "dodo_product_id": os.getenv("DODO_DEMO_PRODUCT_ID", "replace_with_dodo_product_id"),
                "is_active": True,
            },
        )
        self.stdout.write(self.style.SUCCESS(f"Ready: {product.name} ({product.dodo_product_id})"))
