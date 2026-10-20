import io
import subprocess
from pathlib import Path
from unittest.mock import Mock

import pytest
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile, TemporaryUploadedFile
from PIL import Image

from filemanager import services
from filemanager.models import File, validate_file_type


def image_upload(format="PNG", mode="RGB", size=(320, 160), name="image.png"):
    output = io.BytesIO()
    with Image.new(mode, size) as image:
        image.save(output, format=format)
    return SimpleUploadedFile(name, output.getvalue())


@pytest.fixture(scope="module")
def video_bytes(tmp_path_factory):
    path = tmp_path_factory.mktemp("video") / "short.mp4"
    subprocess.run(
        [
            settings.FFMPEG_BINARY,
            "-v",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "color=c=red:s=160x80:r=10",
            "-t",
            "0.2",
            "-c:v",
            "mpeg4",
            str(path),
        ],
        check=True,
        timeout=30,
    )
    return path.read_bytes()


@pytest.mark.parametrize("format", ["JPEG", "PNG", "GIF", "BMP", "TIFF"])
def test_image_type_is_detected_from_content(format):
    upload = image_upload(format=format, name="misleading.mp4")
    upload.seek(3)
    assert services.detect_file_type(upload) == "image"
    assert upload.tell() == 3
    assert not upload.closed


@pytest.mark.parametrize("mode", ["RGB", "RGBA", "L", "P"])
def test_image_thumbnail_is_bounded_rgb_jpeg(mode):
    upload = image_upload(mode=mode)
    upload.seek(2)
    result = services.image_thumbnail(upload)
    with Image.open(io.BytesIO(result)) as thumbnail:
        assert thumbnail.format == "JPEG"
        assert thumbnail.mode == "RGB"
        assert thumbnail.size == (100, 50)
    assert upload.tell() == 2
    assert not upload.closed


def test_small_images_are_not_enlarged():
    result = services.image_thumbnail(image_upload(size=(20, 10)))
    with Image.open(io.BytesIO(result)) as thumbnail:
        assert thumbnail.size == (20, 10)


def test_unsupported_image_format_is_rejected():
    with pytest.raises(services.InvalidMediaError, match="Unsupported image format"):
        services.detect_file_type(image_upload(format="WEBP"))


def test_short_in_memory_video_is_valid_and_produces_thumbnail(video_bytes):
    upload = SimpleUploadedFile(
        "misleading.jpg", video_bytes, content_type="image/jpeg"
    )
    validate_file_type(upload)
    kind, thumbnail_bytes = services.prepare_media(upload)
    assert kind == "video"
    with Image.open(io.BytesIO(thumbnail_bytes)) as thumbnail:
        assert thumbnail.format == "JPEG"
        assert thumbnail.size == (100, 50)
    assert upload.tell() == 0
    assert not upload.closed


def test_disk_video_upload_is_supported_and_original_is_preserved(video_bytes):
    with TemporaryUploadedFile(
        "video.mp4", "video/mp4", len(video_bytes), None
    ) as upload:
        upload.write(video_bytes)
        upload.seek(0)
        path = Path(upload.temporary_file_path())
        with services.local_media_path(upload) as local_path:
            assert Path(local_path) == path
        validate_file_type(upload)
        assert path.exists()


def test_audio_only_container_is_rejected(tmp_path):
    path = tmp_path / "audio.mp4"
    subprocess.run(
        [
            settings.FFMPEG_BINARY,
            "-v",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "anullsrc=r=8000:cl=mono",
            "-t",
            "0.2",
            "-c:a",
            "aac",
            str(path),
        ],
        check=True,
        timeout=30,
    )
    with pytest.raises(ValidationError):
        validate_file_type(SimpleUploadedFile("video.mp4", path.read_bytes()))


def test_text_disguised_as_media_is_rejected():
    with pytest.raises(ValidationError):
        validate_file_type(SimpleUploadedFile("image.jpg", b"not an image"))


def test_oversized_upload_is_rejected_before_decoding(monkeypatch):
    prepare = Mock()
    monkeypatch.setattr("filemanager.models.file.prepare_media", prepare)
    upload = SimpleUploadedFile("image.jpg", b"x")
    upload.size = 8 * 1024 * 1024
    with pytest.raises(ValidationError, match="exceeds"):
        validate_file_type(upload)
    prepare.assert_not_called()


def test_temporary_copy_is_cleaned_up_on_failure():
    upload = SimpleUploadedFile("video.mp4", b"content")
    upload.seek(2)
    with pytest.raises(RuntimeError):
        with services.local_media_path(upload) as path:
            assert Path(path).read_bytes() == b"content"
            raise RuntimeError("processing failed")
    assert not Path(path).exists()
    assert upload.tell() == 2


