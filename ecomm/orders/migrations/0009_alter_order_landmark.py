# Generated by Django 5.0.3 on 2024-03-26 06:49

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0008_rename_address_line_2_order_area_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="landmark",
            field=models.CharField(blank=True, max_length=300),
        ),
    ]
