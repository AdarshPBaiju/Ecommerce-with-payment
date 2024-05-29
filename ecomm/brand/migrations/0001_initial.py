# Generated by Django 5.0.3 on 2024-03-14 19:47

from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Brand",
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
                ("brand_name", models.CharField(max_length=50, unique=True)),
                ("slug", models.SlugField(max_length=100, unique=True)),
                (
                    "brand_image",
                    models.ImageField(blank=True, upload_to="photos/brand"),
                ),
            ],
        ),
    ]
