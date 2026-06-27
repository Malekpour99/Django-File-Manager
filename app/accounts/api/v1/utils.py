from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

import jwt

from mail_templated import EmailMessage

from ..utils import EmailThread


class TokenHandler:
    """Handling token related processes"""

    @staticmethod
    def get_tokens_for_user(user):
        """
        Return an access token (JWT) based on the user

        Args:
            user: User model object

        Returns:
            str: JWT Access token
        """
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)

    @staticmethod
    def Validate_jwt_access_token(token):
        """
        Validates JWT access token

        Args:
            token (str): JWT access token.

        Returns:
            tuple: A tuple containing:
                - valid_token (bool): Whether the token is valid or not.
                - user_id (int or None):
                    The user ID extracted from the token if valid, otherwise None.

        Raises:
            ExpiredSignatureError: If the token has expired.
            InvalidSignatureError: If the token signature is invalid.
        """

        valid_token = False
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("user_id", None)
        except jwt.exceptions.ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired", "valid_token": valid_token},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.exceptions.InvalidSignatureError:
            return Response(
                {"details": "Token is not valid", "valid_token": valid_token},
                status=status.HTTP_401_UNAUTHORIZED,
            )
        except jwt.exceptions.DecodeError:
            return Response(
                {"details": "Token decode error", "valid_token": valid_token},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_token = True

        return (valid_token, user_id)


class EmailSender:
    """Manage Sending email to users"""

    @staticmethod
    def send_activation_email(request, user):
        """
        Send activation email to the user

        Args:
            user: User model object
        """
        token = TokenHandler.get_tokens_for_user(user)
        current_site = get_current_site(request)
        protocol = "https" if request.is_secure() else "http"
        domain = current_site.domain
        email_obj = EmailMessage(
            "email/activation-email.tpl",
            {"protocol": protocol, "domain": domain, "token": token},
            "admin@admin.com",
            to=[user.email],
        )
        EmailThread(email_obj).start()

    @staticmethod
    def send_resetpassword_email(request, user):
        """
        Send password reset email to the user

        Args:
            user: User model object
        """
        token = TokenHandler.get_tokens_for_user(user)
        current_site = get_current_site(request)
        protocol = "https" if request.is_secure() else "http"
        domain = current_site.domain
        email_obj = EmailMessage(
            "email/resetpassword-email.tpl",
            {"protocol": protocol, "domain": domain, "token": token},
            "admin@admin.com",
            to=[user.email],
        )
        EmailThread(email_obj).start()
