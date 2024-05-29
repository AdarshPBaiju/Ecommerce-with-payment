# Generated by Django 5.0.3 on 2024-03-31 07:35

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0015_alter_account_phone_number"),
    ]

    operations = [
        migrations.CreateModel(
            name="LoggedInDevices",
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
                ("device_name", models.CharField(max_length=300)),
                ("session_id", models.CharField(max_length=300, unique=True)),
                ("last_login", models.DateTimeField(auto_now=True)),
                (
                    "account",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
