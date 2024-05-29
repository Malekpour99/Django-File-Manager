from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView
from .models import File
from accounts.models import Profile


class FileListView(LoginRequiredMixin, ListView):
    """
    Showing list of files for the authenticated owner
    """

    template_name = "filemanager/file-list.html"
    context_object_name = "files"

    def get_queryset(self):
        files = File.objects.filter(owner__user__id=self.request.user.id)
        return files
