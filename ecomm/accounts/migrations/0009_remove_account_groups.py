# Generated by Django 5.0.3 on 2024-03-23 09:36

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0008_remove_account_is_superuser_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="account",
            name="groups",
        ),
    ]
