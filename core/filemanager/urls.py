from django.urls import path
from . import views

urlpatterns = [
    path("", views.FileListView.as_view(), name="home"),
]
