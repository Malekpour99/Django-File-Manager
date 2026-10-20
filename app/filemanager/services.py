"""Content inspection and thumbnail generation, independent of database writes."""

import io
import json
import subprocess
import tempfile
import warnings
from contextlib import contextmanager
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from PIL import Image, UnidentifiedImageError

THUMBNAIL_SIZE = (100, 100)
IMAGE_FORMATS = {"JPEG", "PNG", "GIF", "BMP", "TIFF"}
VIDEO_FORMATS = {
    "mov",
    "mp4",
    "m4a",
    "3gp",
    "3g2",
    "mj2",
    "matroska",
    "webm",
    "avi",
    "asf",
    "mpeg",
    "mpegts",
    "mpegvideo",
}


class InvalidMediaError(ValueError):
    """The file cannot be decoded as a supported image or video."""


@contextmanager
def local_media_path(value):
    """Reuse disk uploads; copy remote or in-memory files only when required."""
    source = value if isinstance(value, UploadedFile) else getattr(value, "file", value)
    temporary_path = getattr(source, "temporary_file_path", None)
    if temporary_path is not None:
        yield temporary_path()
        return
    position = value.tell()
    try:
        with tempfile.TemporaryDirectory(prefix="filemanager-media-") as directory:
            path = Path(directory) / "input"
            with path.open("wb") as output:
                for chunk in value.chunks():
                    output.write(chunk)
            yield str(path)
    finally:
        value.seek(position)


def run_media_command(command):
    try:
        return subprocess.run(
            command,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=settings.MEDIA_PROCESS_TIMEOUT,
            check=True,
        ).stdout
    except subprocess.TimeoutExpired as error:
        raise InvalidMediaError("Media processing timed out.") from error
    except subprocess.CalledProcessError as error:
        raise InvalidMediaError("The media file could not be decoded.") from error
    # Missing executables are deployment errors, not invalid user uploads.


def is_supported_image(value):
    position = value.tell()
    try:
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("error", Image.DecompressionBombWarning)
                with Image.open(value) as image:
                    if image.format not in IMAGE_FORMATS:
                        raise InvalidMediaError("Unsupported image format.")
                    image.verify()
            return True
        except UnidentifiedImageError:
            return False
        except (
            OSError,
            SyntaxError,
            Image.DecompressionBombError,
            Image.DecompressionBombWarning,
        ) as error:
            raise InvalidMediaError("Invalid image file.") from error
    finally:
        value.seek(position)


def inspect_video(path):
    output = run_media_command(
        [
            settings.FFPROBE_BINARY,
            "-v",
            "error",
            "-protocol_whitelist",
            "file,pipe",
            "-select_streams",
            "v:0",
            "-show_entries",
            "format=format_name:stream=codec_type:stream_disposition=attached_pic",
            "-of",
            "json",
            path,
        ]
    )
    try:
        info = json.loads(output)
        formats = set(info.get("format", {}).get("format_name", "").split(","))
        streams = info.get("streams", [])
        if formats & VIDEO_FORMATS and any(
            stream.get("codec_type") == "video"
            and not stream.get("disposition", {}).get("attached_pic", 0)
            for stream in streams
        ):
            return "video"
    except (ValueError, TypeError, AttributeError) as error:
        raise InvalidMediaError("Invalid video metadata.") from error
    raise InvalidMediaError(
        "Unsupported file type. Only images and videos are supported."
    )


def image_thumbnail(value):
    position = value.tell()
    try:
        with Image.open(value) as image:
            # Resize before RGB conversion so JPEG decoder reduction remains available.
            image.thumbnail(THUMBNAIL_SIZE, Image.Resampling.LANCZOS)
            with image.convert("RGB") as thumbnail:
                output = io.BytesIO()
                thumbnail.save(output, format="JPEG")
                return output.getvalue()
    finally:
        value.seek(position)


def video_thumbnail_from_path(path):
    output = run_media_command(
        [
            settings.FFMPEG_BINARY,
            "-v",
            "error",
            "-nostdin",
            "-threads",
            "1",
            "-protocol_whitelist",
            "file,pipe",
            "-i",
            path,
            "-map",
            "0:v:0",
            "-frames:v",
            "1",
            "-an",
            "-vf",
            "scale=w='min(100,iw)':h='min(100,ih)':force_original_aspect_ratio=decrease",
            "-threads",
            "1",
            "-f",
            "image2pipe",
            "-c:v",
            "mjpeg",
            "pipe:1",
        ]
    )
    if not output:
        raise InvalidMediaError("The video contains no decodable frame.")
    return output


def prepare_media(value):
    """Reuse validated thumbnails on the same immutable upload during form saving."""
    source = value if isinstance(value, UploadedFile) else getattr(value, "file", value)
    cached = getattr(source, "_filemanager_prepared_media", None)
    if cached is not None:
        return cached
    if is_supported_image(value):
        kind = "image"
        try:
            thumbnail = image_thumbnail(value)
        except (OSError, SyntaxError, ValueError) as error:
            raise InvalidMediaError("Invalid image file.") from error
    else:
        with local_media_path(value) as path:
            kind = inspect_video(path)
            thumbnail = video_thumbnail_from_path(path)
    result = kind, thumbnail
    if isinstance(source, UploadedFile):
        source._filemanager_prepared_media = result
    return result


def detect_file_type(value):
    if is_supported_image(value):
        return "image"
    with local_media_path(value) as path:
        return inspect_video(path)
