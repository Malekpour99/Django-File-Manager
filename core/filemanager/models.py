from django.db import models
from django.forms import ValidationError
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

import os
import logging
import mimetypes
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip


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
        "video/wmv",
        "video/mov",
        "video/avi",
        "video/mpeg",
        "video/quicktime",
        "video/x-msvideo",
        "video/x-ms-wmv",
    ]
    mime_type, encoding = mimetypes.guess_type(value.name)
    if mime_type not in valid_mime_types or mime_type is None:
        raise ValidationError(
            _("Unsupported file type. Allowed types are: %(valid_mime_types)s"),
            params={"valid_mime_types": ", ".join(valid_mime_types)},
        )


# File size custom validator
def validate_file_size(value):
    max_size_mb = 7
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _("File size exceeds the maximum limit of %(max_size_mb)d MB"),
            params={"max_size_mb": max_size_mb},
        )


# Abstract Base Model
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


# Models
class Folder(BaseModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
            # Ensure the slug is unique within the same parent folder
            while Folder.objects.filter(
                slug=self.slug, parent_folder=self.parent_folder
            ).exists():
                self.slug = f"{self.slug}-{self.id}"
        super().save(*args, **kwargs)

    def get_nested_path(self):
        if self.parent_folder:
            return f"{self.parent_folder.get_nested_path()}/{self.slug}"
        return self.slug

    class Meta:
        unique_together = ("name", "parent_folder", "owner")


class File(BaseModel):
    name = models.CharField(max_length=255, blank=True)
    file = models.FileField(
        upload_to="uploads/", validators=[validate_file_type, validate_file_size]
    )
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
        image.thumbnail(thumbnail_size, Image.LANCZOS)
        thumbnail_dir = "thumbnails"
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_filename = os.path.basename(self.file.name)
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        thumbnail_full_path = os.path.join("media/", thumbnail_path)
        image.save(thumbnail_full_path)
        self.thumbnail = thumbnail_path
        self.save()

    def create_video_thumbnail(self):
        thumbnail_size = (100, 100)
        thumbnail_dir = "thumbnails"
        os.makedirs(thumbnail_dir, exist_ok=True)
        thumbnail_filename = os.path.basename(self.file.name)
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename + ".jpg")
        thumbnail_full_path = os.path.join("media/", thumbnail_path)
        file_path = self.file.path
        try:
            clip = VideoFileClip(file_path)
            frame = clip.get_frame(1)  # Capture frame at 1 second
            clip.close()

            thumbnail = Image.fromarray(frame)
            thumbnail.thumbnail(thumbnail_size)

            thumbnail.save(thumbnail_full_path)

            self.thumbnail = thumbnail_path
            self.save()
        except Exception as error:
            logger.error(
                f"Failed to create thumbnail for video {self.file.name}: {error}"
            )
            default_thumbnail_path = "path/to/default/thumbnail.jpg"
            self.thumbnail = default_thumbnail_path
            self.save()

    class Meta:
        unique_together = ("name", "folder", "owner")
