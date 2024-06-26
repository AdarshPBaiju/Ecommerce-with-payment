# Generated by Django 5.0.4 on 2024-04-26 03:09

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("carts", "0003_cartitem_user_alter_cartitem_cart"),
    ]

    operations = [
        migrations.CreateModel(
            name="Coupon",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("code", models.CharField(max_length=20, unique=True)),
                (
                    "discount_type",
                    models.CharField(
                        choices=[
                            ("flat", "Flat Discount"),
                            ("percentage", "Percentage Discount"),
                        ],
                        max_length=10,
                    ),
                ),
                (
                    "discount_amount",
                    models.DecimalField(decimal_places=2, max_digits=10),
                ),
                ("maximum_uses", models.PositiveIntegerField()),
                ("current_uses", models.PositiveIntegerField(default=0)),
                (
                    "expire_date",
                    models.DateTimeField(default=django.utils.timezone.now),
                ),
            ],
        ),
        migrations.AddField(
            model_name="cart",
            name="applied_coupon",
            field=models.CharField(blank=True, max_length=250),
        ),
    ]
