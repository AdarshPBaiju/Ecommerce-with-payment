# Generated by Django 5.0.3 on 2024-03-17 07:33

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0002_product_video_thumbnail_alter_product_video_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="variation",
            name="variation_category",
            field=models.CharField(
                choices=[("color", "color"), ("size", "size")], max_length=100
            ),
        ),
    ]
