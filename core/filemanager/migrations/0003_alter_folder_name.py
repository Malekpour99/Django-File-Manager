# Generated by Django 3.2.25 on 2024-05-31 12:57

from django.db import migrations, models
import filemanager.models.folders


class Migration(migrations.Migration):

    dependencies = [
        ("filemanager", "0002_file_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="folder",
            name="name",
            field=models.CharField(
                max_length=255, validators=[filemanager.models.folders.validate_name]
            ),
        ),
    ]
