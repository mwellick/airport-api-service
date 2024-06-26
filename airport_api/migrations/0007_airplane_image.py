# Generated by Django 5.0.6 on 2024-05-16 15:08

import airport_api.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("airport_api", "0006_alter_ticket_options_alter_airplane_name_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="airplane",
            name="image",
            field=models.ImageField(
                null=True, upload_to=airport_api.models.airplane_image_path
            ),
        ),
    ]
