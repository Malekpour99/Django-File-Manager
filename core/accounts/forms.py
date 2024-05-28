from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model


class CustomUserCreationForm(UserCreationForm):
    """
    Form for creating a new user in our custom user model
    """

    class Meta:
        model = get_user_model()
        fields = ("email", "password1", "password2")
