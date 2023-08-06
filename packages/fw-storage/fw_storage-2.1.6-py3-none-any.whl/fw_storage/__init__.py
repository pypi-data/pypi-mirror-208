"""Flywheel storage library."""
from importlib.metadata import version

__version__ = version(__name__)
__all__ = [
    "FileExists",
    "FileNotFound",
    "IsADirectory",
    "NotADirectory",
    "PermError",
    "Storage",
    "StorageError",
    "create_storage_client",
    "create_storage_config",
]

from .errors import (
    FileExists,
    FileNotFound,
    IsADirectory,
    NotADirectory,
    PermError,
    StorageError,
)
from .storage import Storage, create_storage_client, create_storage_config
