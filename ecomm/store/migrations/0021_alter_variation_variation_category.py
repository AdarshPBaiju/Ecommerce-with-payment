# Generated by Django 5.0.3 on 2024-03-26 08:39

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("store", "0020_alter_variation_variation_category"),
    ]

    operations = [
        migrations.AlterField(
            model_name="variation",
            name="variation_category",
            field=models.CharField(
                choices=[("size", "size"), ("color", "color")], max_length=100
            ),
        ),
    ]
