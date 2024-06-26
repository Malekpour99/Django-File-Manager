from django.db import models
from django.conf import settings
from django.forms import ValidationError
from django.dispatch import receiver
from django.db.models.signals import post_delete
from django.utils.translation import gettext_lazy as _

import os
import logging
import mimetypes
from PIL import Image
from moviepy.video.io.VideoFileClip import VideoFileClip

from .base import BaseModel
from .folders import Folder

# Default Thumbnail for video files
DEFAULT_THUMBNAIL_PATH = os.path.join(
    settings.BASE_DIR, "static/img/default-video-thumbnail.png"
)

#
FILE_TYPE_CHOICES = [
    ("video", "Video"),
    ("image", "Image"),
]

# logger object
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
            _("Unsupported file type. Only videos and images are supported.")
        )
    if mime_type and mime_type.startswith("image"):
        try:
            # Verify uploaded file is an image
            image = Image.open(value)
            image.verify()
        except Exception:
            raise ValidationError(
                _("Unsupported file type. Your file is not a valid image.")
            )
    if mime_type and mime_type.startswith("video"):
        try:
            # Verify uploaded file is a video
            clip = VideoFileClip(value.temporary_file_path())
            clip.reader.close()  # Close the reader
        except Exception:
            raise ValidationError(
                _("Unsupported file type. Your file is not a valid video.")
            )


# File size custom validator
def validate_file_size(value):
    max_size_mb = 7
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(
            _("File size exceeds the maximum limit of %(max_size_mb)d MB"),
            params={"max_size_mb": max_size_mb},
        )


# Model
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
        super().save(*args, **kwargs)
        if not self.thumbnail:
            self.create_thumbnail()

    def choose_file_type(self):
        mime_type, _ = mimetypes.guess_type(self.file.name)
        if mime_type.startswith("image"):
            return "image"
        elif mime_type.startswith("video"):
            return "video"

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
        thumbnail_folder = "media/thumbnails"
        os.makedirs(thumbnail_folder, exist_ok=True)
        thumbnail_dir = "thumbnails"
        thumbnail_filename = os.path.basename(self.file.name)
        thumbnail_path = os.path.join(thumbnail_dir, thumbnail_filename)
        thumbnail_full_path = os.path.join("media/", thumbnail_path)
        image.save(thumbnail_full_path)
        self.thumbnail = thumbnail_path
        self.save()

    def create_video_thumbnail(self):
        thumbnail_size = (100, 100)
        thumbnail_folder = "media/thumbnails"
        os.makedirs(thumbnail_folder, exist_ok=True)
        thumbnail_dir = "thumbnails"
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
            self.thumbnail = DEFAULT_THUMBNAIL_PATH
            self.save()

    class Meta:
        unique_together = ("name", "folder", "owner")


@receiver(post_delete, sender=File)
def delete_file_on_model_delete(sender, instance, **kwargs):
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
    if instance.thumbnail:
        if os.path.isfile(instance.thumbnail.path):
            os.remove(instance.thumbnail.path)
