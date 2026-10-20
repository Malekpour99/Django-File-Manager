import logging
import os
from typing import Optional

from django.db import models
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.forms import ValidationError
from django.dispatch import receiver
from django.db.models.fields.files import FieldFile
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _

from filemanager.services import (
    InvalidMediaError,
    prepare_media,
)

from .base import BaseModel
from .folder import Folder

# Default Thumbnail for video files
DEFAULT_THUMBNAIL_PATH = "static/img/default-video-thumbnail.png"

FILE_TYPE_CHOICES = [
    ("video", "Video"),
    ("image", "Image"),
]

logger = logging.getLogger(__name__)


# File type custom validator
def validate_file_type(value):
    # Reject oversized uploads before invoking image or video decoders.
    validate_file_size(value)
    try:
        prepare_media(value)
    except InvalidMediaError as error:
        raise ValidationError(str(error)) from error


# File size custom validator
def validate_file_size(value):
    max_size_mb = 7
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _("File size exceeds the maximum limit of %(max_size_mb)d MB"),
            params={"max_size_mb": max_size_mb},
        )


class File(BaseModel):
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField(
        upload_to="uploads/", validators=[validate_file_type, validate_file_size]
    )
    type = models.CharField(max_length=10, choices=FILE_TYPE_CHOICES)
    size = models.PositiveIntegerField(blank=True)
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name="files", null=True, blank=True
    )
    owner = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="files"
    )

    @property
    def formatted_size(self):
        """
        Returns the file size in human-readable format.
        """
        size = self.size
        if size < 1024:
            return "%d B" % size
        elif size < 1024 * 1024:
            return "%.1f KB" % (size / 1024)
        else:
            return "%.1f MB" % (size / (1024 * 1024))

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.file.name)
        if not self.size:
            self.size = self.file.size
        if not self.type:
            self.type = self.choose_file_type()
        if not self.thumbnail:
            self.create_thumbnail(save=False)
        super().save(*args, **kwargs)

    def get_thumbnail_name(self, original_filename, force_jpg=False):
        """
        Generate thumbnail name based on original filename

        Args:
            original_filename (str): Original file name
            force_jpg (bool): Force .jpg extension for non-image files
        """
        base_name = os.path.basename(original_filename)
        if force_jpg:
            base_name = os.path.splitext(base_name)[0] + ".jpg"
        return base_name

    def choose_file_type(self):
        try:
            return prepare_media(self.file)[0]
        except InvalidMediaError as error:
            raise ValidationError(str(error)) from error

    def create_thumbnail(self, *, save=True):
        kind = self.type or self.choose_file_type()
        if kind == "image":
            self.create_image_thumbnail(save=save)
        elif kind == "video":
            self.create_video_thumbnail(save=save)

    def create_image_thumbnail(self, *, save=True):
        self.thumbnail.save(
            self.get_thumbnail_name(self.file.name, force_jpg=True),
            ContentFile(prepare_media(self.file)[1]),
            save=False,
        )
        if save:
            self.save()

    def create_video_thumbnail(self, *, save=True):
        try:
            content = prepare_media(self.file)[1]
        except InvalidMediaError:
            logger.exception("Failed to create video thumbnail for %s", self.file.name)
            self.thumbnail = DEFAULT_THUMBNAIL_PATH
        else:
            self.thumbnail.save(
                self.get_thumbnail_name(self.file.name, force_jpg=True),
                ContentFile(content),
                save=False,
            )
        if save:
            self.save()

    class Meta:
        unique_together = ("name", "folder", "owner")


@receiver(post_delete, sender=File)
def delete_file_on_model_delete(sender, instance, **kwargs):
    delete_file_from_storage(
        file_field=instance.file
    )  # Get the relative path of the file
    delete_file_from_storage(
        file_field=instance.thumbnail
    )  # Delete thumbnail if it exists


def delete_file_from_storage(*, file_field: Optional[FieldFile]):
    if file_field:
        file_path = file_field.name
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