def test_subprocess_timeout_is_reported(monkeypatch):
    def timeout(*args, **kwargs):
        raise subprocess.TimeoutExpired(args[0], 30)

    monkeypatch.setattr(services.subprocess, "run", timeout)
    with pytest.raises(services.InvalidMediaError, match="timed out"):
        services.run_media_command(["ffmpeg"])


def test_missing_executable_is_not_reported_as_invalid_upload(settings):
    settings.FFPROBE_BINARY = "/nonexistent/filemanager-ffprobe"
    with pytest.raises(FileNotFoundError):
        services.detect_file_type(SimpleUploadedFile("video.mp4", b"content"))


def test_validated_upload_is_prepared_once_during_model_save(monkeypatch, video_bytes):
    calls = []
    original = services.run_media_command

    def run(command):
        calls.append(command[0])
        return original(command)

    monkeypatch.setattr(services, "run_media_command", run)
    monkeypatch.setattr("django.db.models.Model.save", Mock())
    upload = SimpleUploadedFile("video.mp4", video_bytes)
    instance = File(file=upload)
    validate_file_type(instance.file)
    instance.save()
    assert instance.type == "video"
    assert instance.thumbnail.name.endswith(".jpg")
    assert calls == [settings.FFPROBE_BINARY, settings.FFMPEG_BINARY]
    from django.db.models import Model

    Model.save.assert_called_once()


def test_video_is_staged_once_for_inspection_and_thumbnail(monkeypatch, video_bytes):
    temporary = Mock(wraps=services.tempfile.TemporaryDirectory)
    monkeypatch.setattr(services.tempfile, "TemporaryDirectory", temporary)
    services.prepare_media(SimpleUploadedFile("video.mp4", video_bytes))
    temporary.assert_called_once()


def test_failed_video_decode_is_rejected_and_copy_is_removed(monkeypatch):
    paths = []

    def run(command):
        if command[0] == settings.FFPROBE_BINARY:
            paths.append(command[-1])
            return b'{"format":{"format_name":"mov,mp4"},"streams":[{"codec_type":"video"}]}'
        raise services.InvalidMediaError("The media file could not be decoded.")

    monkeypatch.setattr(services, "run_media_command", run)
    with pytest.raises(ValidationError, match="decoded"):
        validate_file_type(SimpleUploadedFile("video.mp4", b"invalid frames"))
    assert paths and not Path(paths[0]).exists()


def test_decompression_bomb_is_rejected(monkeypatch):
    upload = image_upload(size=(100, 100))
    monkeypatch.setattr(Image, "MAX_IMAGE_PIXELS", 6000)
    with pytest.raises(ValidationError, match="Invalid image"):
        validate_file_type(upload)


def test_malformed_probe_output_is_rejected(monkeypatch):
    monkeypatch.setattr(services, "run_media_command", lambda command: b"not json")
    with pytest.raises(services.InvalidMediaError, match="metadata"):
        services.inspect_video("unused")


def test_image_model_thumbnail_uses_jpeg_extension(monkeypatch):
    saved = Mock()
    monkeypatch.setattr("django.db.models.Model.save", saved)
    instance = File(file=image_upload())
    validate_file_type(instance.file)
    instance.save()
    assert instance.type == "image"
    assert instance.thumbnail.name.endswith(".jpg")
    with Image.open(instance.thumbnail) as thumbnail:
        assert thumbnail.format == "JPEG"
    saved.assert_called_once()


@pytest.mark.parametrize(
    "suffix,codec",
    [
        (".mov", "mpeg4"),
        (".mkv", "mpeg4"),
        (".avi", "mpeg4"),
        (".wmv", "wmv2"),
        (".mpeg", "mpeg2video"),
    ],
)
def test_supported_video_containers(suffix, codec, tmp_path):
    path = tmp_path / ("video" + suffix)
    subprocess.run(
        [
            settings.FFMPEG_BINARY,
            "-v",
            "error",
            "-nostdin",
            "-f",
            "lavfi",
            "-i",
            "color=c=blue:s=160x80:r=25",
            "-t",
            "0.2",
            "-c:v",
            codec,
            str(path),
        ],
        check=True,
        timeout=30,
    )
    upload = SimpleUploadedFile("disguised.bin", path.read_bytes())
    validate_file_type(upload)
    assert services.prepare_media(upload)[0] == "video"


def test_django_starts_without_removed_moviepy_dependencies():
    script = """
import os
import sys

class RemovedPackages:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {
            'moviepy', 'numpy', 'imageio', 'imageio_ffmpeg', 'decorator',
            'proglog', 'requests', 'tqdm', 'charset_normalizer', 'idna',
        }:
            raise ImportError('Removed dependency: ' + fullname)

sys.meta_path.insert(0, RemovedPackages())
os.environ['DJANGO_SETTINGS_MODULE'] = 'core.django.test'
import django
django.setup()
from django.core.management import call_command
call_command('check')
"""
    subprocess.run(
        ["python", "-c", script], check=True, timeout=30, capture_output=True
    )
