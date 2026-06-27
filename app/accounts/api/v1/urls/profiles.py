from django.urls import path
from .. import views

urlpatterns = [
    path("", views.ProfileAPIView.as_view(), name="profile"),
]
