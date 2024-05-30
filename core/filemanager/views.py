from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import CreateView, DeleteView
from django.db.models import Q

from .models import File, Folder
from accounts.models import Profile


class ContentView(LoginRequiredMixin, View):
    """
    Showing list of files and folders for the authenticated owner
    """

    def get(self, request, *args, **kwargs):
        files = File.objects.filter(
            Q(owner__user__id=self.request.user.id) & Q(folder__name=None)
        )
        folders = Folder.objects.filter(
            Q(owner__user__id=self.request.user.id) & Q(parent_folder=None)
        )
        folder_path = "home"
        context = {"files": files, "folders": folders, "folder_path": folder_path}
        return render(request, "filemanager/content-list.html", context)


class FileUploadView(LoginRequiredMixin, CreateView):
    """
    Uploading a new file and dedicating this file to the current user
    """

    template_name = "filemanager/content-list.html"
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
    template_name = "filemanager/content-list.html"
    success_url = reverse_lazy("filemanager:home")
