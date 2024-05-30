from django.urls import path
from . import views

app_name = "filemanager"

urlpatterns = [
    path("", views.ContentView.as_view(), name="home"),
    path("<str:folder_slug>/", views.ContentView.as_view(), name="folder-content"),
    path("file/upload/", views.FileUploadView.as_view(), name="upload-file"),
    path("file/<int:pk>/delete/", views.FileDeleteView.as_view(), name="delete-file"),
    path("folder/<int:pk>/delete/", views.FolderDeleteView.as_view(), name="delete-folder"),
]
