"""Storage base module defining the abstract config and client interfaces."""
import shutil
import typing as t
from abc import ABC, abstractmethod
from functools import cached_property
from pathlib import Path

import fw_utils  # TODO minimize/phase out usage
from pydantic import BaseModel, Field, SecretStr
from pydantic.generics import GenericModel

from .. import filters  # TODO phase out usage
from . import errors

Mode = t.Literal["r", "w"]
AnyPath = t.Union[str, Path, "Item"]
ConfigT = t.TypeVar("ConfigT", bound="Config")
CloudConfigT = t.TypeVar("CloudConfigT", bound="CloudConfig")
ItemT = t.TypeVar("ItemT", bound="Item")
FileT = t.TypeVar("FileT", bound="File")
StorageT = t.TypeVar("StorageT", bound="Storage")


class Config(ABC, GenericModel, t.Generic[ConfigT]):
    """Storage config interface."""

    class Config:
        """Forbid extra attrs and allow using cached_property on models."""

        # fail fast on unexpected input (eg. unknown URL query params)
        extra = "forbid"

        # tell pydantic to leave cached_property alone
        # https://github.com/pydantic/pydantic/issues/1241#issuecomment-587896750
        arbitrary_types_allowed = True
        keep_untouched = (cached_property,)

    def dict(self, reveal: t.Optional[bool] = None, **kw) -> dict:
        """Return model as a dict, w/o defaults and optionally revealed secrets.

        Args:
            reveal: Set to True to reveal secret values, or False to mask them.
            **kw: Keyword arguments passed to pydantic.BaseModel.dict().
        """
        kw.setdefault("exclude_none", True)
        kw.setdefault("exclude_unset", True)
        kw.setdefault("exclude_defaults", True)
        if reveal is None:
            secret = kw.pop("secret", None)
            reveal = secret == "val" if secret else None  # noqa: S105
        data = super().dict(**kw)
        for key, val in data.items():
            if reveal is not None and isinstance(val, SecretStr):  # pragma: no cover
                data[key] = val.get_secret_value() if reveal else str(val)
        return data

    @classmethod
    @abstractmethod
    def from_url(cls: t.Type[ConfigT], url: str) -> ConfigT:
        """Return storage config from a URL."""

    @abstractmethod
    def to_url(self, params: bool = False) -> str:
        """Return storage URL string.

        Args:
            params: Set to True to include auth/query params in the URL, if any.
        """

    @abstractmethod
    def create_client(self) -> "Storage":
        """Return storage client from this config."""

    def __str__(self) -> str:
        """Return string representation."""
        return f"{type(self).__name__}({self.to_url()!r})"

    # STORAGE CONFIG INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)

    @property
    def safe_url(self) -> str:
        """Backwards compatibility only."""
        return self.to_url()

    @property
    def full_url(self) -> str:
        """Backwards compatibility only."""
        return self.to_url(params=True)

    def apply_override(self, override) -> None:
        """Backwards compatibility only."""
        properties = self.schema()["properties"]
        for key, value in override.dict(exclude_unset=True).items():
            assert key in properties
            setattr(self, key, value)


class Item(BaseModel):
    """Storage item representing an individual file/blob/etc."""

    path: str

    def __str__(self) -> str:
        """Return string representation."""
        return self.path

    # STORAGE FILEINFO INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)

    def asdict(self) -> dict:
        """Backwards compatibility only."""
        return self.dict()  # pragma: no cover


class Storage(ABC, t.Generic[ConfigT, ItemT]):
    """Storage client interface."""

    @abstractmethod
    def __init__(self, config: ConfigT) -> None:
        """Init storage client with config."""
        self.config = config  # pragma: no cover

    @abstractmethod
    def relpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return relative item path, stripping any path prefix."""

    @abstractmethod
    def abspath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return absolute item path, including any path prefix."""

    def urlpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return fully qualified item path, including the storage URL."""
        urlpath = self.config.to_url()
        relpath = self.relpath(path)
        if relpath and not urlpath.endswith("/"):
            urlpath += "/"
        return f"{urlpath}{relpath}"

    @abstractmethod
    def ls(  # noqa: D417
        self,
        path: t.Optional[AnyPath] = None,
        filt: t.Optional[t.Callable[[ItemT], bool]] = None,
        **kw,
    ) -> t.Iterator[ItemT]:
        """Yield sorted storage items, optionally filtered.

        Args:
            path: Path prefix to yield items from.
            filt: Callback to filter items with.
        """

    @abstractmethod
    def stat(self, path: AnyPath) -> ItemT:
        """Return a storage item from an str or Path."""

    @abstractmethod
    def open(self, path: AnyPath, mode: Mode = "r") -> t.BinaryIO:
        """Return an item opened for reading or writing."""

    @abstractmethod
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove an item from the storage.

        Args:
            path: Storage item path to remove / delete.
            recurse: Set to True remove all items with the given prefix.
                Required when deleting fs:// directories, for example.
        """

    @abstractmethod
    def test(self, mode: Mode = "r") -> None:
        """Test whether the storage can be read/written and raise if not.

        Args:
            mode: Set to "w" to check write/rm perms in addition to ls/read.
        """

    def cleanup(self) -> None:
        """Run any cleanup steps."""

    def __enter__(self: StorageT) -> StorageT:
        """Enter context to enable auto-cleanup on exit."""
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Run any cleanup steps upon exiting the context."""
        self.cleanup()

    def __del__(self) -> None:
        """Run any cleanup steps when garbage-collected."""
        self.cleanup()

    def __str__(self) -> str:
        """Return string representation."""
        return f"{type(self).__name__}({self.config.to_url()!r})"

    # STORAGE INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)
    # TODO consider ditching fw_utils / BinFile / metapath

    def fullpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Backwards compatibility only."""
        return self.urlpath(path)

    def test_read(self):
        """Backwards compatibility only."""
        self.test()

    def test_write(self):
        """Backwards compatibility only."""
        self.test(mode="w")

    @staticmethod
    def ls_filt_compat(kw: dict) -> t.Optional[t.Callable]:
        """Backwards compatibility only."""
        include = kw.get("include", None)
        exclude = kw.get("exclude", None)
        if not include and not exclude:
            return None
        # TODO deprecation warning (when most of future is implemented)
        return filters.StorageFilter(include=include, exclude=exclude).match

    def get(self, path: AnyPath):
        """Backwards compatibility only."""
        return fw_utils.BinFile(self.open(path), metapath=self.relpath(path))

    def set(self, path: AnyPath, file):
        """Backwards compatibility only."""
        with fw_utils.open_any(file) as rf, self.open(path, mode="w") as wf:
            shutil.copyfileobj(rf, wf)


