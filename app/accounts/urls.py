from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView
from .views import RegisterView

app_name = "accounts"

urlpatterns = [
    path("login/", LoginView.as_view(redirect_authenticated_user=True), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", RegisterView.as_view(), name="register"),
    path("api/v1/", include("accounts.api.v1.urls")),
]
