import pytest

from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.utils.http import url_has_allowed_host_and_scheme

User = get_user_model()


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def create_user():
    def _create_user(email, password, is_verified=True):
        user = User.objects.create_user(
            email=email, password=password, is_verified=is_verified
        )
        return user

    return _create_user


@pytest.mark.django_db
class TestAccountsViews:
    """
    Tests for accounts app views
    """

    def test_user_registration(self, client):
        url = reverse("accounts:register")
        data = {
            "email": "test@example.com",
            "password1": "testpass123",
            "password2": "testpass123",
        }
        response = client.post(url, data, format="json")
        assert response.status_code == 302  # Redirect after successful registration

        user = User.objects.get(email="test@example.com")
        assert user is not None
        assert user.email == "test@example.com"

    def test_registration_redirect_for_authenticated_user(self, client, create_user):
        user = create_user("test@example.com", "password123")
        client.force_login(user=user)
        url = reverse("accounts:register")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to success_url
        assert url_has_allowed_host_and_scheme(
            response.url, None
        )  # Redirected to success_url

    def test_login(self, client, create_user):
        user = create_user("test@example.com", "password123")
        url = reverse("accounts:login")
        data = {
            "username": user.email,
            "password": "password123",
        }
        response = client.post(url, data, format="json")
        assert response.status_code == 302  # Redirect after successful login

        authenticated_user = authenticate(
            email="test@example.com", password="password123"
        )
        assert authenticated_user is not None
        assert authenticated_user.is_authenticated

    def test_authenticated_user_redirect_for_login(self, client, create_user):
        user = create_user("test@example.com", "password123")
        client.force_login(user=user)
        url = reverse("accounts:login")
        response = client.get(url)
        assert response.status_code == 302  # Redirect to success_url

    def test_logout(self, client, create_user):
        user = create_user("test@example.com", "password123")
        client.force_login(user=user)
        url = reverse("accounts:logout")
        response = client.get(url)
        # After a successful logout we don't redirect; we inform the user
        assert response.status_code == 200
        # Check if the user is actually logged out by verifying no user is authenticated
        response = client.get(reverse("accounts:login"))
        assert response.status_code == 200  # The login page should be accessible