class File(Item):
    """File item with common attrs of files or blobs."""

    size: int
    ctime: t.Union[int, float, None]
    mtime: t.Union[int, float, None]
    hash: str

    @property
    def dir(self) -> str:
        """Return the directory name of this path."""
        dirname = str(Path(self.path).parent)
        return "" if dirname == "." else dirname

    @property
    def name(self) -> str:
        """Return the base filename of this path."""
        return Path(self.path).name

    @property
    def stem(self) -> str:
        """Return the filename stem without any extension suffix."""
        return Path(self.path).stem

    @property
    def ext(self) -> str:
        """Return the extension of this path."""
        return Path(self.path).suffix.lstrip(".")

    # STORAGE ITEM (OLD FILEINFO) INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)

    @property
    def created(self):
        """Backwards compatibility only."""
        return self.ctime

    @property
    def modified(self):
        """Backwards compatibility only."""
        return self.mtime


class FileStorage(Storage, t.Generic[FileT]):
    """File storage client interface w/ extended item and implementing test()."""

    @abstractmethod
    def stat(self, path: AnyPath) -> FileT:
        """Return a storage item from an str or Path."""

    def test(self, mode: Mode = "r") -> None:
        """Test whether the storage can be read/written and raise if not.

        Args:
            mode: Set to "w" to check write/rm perms in addition to ls/read.
        """
        # test open("w") and write() if mode=w
        fw_test = "fw-test"
        if mode == "w":
            with self.open(fw_test, mode="w") as file:
                file.write(fw_test.encode("ascii"))
        # test ls() then stat() the first item
        item: t.Any = None
        for item in self.ls():
            item = self.stat(item)
            break
        else:
            # for/else: no items found - if "w", we expect the test file
            if mode == "w":  # pragma: no cover
                raise errors.StorageError(f"ls() did not yield {fw_test!r}")
        # test open("r") and read() a single byte (whole file could be BIG)
        # use the test file if "w", or the 1st ls() yield if available
        item = fw_test if mode == "w" else item
        if item:
            with self.open(item) as file:
                file.read(1)
        # test rm() on the test file if mode=w
        if mode == "w":
            self.rm(fw_test)
            self.cleanup()


class CloudConfig(Config):
    """Cloud storage config interface w/ rm_batch_max."""

    rm_batch_max: t.Optional[int] = Field(
        100,
        title="Max no. of blobs to delete in a single bulk operation.",
        min=1,
        max=1000,
    )


class CloudStorage(FileStorage, t.Generic[CloudConfigT]):  # pragma: no cover
    """Cloud storage client interface defining rm_bulk() / implementing rm()."""

    @abstractmethod
    def __init__(self, config: CloudConfigT) -> None:
        """Init cloud storage client with config and an empty rm_keys."""
        self.config = config
        self.rm_keys: t.List[str] = []

    @abstractmethod
    def rm_bulk(self) -> None:
        """Remove all blobs in rm_keys with a bulk operation."""

    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Mark blob path to be removed in a bulk operation later."""
        if recurse:
            for item in self.ls(path):
                self.rm(item)
        else:
            self.rm_keys.append(self.abspath(path))
            if len(self.rm_keys) >= self.config.rm_batch_max:
                self.rm_bulk()
                self.rm_keys.clear()

    def cleanup(self) -> None:
        """Run bulk delete operation if any blobs are marked for removal."""
        if self.rm_keys:
            self.rm_bulk()
            self.rm_keys.clear()
