from django.db import migrations, models
import django.db.models.deletion


def create_demo_product(apps, schema_editor):
    Product = apps.get_model("payments", "Product")
    Product.objects.create(
        name="Dodo Demo Product",
        description="A single checkout item used to demonstrate the hosted Dodo Payments flow.",
        price_display="$19.00",
        dodo_product_id="replace_with_dodo_product_id",
    )


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("description", models.TextField(blank=True)),
                ("price_display", models.CharField(help_text="Demo label, e.g. $19.00", max_length=40)),
                ("dodo_product_id", models.CharField(max_length=120)),
                ("is_active", models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("customer_name", models.CharField(max_length=120)),
                ("customer_email", models.EmailField(max_length=254)),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("created", "Created"),
                            ("checkout_created", "Checkout created"),
                            ("paid", "Paid"),
                            ("failed", "Failed"),
                            ("cancelled", "Cancelled"),
                        ],
                        default="created",
                        max_length=32,
                    ),
                ),
                ("checkout_session_id", models.CharField(blank=True, max_length=160)),
                ("checkout_url", models.URLField(blank=True, max_length=500)),
                ("provider_payment_id", models.CharField(blank=True, max_length=160)),
                ("provider_payload", models.JSONField(blank=True, default=dict)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="orders",
                        to="payments.product",
                    ),
                ),
            ],
        ),
        migrations.RunPython(create_demo_product, migrations.RunPython.noop),
    ]
