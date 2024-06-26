# Generated by Django 5.0.3 on 2024-03-26 06:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0011_remove_account_groups"),
    ]

    operations = [
        migrations.RenameField(
            model_name="userprofile",
            old_name="address_line_1",
            new_name="area",
        ),
        migrations.RenameField(
            model_name="userprofile",
            old_name="address_line_2",
            new_name="house_no",
        ),
        migrations.AddField(
            model_name="userprofile",
            name="landmark",
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
