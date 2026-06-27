import pytest

from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token

from accounts.models import Profile
from ..api.v1.utils import TokenHandler


User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def create_user():
    def _create_user(email, password, is_verified=True):
        user = User.objects.create_user(
            email=email, password=password, is_verified=is_verified
        )
        return user

    return _create_user


@pytest.fixture
def create_profile(create_user):
    def _create_profile(email, password, is_verified=True):
        user = create_user(email, password, is_verified)
        # getting the profile from the tuple (don't need created_status boolean)
        profile = Profile.objects.get_or_create(user=user)[0]
        return profile

    return _create_profile


@pytest.mark.django_db
class TestAccountsAPI:
    """
    Tests for accounts app APIs
    """

    def test_user_registration(self, api_client):
        url = reverse("accounts:registration")
        data = {
            "email": "test@example.com",
            "password": "testpass123",
            "password1": "testpass123",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_201_CREATED
        assert "email" in response.data

    def test_change_password(self, api_client, create_user):
        user = create_user("test@example.com", "oldpassword")
        api_client.force_authenticate(user=user)
        url = reverse("accounts:change-password")
        data = {
            "old_password": "oldpassword",
            "new_password": "newpassword123",
            "new_password1": "newpassword123",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["details"] == "password changed successfully"

    def test_custom_obtain_auth_token(self, api_client, create_user):
        create_user("test@example.com", "password123")
        url = reverse("accounts:token-login")
        data = {"email": "test@example.com", "password": "password123"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert "token" in response.data

    def test_custom_discard_auth_token(self, api_client, create_user):
        user = create_user("test@example.com", "password123")
        Token.objects.create(user=user)
        api_client.force_authenticate(user=user)
        url = reverse("accounts:token-logout")
        response = api_client.post(url, format="json")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_activation_resend(self, api_client, create_user):
        create_user("test@example.com", "password123", is_verified=False)
        url = reverse("accounts:activation-resend")
        data = {"email": "test@example.com"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["details"] == "Activation link resend was successful"

    def test_profile_view(self, api_client, create_profile):
        profile = create_profile("test@example.com", "password123")
        user = profile.user
        api_client.force_authenticate(user=user)
        url = reverse("accounts:profile")
        response = api_client.get(url, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["email"] == user.email

    def test_reset_password(self, api_client, create_user):
        create_user("test@example.com", "password123")
        url = reverse("accounts:reset-password")
        data = {"email": "test@example.com"}
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["details"] == "reset password link was sent to you."

    def test_reset_password_confirm(self, api_client, create_user):
        user = create_user("test@example.com", "password123")
        url = reverse("accounts:reset-password-confirm")
        token = TokenHandler.get_tokens_for_user(user)
        data = {
            "token": token,
            "password": "newpassword123",
            "confirm_password": "newpassword123",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["details"] == "Reset password was successful"
