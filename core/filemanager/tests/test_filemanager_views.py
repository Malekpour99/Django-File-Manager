from django.urls import reverse
from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

import os
import pytest

from accounts.models import Profile
from filemanager.models import File, Folder

# test image paths for tests
source_path = "statics/img/test.jpg"
destination_path = "media/test.jpg"

# Check if the file doesn't exist in the destination
if not os.path.exists(destination_path):
    # Copying test image to the media folder for tests
    with open(source_path, "rb") as src_file:
        content = src_file.read()

    with open(destination_path, "wb") as dest_file:
        dest_file.write(content)


@pytest.fixture
def user():
    return get_user_model().objects.create_user(
        email="user@test.com", password="testPassword", is_verified=True
    )


@pytest.fixture
def profile(user):
    # getting the profile from the tuple (don't need created_status boolean)
    return Profile.objects.get_or_create(user=user)[0]


@pytest.fixture
def client(user):
    client = Client()
    client.force_login(user=user)
    return client


@pytest.fixture
def folder(profile):
    return Folder.objects.create(name="Test Folder", owner=profile)


@pytest.fixture
def file(profile, folder):
    return File.objects.create(
        name="Test File", owner=profile, folder=folder, file="./test.jpg"
    )


@pytest.fixture(autouse=True)
def cleanup():
    yield
    uploaded_file_path = "media/uploads/test.jpg"
    if os.path.exists(uploaded_file_path):
        os.remove(uploaded_file_path)


@pytest.mark.django_db
def test_content_view(client, folder, file):
    url = reverse("filemanager:folder-content", kwargs={"folder_slug": "test-folder"})
    response = client.get(url)
    assert response.status_code == 200
    assert "files" in response.context
    assert "folders" in response.context
    assert response.context["current_folder"] == folder
    assert response.context["folder_path"] == "home / " + folder.get_nested_path()
    assert response.templates[0].name == "filemanager/content-list.html"


@pytest.mark.django_db
def test_file_upload_view(client, folder):
    url = reverse("filemanager:upload-file")
    with open("media/test.jpg", "rb") as fp:
        # simulating a real file upload
        file_data = SimpleUploadedFile(fp.name, fp.read(), content_type="image/jpeg")
        response = client.post(url, {"file": file_data, "folder": folder.id})
    assert response.status_code == 302
    assert File.objects.filter(name="test.jpg", folder=folder).exists()


@pytest.mark.django_db
def test_folder_create_view(client, folder):
    url = reverse("filemanager:create-folder")
    response = client.post(url, {"name": "New Folder", "parent_folder": folder.id})
    assert response.status_code == 302
    assert Folder.objects.filter(name="New Folder", parent_folder=folder).exists()


@pytest.mark.django_db
def test_file_update_view(client, file):
    url = reverse("filemanager:update-file", kwargs={"pk": file.id})
    response = client.post(url, {"name": "Updated File Name"})
    assert response.status_code == 302
    file.refresh_from_db()
    assert file.name == "Updated File Name"


@pytest.mark.django_db
def test_folder_update_view(client, folder):
    url = reverse("filemanager:update-folder", kwargs={"pk": folder.id})
    response = client.post(url, {"name": "Updated Folder Name"})
    assert response.status_code == 302
    folder.refresh_from_db()
    assert folder.name == "Updated Folder Name"


@pytest.mark.django_db
def test_search_view(client, file, folder):
    url = reverse("filemanager:search")
    response = client.get(url, {"search": "Test"})
    assert response.status_code == 200
    assert "files" in response.context
    assert "folders" in response.context
    assert file in response.context["files"]
    assert folder in response.context["folders"]
    assert response.templates[0].name == "filemanager/search-list.html"


@pytest.mark.django_db
def test_file_delete_view(client, file):
    url = reverse("filemanager:delete-file", kwargs={"pk": file.id})
    response = client.post(url)
    assert response.status_code == 302
    assert not File.objects.filter(id=file.id).exists()


@pytest.mark.django_db
def test_folder_delete_view(client, folder):
    url = reverse("filemanager:delete-folder", kwargs={"pk": folder.id})
    response = client.post(url)
    assert response.status_code == 302
    assert not Folder.objects.filter(id=folder.id).exists()
