# Generated by Django 5.0.3 on 2024-03-17 08:07

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("orders", "0001_initial"),
    ]

    operations = [
        migrations.RenameField(
            model_name="order",
            old_name="order_nate",
            new_name="order_note",
        ),
    ]
