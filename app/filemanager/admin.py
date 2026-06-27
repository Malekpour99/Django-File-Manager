from django.contrib import admin
from .models import File, Folder


@admin.register(File)
class FileAdmin(admin.ModelAdmin):
    # Activates post filtering by date hierarchy
    date_hierarchy = "created_at"
    empty_value_display = "-NONE-"
    list_display = (
        "name",
        "owner",
        "folder",
        "formatted_size",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    search_fields = ["name"]


@admin.register(Folder)
class CommentAdmin(admin.ModelAdmin):
    date_hierarchy = "created_at"
    empty_value_display = "-empty-"
    list_display = (
        "name",
        "owner",
        "parent_folder",
        "created_at",
        "updated_at",
    )
    list_filter = ("parent_folder", "created_at", "updated_at")
    search_fields = ["name", "parent_folder"]
