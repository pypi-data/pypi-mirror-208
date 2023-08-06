"""Azure blob storage module."""
import functools
import io
import os
import re
import stat
import typing as t

import azure.core.exceptions as az_errors
from azure.core.exceptions import ClientAuthenticationError, HttpResponseError
from azure.identity import DefaultAzureCredential
from azure.storage.blob import ContainerClient, _blob_client
from azure.storage.blob._shared.policies import StorageRetryPolicy
from fw_utils import AnyFile, Filters, open_any
from pydantic import BaseSettings

from .. import errors
from ..config import AZConfig
from ..fileinfo import FileInfo
from ..filters import StorageFilter
from ..storage import AnyPath, CloudStorage

__all__ = ["AZStorage"]


def create_default_client(
    account: str,
    container: str,
    access_key: str = None,
) -> ContainerClient:
    """Azure Blob Container Client factory.

    Uses the Azure Access Key passed in directly OR provided via the envvar
    AZURE_ACCESS_KEY.

    See the Azure docs for the full list of supported credential sources:
    https://docs.microsoft.com/en-us/python/api/azure-identity/azure.identity.defaultazurecredential
    """
    from_creds = functools.partial(ContainerClient, account, container)
    no_retry = AzureRetryPolicy(RetryConfig(total=1, backoff_factor=0.1))
    retry_policy = AzureRetryPolicy(RetryConfig())

    def check_key(client):
        try:
            client.get_account_information()
        except ClientAuthenticationError as e:
            raise e  # pragma: no cover
        except HttpResponseError as e:  # pragma: no cover
            if e.status_code in (401, 403):
                raise e

    if access_key:
        check_key(from_creds(credential=str(access_key), retry_policy=no_retry))
        return from_creds(credential=str(access_key), retry_policy=retry_policy)

    check_key(from_creds(credential=DefaultAzureCredential(), retry_policy=no_retry))
    return from_creds(credential=DefaultAzureCredential(), retry_policy=retry_policy)


class RetryConfig(BaseSettings):
    """Retry config."""

    class Config:
        """Model config."""

        env_prefix = "AZURE_RETRY_"

    total: int = 3
    backoff_factor: float = 0.5


class AzureRetryPolicy(StorageRetryPolicy):
    """Custom Azure retry policy."""

    def __init__(self, config: RetryConfig):
        """Init retry policy."""
        self.backoff_factor = config.backoff_factor
        super().__init__(retry_total=config.total, retry_to_secondary=False)

    def get_backoff_time(self, settings):  # pragma: no cover
        """Calculates how long to sleep before retrying."""
        # TODO re-add cover
        return self.backoff_factor * (2 ** settings["count"] - 1)


ERRMAP = {
    az_errors.ClientAuthenticationError: errors.PermError,
    az_errors.ResourceNotFoundError: errors.FileNotFound,
    az_errors.ResourceExistsError: errors.FileExists,
    az_errors.AzureError: errors.StorageError,
}
errmap = errors.ErrorMapper(ERRMAP)


class AZStorage(CloudStorage):
    """Azure Blob Storage class."""

    # NOTE Azure only supports up to 256 requests in a single batch
    delete_batch_size: t.ClassVar[int] = 256

    def __init__(
        self,
        config: AZConfig,
        **kwargs,
    ) -> None:
        """Construct Azure storage."""
        self.config = config

        secret = None
        if self.config.access_key:
            secret = self.config.access_key.get_secret_value()

        self.client = create_default_client(
            self.config.account, self.config.container, secret
        )

        super().__init__(**kwargs)

    def abspath(self, path: AnyPath) -> str:
        """Return path string relative to the storage URL, including the perfix."""
        return f"{self.config.prefix}/{self.relpath(path)}".lstrip("/")

    def fullpath(self, path: AnyPath) -> str:
        """Return path string including the storage URL and prefix."""
        return f"az://{self.config.account}/{self.config.container}/{self.abspath(path)}".rstrip(
            "/"
        )

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
        path = self.abspath(path)
        filt = StorageFilter(include=include, exclude=exclude)
        for blob in self.client.list_blobs(name_starts_with=path):
            relpath = re.sub(rf"^{self.config.prefix}", "", blob.name).lstrip("/")
            info = FileInfo(
                path=relpath,
                size=blob.size,
                hash=blob.etag,
                created=blob.creation_time.timestamp(),
                modified=blob.last_modified.timestamp(),
            )
            # skip az "folders" - path is empty if the prefix itself is a "folder"
            if not relpath or relpath.endswith("/") and info.size == 0:
                continue  # pragma: no cover
            if filt.match(info):
                yield info

    @errmap
    def stat(self, path: AnyPath) -> FileInfo:
        """Return FileInfo for a single file."""
        blob_client = self.client.get_blob_client(self.abspath(path))
        blob = blob_client.get_blob_properties()
        return FileInfo(
            path=str(path),
            size=blob.size,
            hash=blob.etag,
            created=blob.creation_time.timestamp(),
            modified=blob.last_modified.timestamp(),
        )

    @errmap
    def download_file(self, path: str, dst: t.IO[bytes]) -> None:
        """Download file and it is opened for reading in binary mode."""
        blob_stream = self.client.download_blob(path)
        blob_stream.readinto(dst)

    @errmap
    def upload_file(self, path: str, file: AnyFile) -> None:
        """Write source file to the given path."""
        # upload_blob uses automatic chunking stated by Azure documentation
        with open_any(file, mode="rb") as r_file:
            self.client.upload_blob(name=path, data=r_file, overwrite=True)

    @errmap
    def flush_delete(self) -> None:
        """Remove a file at the given path."""
        self.client.delete_blobs(*self.delete_keys, delete_snapshots="include")
        self.delete_keys.clear()


# patch Azure SDK's get_length to support streaming from requests (sockets)
# see: https://flywheelio.atlassian.net/browse/FLYW-11776

orig_get_length = _blob_client.get_length


def get_length_patch(data) -> t.Optional[int]:
    """Return None instead of 0 if data is a socket."""
    try:
        fileno = data.fileno()
        fstat = os.fstat(fileno)
        if stat.S_ISSOCK(fstat.st_mode):
            return None
    except (AttributeError, OSError, io.UnsupportedOperation):
        pass
    return orig_get_length(data)


_blob_client.get_length = get_length_patch
