# Generated by Django 5.0.3 on 2024-03-31 07:50

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0017_rename_loggedindevices_loggedindevice"),
    ]

    operations = [
        migrations.DeleteModel(
            name="LoggedInDevice",
        ),
    ]
