from rest_framework import serializers

from .models import Order, Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ("id", "name", "description", "price_display")


class CheckoutSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    customer_name = serializers.CharField(max_length=120)
    customer_email = serializers.EmailField()


class OrderSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "product",
            "customer_name",
            "customer_email",
            "status",
            "checkout_session_id",
            "checkout_url",
            "created_at",
            "updated_at",
        )
