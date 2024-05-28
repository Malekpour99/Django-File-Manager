from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

import jwt
from mail_templated import EmailMessage

from .serializers import (
    RegistrationSerializer,
    CustomAuthTokenSerializer,
    ChangePasswordSerializer,
    CustomTokenObtainPairSerializer,
    ActivationResendSerializer,
    ProfileSerializer,
    ResetPasswordSerializer,
    ResetPasswordConfirmSerializer,
)
from ..utils import EmailThread
from accounts.models import Profile


User = get_user_model()


class TokenHandler:
    """Handling token related processes"""

    @staticmethod
    def get_tokens_for_user(user):
        """Return an access token (JWT) based on the user"""
        refresh = RefreshToken.for_user(user)
        return str(refresh.access_token)


class EmailSender:
    """Sending email to users"""

    @staticmethod
    def send_activation_email(request, user):
        """Send activation email to the user"""
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
        """Send password reset email to the user"""
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


class UserRegistration(GenericAPIView):
    """Register new users"""

    serializer_class = RegistrationSerializer

    def post(self, request):
        """Create a new user from provided data"""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        email = serializer.validated_data["email"]
        data = {"email": email}
        user_obj = get_object_or_404(User, email=email)
        EmailSender.send_activation_email(request, user_obj)
        # Prevention of receiving hashed password in the serializer.data
        return Response(data, status=status.HTTP_201_CREATED)


class ChangePasswordAPIView(GenericAPIView):
    """Changing user's password"""

    permission_classes = [IsAuthenticated]
    model = User
    serializer_class = ChangePasswordSerializer

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response(
                    {"old_password": ["Wrong password."]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            return Response(
                {"details": "password changed successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomObtainAuthToken(ObtainAuthToken):
    """Generate an authentication token for user"""

    serializer_class = CustomAuthTokenSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key, "user_id": user.pk, "email": user.email})


class CustomDiscardAuthToken(APIView):
    """Delete user's existing authentication token"""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ObjectDoesNotExist:
            return Response(
                {"detail": "Token does not exist"}, status=status.HTTP_404_NOT_FOUND
            )


class CustomTokenObtainPairView(TokenObtainPairView):
    """Obtaining JWT pairs for user"""

    serializer_class = CustomTokenObtainPairSerializer


class ActivationAPIView(APIView):
    """Decoding JWT authentication token and activating user account"""

    def get(self, request, token, *args, **kwargs):
        try:
            token = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = token.get("user_id", None)
        except jwt.exceptions.ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.InvalidSignatureError:
            return Response(
                {"details": "Token is not valid"}, status=status.HTTP_400_BAD_REQUEST
            )
        user_obj = User.objects.get(pk=user_id)
        if user_obj.is_verified:
            return Response(
                {"details": "Your account has already been verified and is active"}
            )
        user_obj.is_verified = True
        user_obj.save()
        return Response({"details": "Your account has been verified and activated"})


class ActivationResendAPIView(GenericAPIView):
    """Resending JWT authentication token for user activation"""

    serializer_class = ActivationResendSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        EmailSender.send_activation_email(request, user_obj)
        return Response(
            {"details": "Activation link resend was successful"},
            status=status.HTTP_200_OK,
        )


class ProfileAPIView(RetrieveUpdateAPIView):
    """Getting authenticated user's profile data"""

    permission_classes = [IsAuthenticated]
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_object(self):
        # Since we only need one object, we override the get_object method instead of get_queryset
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


class ResetPasswordAPIView(GenericAPIView):
    """Sending a reset password link to the user by email"""

    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        if user_obj:
            EmailSender.send_resetpassword_email(request, user_obj)
        return Response(
            {
                "details": "reset password link was sent to you."
                # if you didn't receive it, check your email address or spam
            }
        )


class ResetPasswordValidateAPIView(APIView):
    """Validating JWT token"""

    def get(self, request, token, *args, **kwargs):
        valid_token = False
        try:
            jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        except jwt.exceptions.ExpiredSignatureError:
            return Response(
                {"details": "Token has been expired", "valid_token": valid_token},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except jwt.exceptions.InvalidSignatureError:
            return Response(
                {"details": "Token is not valid", "valid_token": valid_token},
                status=status.HTTP_400_BAD_REQUEST,
            )
        valid_token = True
        data = {
            "token": token,
            "valid_token": valid_token,
        }
        # token can also be saved in the session to be used
        # then check the valid_token and redirect user to the the password reset form
        return Response(data, status=status.HTTP_200_OK)


class ResetPasswordConfirmAPIView(GenericAPIView):
    """Resetting user's password"""

    serializer_class = ResetPasswordConfirmSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uid = serializer.validated_data.get("uid")
        user_obj = User.objects.get(pk=uid)
        # set_password also hashes the password that the user will get
        user_obj.set_password(serializer.validated_data.get("password"))
        user_obj.save()
        return Response(
            {"details": "Reset password was successful"},
            status=status.HTTP_200_OK,
        )
