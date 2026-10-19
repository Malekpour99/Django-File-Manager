"""Shared environment reader; process variables take precedence over .env."""

import os
from pathlib import Path

from decouple import (
    AutoConfig,
    Config,
    Csv as Csv,
    RepositoryEmpty,
    UndefinedValueError,
    undefined,
)

BASE_DIR = Path(__file__).resolve().parent.parent
# The repository root locally; Docker Compose supplies process variables in /app.
PROJECT_ROOT = BASE_DIR.parent
# Tests must not inherit a developer's .env or require integration credentials.
_TESTING = os.environ.get("DJANGO_SETTINGS_MODULE") == "core.django.test"
_config = (
    Config(RepositoryEmpty()) if _TESTING else AutoConfig(search_path=str(PROJECT_ROOT))
)


def env(name, default=undefined, cast=undefined, *, legacy=None):
    """Read a setting, accepting its previous name during migration."""
    try:
        return _config(name, cast=cast)
    except UndefinedValueError:
        pass
    if legacy is not None and not _TESTING:
        return _config(legacy, default=default, cast=cast)
    return _config(name, default=default, cast=cast)
