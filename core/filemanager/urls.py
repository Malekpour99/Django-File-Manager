from django.urls import path
from . import views

app_name = "filemanager"

urlpatterns = [
    path("", views.FileListView.as_view(), name="home"),
    path("file/upload/", views.FileUploadView.as_view(), name="upload-file"),
]
