from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import FormView
from django.contrib.auth import login

from .forms import CustomUserCreationForm


class RegisterView(FormView):
    """
    Managing registration of new users
    """

    template_name = "registration/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("")

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            # login user after successful registration
            login(self.request, user)
        return super().form_valid(form)

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().get(request, *args, **kwargs)
