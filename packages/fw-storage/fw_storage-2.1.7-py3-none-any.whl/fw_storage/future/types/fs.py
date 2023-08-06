"""FS / local file-system storage."""
import hashlib
import os
import re
import shutil
import typing as t
from functools import cached_property
from pathlib import Path

from pydantic import BaseModel, Field, root_validator, validator

from .. import errors, utils
from ..base import AnyPath, Config, File, FileStorage, Mode

ERRMAP: dict = {
    FileExistsError: errors.FileExists,
    FileNotFoundError: errors.FileNotFound,
    IsADirectoryError: errors.IsADirectory,
    NotADirectoryError: errors.NotADirectory,
    PermissionError: errors.PermError,
    OSError: errors.StorageError,
}

errmap = errors.ErrorMapper(ERRMAP)
UnixId = t.Union[int, str]


class Compat(BaseModel):
    """Backwards-compatibility mixin for FSConfig and FSConfigOverride."""

    @root_validator(pre=True)
    @classmethod
    def compat(cls, values: dict) -> dict:
        """Map modified config field names/values for backwards-compatibility."""
        if not values.get("chown"):
            user = values.pop("user", None)
            uid, gid = values.pop("uid", None), values.pop("gid", None)
            if user or uid:
                # TODO deprecation warning (when most of future is implemented)
                pass
            if user:
                values["chown"] = user
            elif uid:
                values["chown"] = f"{uid}:{gid}" if gid else str(uid)
        return values

    @property
    def user(self) -> t.Optional[str]:
        """Alias for accessing 'chown' field for backwards-compatibility."""
        return getattr(self, "chown", None)


class FSConfig(Config, Compat):
    """FS / local file-system storage config."""

    type: t.Literal["fs"] = Field("fs", title="FS storage type")
    path: str = Field(title="FS directory path", example="/mnt/data")
    cleanup_dirs: bool = Field(False, title="Remove empty directories on cleanup")
    content_hash: bool = Field(False, title="Calculate content-hash for files (md5)")
    follow_links: bool = Field(False, title="Follow symbolic links when walking dirs")
    chown: t.Optional[str] = Field(
        title="Unix user[:group] id/name to chown to when writing files",
        examples=["user", "user:group", "1000:1000"],
        regex=r"^[a-z0-9-]+(:[a-z0-9-]+)?$",
    )
    chmod: t.Optional[str] = Field(
        title="Unix file permissions to chmod to when writing files",
        examples=["664", "rw-rw-r--"],
        regex=r"^[0-7]{3}|([r-][w-][x-]){3}$",
    )

    @classmethod
    def from_url(cls, url: str) -> "FSConfig":
        """Return FS storage config parsed from the given storage URL."""
        parsed = utils.URL.from_string(url).dict()
        config = {
            "type": parsed.pop("scheme"),
            "path": f"{parsed.pop('host', '')}{parsed.pop('path', '')}",
            "cleanup_dirs": parsed.pop("cleanup_dirs", None),
            "content_hash": parsed.pop("content_hash", None),
            "follow_links": parsed.pop("follow_links", None),
            "chown": parsed.pop("chown", None),
            "chmod": parsed.pop("chmod", None),
        }
        config.update(parsed)
        return cls(**utils.filter_none(config))

    def to_url(self, params: bool = False) -> str:
        """Return FS storage URL, optionally including all parameters."""
        parsed: dict = {"scheme": self.type, "path": self.path}
        if params:
            config = self.dict()
            extras = ["cleanup_dirs", "content_hash", "follow_links", "chown", "chmod"]
            parsed["query"] = {key: config.get(key) for key in extras}
        return str(utils.URL(**parsed))

    def create_client(self) -> "FSStorage":
        """Return FS storage client from this config."""
        return FSStorage(self)

    @validator("path")
    @classmethod
    def canonize_path(cls, path: str) -> str:
        """Return absolute path, resolving any ~ refs and symlinks."""
        return str(Path(path).expanduser().resolve())

    @validator("chmod")
    @classmethod
    def canonize_chmod(cls, chmod: t.Optional[str]) -> t.Optional[str]:
        """Return file permissions in canonized, octal form if given."""
        if not chmod:
            return None  # pragma: no cover
        if not chmod.isdigit():
            chmod = "".join(["0" if c == "-" else "1" for c in chmod])
            chmod = "".join([str(int(chmod[i : i + 3], base=2)) for i in (0, 3, 6)])
        assert all(c in "046" for c in chmod)  # limit to nil/ro/rw
        return chmod

    @cached_property
    def owner(self) -> t.Optional[t.Tuple[UnixId, t.Optional[UnixId]]]:
        """Return unix user & group as needed for shutil.chown."""
        if self.chown is None:
            return None  # pragma: no cover
        user: UnixId
        group: UnixId
        user, _, group = self.chown.partition(":")
        user = int(user) if user.isdigit() else user
        group = int(group) if group.isdigit() else group
        return user, group or None

    @cached_property
    def file_perms(self) -> t.Optional[int]:
        """Return unix file permissions as needed for pathlib.Path.chmod."""
        return int(self.chmod, base=8) if self.chmod else None

    @cached_property
    def dir_perms(self) -> t.Optional[int]:
        """Return unix dir permissions as needed for pathlib.Path.chmod."""
        # add +x (required for ls) for user/group/all if +r(4->5) or +rw(6->7)
        table = str.maketrans({"4": "5", "6": "7"})
        return int(self.chmod.translate(table), base=8) if self.chmod else None


