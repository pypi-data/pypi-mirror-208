"""Google Cloud Storage module."""
import json
import re
import typing as t

import google.api_core.exceptions as gs_errors
from fw_utils import AnyFile, Filters
from google.cloud.storage import Client
from google.cloud.storage.retry import DEFAULT_RETRY

from .. import errors
from ..config import GSConfig
from ..fileinfo import FileInfo
from ..filters import StorageFilter
from ..storage import AnyPath, CloudStorage

__all__ = ["GSStorage"]

DEFAULT_CONTENT_TYPE = "application/octet-stream"

ERRMAP = {
    gs_errors.NotFound: errors.FileNotFound,
    gs_errors.Forbidden: errors.PermError,
    gs_errors.GoogleAPIError: errors.StorageError,
}
errmap = errors.ErrorMapper(ERRMAP)


class GSStorage(CloudStorage):
    """Google Cloud Storage class."""

    def __init__(  # noqa: D417
        self,
        config: GSConfig,
        **kwargs,
    ):
        """Google Cloud Storage class for working with blobs in GCS buckets.

        Args:
            config: config: GSConfig
        """
        self.config = config

        secret = None
        if self.config.application_credentials:
            secret = self.config.application_credentials.get_secret_value()
        if secret and secret.strip().startswith("{"):
            creds_obj = json.loads(secret)
            self.client = Client.from_service_account_info(info=creds_obj)
        else:
            # fallback to default credentials
            self.client = Client()  # pragma: no cover

        super().__init__(**kwargs)

    def abspath(self, path: AnyPath) -> str:
        """Return path string relative to the storage URL, including the perfix."""
        return f"{self.config.prefix}/{self.relpath(path)}".lstrip("/")

    def fullpath(self, path: AnyPath) -> str:
        """Return path string including the storage URL and prefix."""
        return f"gs://{self.config.bucket}/{self.abspath(path)}".rstrip("/")

    @errmap
    def ls(
        self,
        path: AnyPath = "",
        *,
        include: Filters = None,
        exclude: Filters = None,
        **_,
    ) -> t.Iterator[FileInfo]:
        """Yield each item under prefix matching the include/exclude filters."""
        # https://cloud.google.com/storage/docs/folders#gsutil
        # https://cloud.google.com/storage/docs/hashes-etags
        filt = StorageFilter(include=include, exclude=exclude)
        prefix = f"{self.config.prefix}/{path}".strip("/")
        if prefix:
            prefix += "/"
        for blob in self.client.list_blobs(self.config.bucket, prefix=prefix):
            relpath = re.sub(rf"^{self.config.prefix}", "", blob.name).lstrip("/")
            info = FileInfo(
                path=relpath,
                size=blob.size,
                hash=blob.etag,
                created=blob.time_created.timestamp(),
                modified=blob.updated.timestamp(),
            )
            # skip gs "folders" - path is empty if the prefix itself is a "folder"
            if not relpath or relpath.endswith("/") and info.size == 0:
                continue  # pragma: no cover
            if filt.match(info):
                yield info

    @errmap
    def stat(self, path: AnyPath) -> FileInfo:
        """Return FileInfo for a single file."""
        blob = self.client.bucket(self.config.bucket).blob(self.abspath(path))
        blob.reload()
        return FileInfo(
            path=str(path),
            size=blob.size,
            hash=blob.etag,
            created=blob.time_created.timestamp(),
            modified=blob.updated.timestamp(),
        )

    @errmap
    def download_file(self, path: str, dst: t.IO[bytes]) -> None:
        """Download file and it opened for reading in binary mode."""
        self.client.bucket(self.config.bucket).blob(path).download_to_file(dst)

    @errmap
    def upload_file(self, path: str, file: AnyFile) -> None:
        """Upload file to the given path."""
        blob = self.client.bucket(self.config.bucket).blob(path)
        if isinstance(file, bytes):
            upload_func = blob.upload_from_string
        elif isinstance(file, str):
            upload_func = blob.upload_from_filename
        else:
            upload_func = blob.upload_from_file
        # by default, only uploads with if_generation_match set
        # will be retried, override this and retry always for now
        # TODO consider fetching the current generation and use that
        # but it would require one additional request per upload
        # see: https://cloud.google.com/storage/docs/generations-preconditions
        upload_func(file, content_type=DEFAULT_CONTENT_TYPE, retry=DEFAULT_RETRY)

    @errmap
    def flush_delete(self):
        """Flush pending remove operations."""
        for key in sorted(self.delete_keys):
            self.client.bucket(self.config.bucket).blob(key).delete()
            self.delete_keys.remove(key)
