"""Storage base class and factory."""
import abc
import importlib
import typing as t
from pathlib import Path

from fw_utils import AnyFile, BinFile, TempFile, parse_url
from memoization import cached

from .config import Config
from .fileinfo import FileInfo

SPOOLED_TMP_MAX_SIZE = 1 << 20  # 1MB
# map of url schemes to storage class import paths (and user-registered classes)
# TODO fw:// storage class
ConfigType = t.Union[str, t.Type["Config"]]
StorageType = t.Union[str, t.Type["Storage"]]
STORAGE_CLASSES: t.Dict[str, t.Tuple[ConfigType, StorageType]] = {
    "fs": ("fw_storage.config.FSConfig", "fw_storage.types.fs.FSStorage"),
    "s3": ("fw_storage.config.S3Config", "fw_storage.types.s3.S3Storage"),
    "gs": ("fw_storage.config.GSConfig", "fw_storage.types.gs.GSStorage"),
    "az": ("fw_storage.config.AZConfig", "fw_storage.types.az.AZStorage"),
    "dicom": ("fw_storage.config.DICOMConfig", "fw_storage.types.dicom.DICOMStorage"),
    "dicomweb": (
        "fw_storage.config.DICOMWebConfig",
        "fw_storage.types.dicomweb.DICOMWebStorage",
    ),
}

AnyPath = t.Union[str, FileInfo]


class Storage(abc.ABC):
    """Abstract storage class defining the common interface."""

    @staticmethod
    def relpath(path: AnyPath) -> str:
        """Return path string relative to the storage prefix."""
        return str(path).lstrip("/")

    @abc.abstractmethod
    def abspath(self, path: AnyPath) -> str:
        """Return path string relative to the storage URL, including the perfix."""

    @abc.abstractmethod
    def fullpath(self, path: AnyPath) -> str:
        """Return path string including the storage URL and prefix."""

    @abc.abstractmethod
    def ls(
        self,
        path: AnyPath = "",
        *,
        include: t.Optional[t.List[str]] = None,
        exclude: t.Optional[t.List[str]] = None,
        **kwargs,
    ) -> t.Iterator[FileInfo]:
        """Yield items under path that match the include/exclude filters."""

    @abc.abstractmethod
    def stat(self, path: AnyPath) -> FileInfo:
        """Return FileInfo for a given path."""

    @abc.abstractmethod
    def get(self, path: AnyPath, **kwargs) -> BinFile:
        """Return a file opened in binary reading mode."""

    @abc.abstractmethod
    def set(self, path: AnyPath, file: AnyFile) -> None:
        """Write a file at a given path in storage."""

    @abc.abstractmethod
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove a file from storage."""

    # TODO add opt-in perf testing
    def test_read(self):
        """Verify read access (list files then stat/get the 1st)."""
        file = stat = None
        for file in self.ls():
            stat = self.stat(file)
            break
        # TODO implement get(path, stream=True) instead...
        if file and stat and stat.size < 1 << 20:  # < 1MB
            self.get(file)
        self.cleanup()

    def test_write(self):
        """Verify write access (create/remove a test file)."""
        self.set("flywheel-write-test", b"flywheel-write-test")
        self.rm("flywheel-write-test")
        self.cleanup()

    def cleanup(self) -> None:
        """Run any cleanup steps for the storage (eg. tempfiles, buffers)."""

    def __enter__(self):
        """Enter storage 'with' context to enable automatic cleanup()."""
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        """Invoke cleanup() when exiting the storage 'with' context."""
        self.cleanup()

    def __del__(self) -> None:
        """Invoke cleanup() when the storage is garbage-collected."""
        self.cleanup()

    def __str__(self) -> str:  # pragma: no cover
        """Return string representation of the storage."""
        return f"{self.__class__.__name__}({self.fullpath('')!r})"


class CloudStorage(Storage):
    """Base class for Cloud Storages."""

    delete_batch_size: t.ClassVar[int] = 1000

    def __init__(
        self,
        *_args,
        **_kwargs,
    ):
        """Initialize cloud storage, check permission and setup cache."""
        self.delete_keys: t.Set[str] = set()

    @abc.abstractmethod
    def download_file(self, path: str, dst: t.IO[bytes]) -> None:
        """Download file and it opened for reading in binary mode."""

    @abc.abstractmethod
    def upload_file(self, path: str, file: AnyFile) -> None:
        """Upload file to the given path."""

    @abc.abstractmethod
    def flush_delete(self):
        """Flush pending remove operations."""

    def get(self, path: AnyPath, **_kwargs) -> BinFile:
        """Return a file opened for reading in binary mode."""
        abspath = self.abspath(path)
        file = TempFile()
        self.download_file(abspath, file)
        file.seek(0)
        return BinFile(t.cast(t.BinaryIO, file), metapath=self.relpath(path))

    def set(self, path: AnyPath, file: AnyFile) -> None:
        """Write a file at the given path in storage."""
        path = self.abspath(path)
        file = str(file) if isinstance(file, Path) else file
        self.upload_file(path, file)

    def rm(self, path: AnyPath, recurse: bool = False, flush: bool = False) -> None:
        """Remove file from storage.

        Removing objects is delayed and performed in batches (see 'flush_delete').
        """
        if not recurse:
            self.delete_keys.add(self.abspath(path))
        else:
            for file in self.ls(path):
                self.delete_keys.add(self.abspath(file))
                if len(self.delete_keys) >= self.delete_batch_size:
                    self.flush_delete()
        if flush or len(self.delete_keys) >= self.delete_batch_size:
            self.flush_delete()

    def cleanup(self):
        """Flush pending remove operations and clear cache."""
        if hasattr(self, "delete_keys") and self.delete_keys:
            self.flush_delete()


def create_storage_client(storage_url: str) -> Storage:
    """Return storage instance for a storage URL (factory)."""
    parsed = parse_url(storage_url)
    scheme = parsed["scheme"]
    if scheme not in STORAGE_CLASSES:
        raise ValueError(f"Unknown storage URL scheme {scheme}")
    _, storage_cls = STORAGE_CLASSES[scheme]
    if isinstance(storage_cls, str):
        storage_cls = create_storage_client_cls(storage_cls)

    config = create_storage_config(storage_url)
    return storage_cls(config)  # type: ignore


def create_storage_config(storage_url: str) -> Config:
    """Return storage config instance for a storage URL (factory)."""
    parsed = parse_url(storage_url)
    scheme = parsed["scheme"]
    if scheme not in STORAGE_CLASSES:
        raise ValueError(f"Unknown storage URL scheme {scheme}")
    config_cls, _ = STORAGE_CLASSES[scheme]
    if isinstance(config_cls, str):
        config_cls = get_config_cls(config_cls)

    return config_cls.from_url(storage_url)


def get_config_cls(config_cls_path: str) -> t.Type["Config"]:
    """Return the config class for an import path (late import)."""
    return _get_cls(config_cls_path)


def create_storage_client_cls(storage_cls_path: str) -> t.Type[Storage]:
    """Return the storage class for an import path (late import)."""
    return _get_cls(storage_cls_path)


@cached
def _get_cls(cls_path: str):
    """Return the class for an import path (late import)."""
    module_path, cls_name = cls_path.rsplit(".", maxsplit=1)
    try:
        module = importlib.import_module(module_path, cls_name)
        storage_cls = getattr(module, cls_name)
    except (ImportError, AttributeError) as exc:
        msg = f"Cannot import class {cls_path} ({exc})"
        raise ValueError(msg) from exc
    return storage_cls