CopyField = utils.copy_field_func(FSConfig)


class FSConfigOverride(Compat):
    """FS / local file-system storage config runtime overrides."""

    type: t.Literal["fs"] = CopyField("type")
    cleanup_dirs: bool = CopyField("cleanup_dirs")
    content_hash: bool = CopyField("content_hash")
    follow_links: bool = CopyField("follow_links")
    chown: t.Optional[str] = CopyField("chown")
    chmod: t.Optional[str] = CopyField("chmod")


class FSStorage(FileStorage):
    """FS / local file-system storage client."""

    def __init__(self, config: FSConfig) -> None:
        """Init FS / local file-system storage from a config."""
        self.config = config
        path = Path(config.path)
        if not path.exists():
            raise errors.StorageError(f"path doesn't exist: {path}")
        if not path.is_dir():
            raise errors.NotADirectory(f"path is not a dir: {path}")
        if config.chown and os.geteuid() != 0:
            raise errors.StorageError(f"root required for chown: {config.chown}")

    def relpath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return relative file path, excluding the storage path."""
        root = Path(self.config.path)
        path = Path(str(path or ""))
        relpath = Path(re.sub(rf"^{root}/?", "", str(path)))
        return "" if str(relpath) == "." else str(relpath)

    def abspath(self, path: t.Optional[AnyPath] = None) -> str:
        """Return absolute file path, including the storage path."""
        return str(Path(self.config.path) / self.relpath(path))

    @errmap
    def ls(  # noqa: D417, PLR0913
        self,
        path: t.Optional[AnyPath] = None,
        filt: t.Optional[t.Callable[[File], bool]] = None,
        filt_dir: t.Optional[t.Callable[[str], bool]] = None,
        filt_file: t.Optional[t.Callable[[str], bool]] = None,
        follow_links: t.Optional[bool] = None,
        **kw,
    ) -> t.Iterator[File]:
        """Yield sorted files, optionally filtered.

        Args:
            path: Path prefix / subdir to yield files from.
            filt: File filter callback for including/exluding by path, size, etc.
            filt_dir: Dirname filter callback for pruning the walk tree.
            filt_file: Filename filter callback for skipping stat() calls.
            follow_links: Set to True to follow symbolic links.
        """
        top = self.abspath(path)
        filt = filt or self.ls_filt_compat(kw) or utils.true
        # TODO before 1st usage in prod, consider adding to super() interface
        filt_dir = filt_dir or utils.true
        filt_file = filt_file or utils.true
        links = follow_links if follow_links is not None else self.config.follow_links
        rel_dirs: t.List[str] = []
        rel_files: t.List[str] = []
        for root, dirs, files in os.walk(top, followlinks=links, onerror=onerr):

            def rel(name):
                return self.relpath(f"{root}/{name}")

            # pop first dir from the buffer (should be the root)
            assert not rel_dirs or rel_dirs.pop(0) == rel("")
            # apply the dir filters to prune the walk tree for efficiency
            # also sort dirs to enforce deterministic walk order
            dirs[:] = [d for d in sorted(dirs) if filt_dir(d)]
            rel_dirs.extend([rel(d) for d in dirs])
            rel_dirs.sort()
            # apply the path-based filters before using os.stat for efficiency
            files = [f for f in sorted(files) if filt_file(f)]
            rel_files.extend([rel(f) for f in files])
            rel_files.sort()
            # use sorted dir and file buffers to yield in total order
            # ie. stop yielding if a sibling dir should be walked first
            while rel_files and not (rel_dirs and rel_dirs[0] < rel_files[0]):
                item = self.stat(rel_files.pop(0))
                if filt(item):
                    yield item

    @errmap
    def stat(self, path: AnyPath) -> File:
        """Return file stat from an str or Path."""
        path = Path(self.abspath(path))
        stat = path.stat()
        return File(
            path=self.relpath(path),
            size=stat.st_size,
            ctime=stat.st_ctime,
            mtime=stat.st_mtime,
            hash=md5sum(path, stat, self.config.content_hash),
        )

    @errmap
    def open(self, path: AnyPath, mode: Mode = "r") -> t.BinaryIO:
        """Return a file opened for reading or writing."""
        path = Path(self.abspath(path))
        if mode == "w":
            parent = path.parent
            missing: t.List[Path] = []
            while not parent.exists():
                missing.append(parent)
                parent = parent.parent
            if not parent.is_dir():
                raise errors.NotADirectory(f"Not a directory: '{parent}'")
            for parent in reversed(missing):
                parent.mkdir(exist_ok=True)
                if self.config.chmod:
                    parent.chmod(self.config.dir_perms)
                if self.config.chown:
                    shutil.chown(parent, *self.config.owner)
            path.touch()
            if self.config.chmod:
                path.chmod(self.config.file_perms)
            if self.config.chown:
                shutil.chown(path, *self.config.owner)

        file = path.open(mode=f"{mode}b")
        return t.cast(t.BinaryIO, file)

    @errmap
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove a file at the given path."""
        path = Path(self.abspath(path))
        if not path.is_dir():
            path.unlink()
        elif recurse:
            shutil.rmtree(path)
        else:
            raise errors.IsADirectory(f"cannot remove dir w/o recurse=True: {path!r}")

    @errmap
    def rm_empty_dirs(self):
        """Remove empty directories recursivey, bottom-up."""
        top = self.config.path
        deleted = set()
        for root, dirs, files in os.walk(top, topdown=False, onerror=onerr):
            if root == top:
                break
            dirs.sort()
            if not files and all(f"{root}/{d}" in deleted for d in dirs):
                os.rmdir(root)
                deleted.add(root)

    def cleanup(self) -> None:
        """Remove empty directories if enabled on the config."""
        if self.config.cleanup_dirs:
            self.rm_empty_dirs()

    # STORAGE INTERFACE BACKWARDS COMPATIBILITY
    # TODO deprecation warning (when most of future is implemented)

    @property
    def prefix(self) -> Path:
        """Backwards compatibility only."""
        return Path(self.config.path)


def onerr(exc: OSError):
    """Walk error callback to raise exceptions instead of swallowing them."""
    raise exc  # pragma: no cover


def md5sum(
    path: AnyPath,
    stat: os.stat_result,
    content_hash: bool = False,
    block_size: int = 2**20,
) -> str:
    """Return the first 32 chars of the file's MD5 content-hash."""
    md5 = hashlib.md5()  # noqa: S324
    if content_hash:
        with open(str(path), mode="rb") as file:
            while data := file.read(block_size):
                md5.update(data)
    else:
        md5.update(f"{path}{stat.st_size}{stat.st_mtime}".encode("utf8"))
    return md5.hexdigest()[:32]
