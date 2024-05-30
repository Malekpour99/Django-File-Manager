from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, CreateView, DeleteView
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


class FileUploadView(LoginRequiredMixin, CreateView):
    """
    Uploading a new file and dedicating this file to the current user
    """

    template_name = "filemanager/file-list.html"
    model = File
    fields = ["file"]
    success_url = reverse_lazy("filemanager:home")

    def form_valid(self, form):
        form.instance.owner = Profile.objects.get(user__id=self.request.user.id)
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["files"] = File.objects.filter(owner__user=self.request.user)
        return context


class FileDeleteView(LoginRequiredMixin, DeleteView):
    """
    Deleting specified file
    """

    model = File
    template_name = "filemanager/file-list.html"
    success_url = reverse_lazy("filemanager:home")
