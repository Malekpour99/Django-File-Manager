from django.db import models
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

import os
import logging
import mimetypes
import subprocess
from PIL import Image


# logging Configuration
logger = logging.getLogger(__name__)


# File type custom validator
def validate_file_type(value):
    valid_mime_types = [
        "image/jpeg",
        "image/jpg",
        "image/png",
        "image/gif",
        "image/bmp",
        "image/tiff",
        "video/mp4",
        "video/mkv",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-ms-wmv",
    ]
    mime_type, _ = mimetypes.guess_type(value.name)
    if mime_type not in valid_mime_types:
        raise ValidationError(
            _("Unsupported file type. Allowed types are: %(valid_mime_types)s"),
            params={"valid_mime_types": ", ".join(valid_mime_types)},
        )


# File size custom validator
def validate_file_size(value):
    max_file_size = 7 * 1024 * 1024  # 7 MB
    if value.size > max_file_size:
        raise ValidationError(_("File size exceeds the maximum limit of 10 MB"))


# Abstract Base Model
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Models
class Folder(BaseModel):
    name = models.CharField(max_length=255)
    owner = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="folders"
    )
    parent_folder = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="subfolders",
    )

    def __str__(self):
        return self.name

    class Meta:
        unique_together = ("name", "parent_folder", "owner")


class File(BaseModel):
    name = models.CharField(max_length=255)
    file = models.FileField(
        upload_to="uploads/", validators=[validate_file_type, validate_file_size]
    )
    size = models.PositiveIntegerField()
    thumbnail = models.ImageField(upload_to="thumbnails/", null=True, blank=True)
    folder = models.ForeignKey(
        Folder, on_delete=models.CASCADE, related_name="files", null=True, blank=True
    )
    owner = models.ForeignKey(
        "accounts.Profile", on_delete=models.CASCADE, related_name="files"
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = os.path.basename(self.file.name)
        if not self.size:
            self.size = self.file.size
        super().save(*args, **kwargs)
        if not self.thumbnail:
            self.create_thumbnail()

    def create_thumbnail(self):
        mime_type, _ = mimetypes.guess_type(self.file.name)
        if mime_type and mime_type.startswith("image"):
            self.create_image_thumbnail()
        elif mime_type and mime_type.startswith("video"):
            self.create_video_thumbnail()

    def create_image_thumbnail(self):
        thumbnail_size = (100, 100)
        image = Image.open(self.file)
        image.thumbnail(thumbnail_size, Image.ANTIALIAS)
        thumbnail_path = os.path.join("thumbnails", os.path.basename(self.file.name))
        image.save(thumbnail_path)
        self.thumbnail = thumbnail_path
        self.save()

    def create_video_thumbnail(self):
        thumbnail_size = "100x100"
        thumbnail_path = os.path.join(
            "thumbnails", os.path.basename(self.file.name) + ".jpg"
        )
        file_path = self.file.path
        command = [
            "ffmpeg",
            "-i",
            file_path,
            "-ss",
            "00:00:01.000",
            "-vframes",
            "1",
            "-s",
            thumbnail_size,
            thumbnail_path,
        ]
        try:
            subprocess.run(command, check=True)
            self.thumbnail = thumbnail_path
            self.save()
        except subprocess.CalledProcessError as error:
            logger.error(
                f"Failed to create thumbnail for video {self.file.name}: {error}"
            )
            default_thumbnail_path = "path/to/default/thumbnail.jpg"
            self.thumbnail = default_thumbnail_path
            self.save()

    class Meta:
        unique_together = ("name", "folder", "owner")
