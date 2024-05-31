from django.urls import path
from . import views

app_name = "filemanager"

urlpatterns = [
    path("", views.ContentView.as_view(), name="home"),
    path("folder/<str:folder_slug>/", views.ContentView.as_view(), name="folder-content"),
    path("upload/file/", views.FileUploadView.as_view(), name="upload-file"),
    path("create/folder/", views.FolderCreateView.as_view(), name="create-folder"),
    path("file/<int:pk>/edit/", views.FileUpdateView.as_view(), name="update-file"),
    path("file/<int:pk>/delete/", views.FileDeleteView.as_view(), name="delete-file"),
    path("folder/<int:pk>/delete/", views.FolderDeleteView.as_view(), name="delete-folder"),
    path("search/", views.SearchView.as_view(), name="search"),
]
