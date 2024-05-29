# Generated by Django 3.2.25 on 2024-05-29 05:15

from django.db import migrations, models
import django.db.models.deletion
import filemanager.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='folders', to='accounts.profile')),
                ('parent_folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subfolders', to='filemanager.folder')),
            ],
            options={
                'unique_together': {('name', 'parent_folder', 'owner')},
            },
        ),
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('name', models.CharField(max_length=255)),
                ('file', models.FileField(upload_to='uploads/', validators=[filemanager.models.validate_file_type, filemanager.models.validate_file_size])),
                ('size', models.PositiveIntegerField()),
                ('thumbnail', models.ImageField(blank=True, null=True, upload_to='thumbnails/')),
                ('folder', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='files', to='filemanager.folder')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='files', to='accounts.profile')),
            ],
            options={
                'unique_together': {('name', 'folder', 'owner')},
            },
        ),
    ]