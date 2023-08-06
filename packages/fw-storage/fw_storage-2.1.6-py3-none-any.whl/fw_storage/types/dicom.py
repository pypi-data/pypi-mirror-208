"""DICOM storage module."""
import abc
import re
import tempfile
import typing as t
from datetime import datetime, timezone
from pathlib import Path

import pydicom
from fw_file.dicom.utils import get_timestamp
from fw_utils import Filters, fileglob
from pydicom.dataset import Dataset, FileMetaDataset
from pynetdicom import AE, StoragePresentationContexts, build_role, evt, sop_class

from ..config import DICOMConfig
from ..fileinfo import FileInfo
from ..storage import AnyPath, Storage

__all__ = ["DICOMStorage"]

PENDING = {0xFF00, 0xFF01}
SUCCESS = 0x0000


STUDY_FIND = sop_class.StudyRootQueryRetrieveInformationModelFind
STUDY_GET = sop_class.StudyRootQueryRetrieveInformationModelGet
STUDY_MOVE = sop_class.StudyRootQueryRetrieveInformationModelMove
# pylint: enable=no-member


class DICOMBase(Storage):
    """Base class for DICOM storages."""

    def abspath(self, path: AnyPath) -> str:
        """Return absolute path for a given path."""
        return str(path)

    @abc.abstractmethod
    def stat(self, path: AnyPath) -> FileInfo:
        """Return FileInfo for a single file."""

    @abc.abstractmethod
    def get(self, path: AnyPath, **kwargs) -> AnyPath:  # type: ignore
        """Return path to downloaded series."""

    @abc.abstractmethod
    def set(self, file: AnyPath) -> None:  # type: ignore
        """Write a file at the given path in storage."""

    @abc.abstractmethod
    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove file from storage."""

    def result_to_fileinfo(self, ds: Dataset) -> FileInfo:
        """Fills the FileInfo from a dict."""
        study_uid = ds.StudyInstanceUID
        series_uid = ds.SeriesInstanceUID
        self.correct_image_count(ds)
        size = ds.get("NumberOfSeriesRelatedInstances", 0)
        dt = get_timestamp(t.cast(dict, ds), "Series")
        if dt:
            timestamp = dt.replace(tzinfo=timezone.utc).timestamp()
        else:
            timestamp = datetime.utcnow().timestamp()
        return FileInfo(
            path=f"{study_uid}/{series_uid}",
            size=size,
            hash=None,  # TODO figure out what to use
            created=timestamp,
            modified=timestamp,
        )

    def correct_image_count(self, ds: Dataset) -> None:
        """Correct image count of Dataset.

        Only tries to correct if NumberOfSeriesRelatedInstances not present or zero.
        """
        if not ds.get("NumberOfSeriesRelatedInstances"):
            count = self.get_image_count(ds.StudyInstanceUID, ds.SeriesInstanceUID)
            ds.NumberOfSeriesRelatedInstances = count

    @abc.abstractmethod
    def get_image_count(self, study_uid: str, series_uid: str) -> int:
        """Get image count of a series."""


def parse_path(
    path: AnyPath, required_parts: int = 0
) -> t.Tuple[t.Optional[str], t.Optional[str]]:
    """Parse DICOM study/series 'UID path' and return as a tuple."""
    path_str = str(path)
    uid_re = r"\d+(\.\d+)*"
    assert 0 <= required_parts <= 2
    if not required_parts:
        path_re = rf"^((?P<study>{uid_re})(/(?P<series>{uid_re}))?)?$"
    elif required_parts == 1:
        path_re = rf"^(?P<study>{uid_re})(/(?P<series>{uid_re}))?$"
    elif required_parts == 2:
        path_re = rf"^(?P<study>{uid_re})/(?P<series>{uid_re})$"
    match = re.match(path_re, path_str)
    if match:
        return match.group("study"), match.group("series")
    raise ValueError(f"Invalid DICOM study/series UID path: {path}")


def parse_filters_to_dict(filters: t.List[str]) -> t.Dict[str, str]:
    """Parse list of strings into filter dict."""
    filt_dict = {}
    for filt in filters:
        try:
            key, value = filt.split("=", maxsplit=1)
            param_to_tag(key)  # raises on invalid keys
            filt_dict[key] = value
        except ValueError as exc:
            raise ValueError("Missing filter key or value") from exc
    return filt_dict


def parse_filters_to_ds(filters: t.List[str], ds: Dataset) -> None:
    """Parse list of strings into Dataset filters."""
    for filt in filters:
        try:
            key, value = filt.split("=", maxsplit=1)
            if "," in value:
                setattr(ds, key, value.split(","))
            else:
                setattr(ds, key, value)
        except ValueError as exc:
            raise ValueError("Missing filter key or value") from exc


def apply_exclude_filters(ds: Dataset, filters: t.Dict[str, str]) -> bool:
    """Apply exclude filters on dataset."""
    for key, value in filters.items():
        field = ds.get(int(param_to_tag(key), 16))
        if field is None:
            continue
        if field.VR in ("DA", "TM"):
            if "-" in value:
                minimum, maximum = value.split("-")
                if minimum and minimum <= field.value:
                    if not maximum:
                        return True
                    if field.value <= maximum:
                        return True
        elif field.VR == "UI":
            if "," in value:
                if field.value in value.split(","):
                    return True
        if field.value == value:
            return True
    return False


def param_to_tag(param: str) -> str:
    """Get DICOM tag string for query param."""
    if param in pydicom.datadict.keyword_dict:
        tag = f"{pydicom.datadict.tag_for_keyword(param):08x}"
    else:
        tag = param
    pydicom.datadict.keyword_for_tag(tag)
    return tag


class DICOMStorage(DICOMBase):
    """Storage class for medical imaging."""

    def __init__(self, config: DICOMConfig) -> None:
        """Construct DICOM storage.

        Args:
            config: DICOMConfig
        """
        self.config = config
        self.ae = AE(ae_title=self.config.aet.encode())
        # Add required contexts for operations
        contexts = [STUDY_FIND, STUDY_GET, STUDY_MOVE]
        for cx in contexts:
            self.ae.add_requested_context(cx)

        for cx in StoragePresentationContexts:
            if len(self.ae.requested_contexts) == 128:
                break
            self.ae.add_requested_context(cx.abstract_syntax)

        # Both scu and scp roles needs to be set to True so most C service can be
        # supported. Most C services require SCU role for successful association.
        # C-GET requires to act as an SCP to handle responses.
        roles = [
            build_role(cx.abstract_syntax, scp_role=True, scu_role=True)
            for cx in StoragePresentationContexts
        ]

        self.rport = int(self.config.rport) if self.config.rport else None
        self.storage_scp = None
        self.assoc = self.ae.associate(
            self.config.host,
            int(self.config.port),
            ae_title=self.config.aec or b"ANY-SCP",
            ext_neg=roles,
            evt_handlers=handlers,
        )

    def fullpath(self, path: AnyPath) -> str:  # pragma: no cover
        """Return absolute path string including the storage URL."""
        return f"dicom://{self.config.host}:{self.config.port}/{self.config.aec}/{path}"

    def start_storage_scp(self):
        """Start Storage SCP to handle C-MOVE responses."""
        if not self.rport:
            msg = "Initiate DICOM Storage with DICOM url that includes return port"
            raise ValueError(msg)
        # Initialise the Application Entity
        ae = AE()

        # Add a requested presentation context
        ae.add_requested_context(STUDY_MOVE)

        # Add the Storage SCP's supported presentation contexts
        ae.supported_contexts = StoragePresentationContexts
        # Start our Storage SCP in non-blocking mode, listening on port self,rport
        ae.ae_title = self.ae.ae_title
        self.storage_scp = ae.start_server(
            ("", self.rport), block=False, evt_handlers=handlers
        )

    def ls(
        self,
        path: AnyPath = "",
        *,
        include: Filters = None,
        exclude: Filters = None,
        **_,
    ) -> t.Iterator[FileInfo]:
        """Yield items under path that match the include/exclude filters."""
        ds = Dataset()
        ds.QueryRetrieveLevel = "SERIES"
        ds.SeriesInstanceUID = None
        ds.SeriesDate = None
        ds.SeriesTime = None
        ds.NumberOfSeriesRelatedInstances = None
        study_uid, series_uid = parse_path(path, required_parts=0)
        if include:
            parse_filters_to_ds(include, ds)
        exc_filters = {}
        if exclude:
            exc_filters = parse_filters_to_dict(exclude)
            for key in exc_filters:
                setattr(ds, key, None)
        study_uids = [study_uid] if study_uid else self._get_every_study_uid()
        # TODO: Series level ls might be unnecessary, see stat method
        if series_uid:
            ds.SeriesInstanceUID = series_uid
        ds.StudyInstanceUID = study_uids
        responses = self.assoc.send_c_find(ds, STUDY_FIND)
        for resp in iter_scp_responses(responses, exc_filters):
            yield self.result_to_fileinfo(resp)

    def stat(self, path: AnyPath) -> FileInfo:
        """Return FileInfo for a single series."""
        study_uid, series_uid = parse_path(path, required_parts=2)
        ds = Dataset()
        ds.QueryRetrieveLevel = "SERIES"
        ds.SeriesInstanceUID = None
        ds.SeriesDate = None
        ds.SeriesTime = None
        ds.NumberOfSeriesRelatedInstances = None
        ds.SeriesInstanceUID = series_uid
        ds.StudyInstanceUID = study_uid
        responses = self.assoc.send_c_find(ds, STUDY_FIND)
        results = list(iter_scp_responses(responses))
        if len(results) == 1:
            return self.result_to_fileinfo(results[0])
        raise ValueError("Ambiguous resource or resource not found")

    def get(self, path: AnyPath, **kwargs) -> AnyPath:  # type: ignore
        """Return path to downloaded series."""
        study_uid, series_uid = parse_path(path, required_parts=2)
        ds = Dataset()
        ds.QueryRetrieveLevel = "SERIES"
        ds.StudyInstanceUID = study_uid
        ds.SeriesInstanceUID = series_uid

        tmp = Path(tempfile.gettempdir()) / self.abspath(path)
        tmp.mkdir(parents=True, exist_ok=True)
        try:
            list(iter_scp_responses(self.assoc.send_c_get(ds, STUDY_GET)))
        except ValueError:
            self.start_storage_scp()
            responses = self.assoc.send_c_move(ds, self.ae.ae_title, STUDY_MOVE)
            list(iter_scp_responses(responses))
        return str(tmp)

    def set(self, file: AnyPath) -> None:  # type: ignore
        """Write a file at the given path in storage."""
        path = Path(self.abspath(file))
        paths = fileglob(path) if path.is_dir() else [path]
        for path in paths:
            ds = pydicom.dcmread(path)
            self.assoc.send_c_store(ds)

    def rm(self, path: AnyPath, recurse: bool = False) -> None:
        """Remove file from storage."""
        raise NotImplementedError

    def get_image_count(self, study_uid: str, series_uid: str) -> int:
        """Get image count of a series."""
        query_ds = Dataset()
        query_ds.QueryRetrieveLevel = "IMAGE"
        query_ds.StudyInstanceUID = study_uid
        query_ds.SeriesInstanceUID = series_uid
        query_ds.SOPInstanceUID = ""
        responses = self.assoc.send_c_find(query_ds, STUDY_FIND)
        return len(list(iter_scp_responses(responses)))

    def _get_every_study_uid(self):
        """Get every study uid."""
        study_uids = []
        study_ds = Dataset()
        study_ds.QueryRetrieveLevel = "STUDY"
        study_ds.StudyInstanceUID = None
        for resp in iter_scp_responses(self.assoc.send_c_find(study_ds, STUDY_FIND)):
            study_uids.append(resp.StudyInstanceUID)
        return study_uids

    def cleanup(self):
        """Stop storage_scp if running and abort association."""
        if self.storage_scp:
            self.storage_scp.server_close()
            self.storage_scp = None
        if not self.assoc.is_aborted:
            self.assoc.abort()


def handle_store(event):
    """Handle a C-STORE request event."""
    ds = event.dataset
    ds.file_meta = FileMetaDataset(event.file_meta)

    tmp = (
        Path(tempfile.gettempdir())
        / str(ds.StudyInstanceUID)
        / str(ds.SeriesInstanceUID)
    )
    tmp.mkdir(parents=True, exist_ok=True)
    # Save the dataset using the SOP Instance UID as the filename
    ds.save_as(f"{tmp}/{ds.SOPInstanceUID}.dcm", write_like_original=False)

    # Return a 'Success' status
    return SUCCESS


handlers = [(evt.EVT_C_STORE, handle_store)]


def iter_scp_responses(
    responses: t.Iterator[t.Tuple[Dataset, Dataset]],
    exc_filters: dict = None,
) -> t.Iterator[Dataset]:
    """Process responses sent by the SCP."""
    for status, identifier in responses:
        if not status:
            msg = "Connection error: timed out, aborted or received invalid response"
            raise ValueError(msg)
        if status.Status in PENDING:
            if exc_filters:
                if apply_exclude_filters(identifier, exc_filters):
                    continue
            yield identifier
        elif status.Status == SUCCESS:
            return
        else:
            raise ValueError(f"An error occured (DIMSE status: {status})")
