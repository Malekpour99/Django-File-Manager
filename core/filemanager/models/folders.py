from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

from .base import BaseModel


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
            return f"{self.parent_folder.get_nested_path()}/{self.name}"
        return self.name

    class Meta:
        unique_together = ("name", "parent_folder", "owner")
