from django.urls import path
from . import views

app_name = "filemanager"

urlpatterns = [
    path("", views.ContentView.as_view(), name="home"),
    path("file/upload/", views.FileUploadView.as_view(), name="upload-file"),
    path("file/<int:pk>/delete/", views.FileDeleteView.as_view(), name="delete-file"),
]
