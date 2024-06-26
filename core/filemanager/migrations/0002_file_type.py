# Generated by Django 3.2.25 on 2024-05-30 07:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("filemanager", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="file",
            name="type",
            field=models.CharField(
                choices=[("video", "Video"), ("image", "Image")],
                default="image",
                max_length=10,
            ),
            preserve_default=False,
        ),
    ]
