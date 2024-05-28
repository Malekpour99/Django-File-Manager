from django.urls import path
from .. import views
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

urlpatterns = [
    # Registration ---------------------------------------------------
    path("registration/", views.UserRegistration.as_view(), name="registration"),
    # Password ---------------------------------------------------
    path(
        "change-password/",
        views.ChangePasswordAPIView.as_view(),
        name="change-password",
    ),
    path(
        "reset-password/",
        views.ResetPasswordAPIView.as_view(),
        name="reset-password",
    ),
    path(
        "reset-password/validate/<str:token>",
        views.ResetPasswordValidateAPIView.as_view(),
        name="reset-password-validate",
    ),
    path(
        "reset-password/confirm/",
        views.ResetPasswordConfirmAPIView.as_view(),
        name="reset-password-confirm",
    ),
    # Token ---------------------------------------------------
    path("token/login/", views.CustomObtainAuthToken.as_view(), name="token-login"),
    path("token/logout/", views.CustomDiscardAuthToken.as_view(), name="token-logout"),
    # JWT ---------------------------------------------------
    path("jwt/create/", views.CustomTokenObtainPairView.as_view(), name="jwt-create"),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="jwt-verify"),
    # Activation ---------------------------------------------------
    path(
        "activation/confirm/<str:token>",
        views.ActivationAPIView.as_view(),
        name="activation",
    ),
    path(
        "activation/resend/",
        views.ActivationResendAPIView.as_view(),
        name="activation-resend",
    ),
]
