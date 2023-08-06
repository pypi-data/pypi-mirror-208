"""Storage configuration models."""
# TODO fw-storage
# - utilize configs for parsing/loading/validation in factory and storage classes
# - update readme with clarified, explicit creds handling
# TODO xfer
# - drop .env support and rename fs.uid->user / gs.sv_acct->app_creds
# - utilize configs for parsing/validation
import abc
import json
import os
import re
import typing as t
from pathlib import Path

from fw_http_client import AnyAuth
from fw_utils import format_query_string as qs
from fw_utils import format_url, parse_url
from pydantic import BaseModel, Field, SecretStr, root_validator, validator

from .future.types.fs import FSConfig, FSConfigOverride

LOAD_ENV = True  # load creds from envvars (and read file for gs)
REQUIRE_CREDS = True  # raise on missing creds (s3/gs/az)


class StorageConfig(BaseModel, abc.ABC):
    """Storage config model with URL <-> CFG conversion interface."""

    @classmethod
    @abc.abstractmethod
    def from_url(cls, url: str) -> "StorageConfig":
        """Return storage config parsed from a URL."""

    @property
    @abc.abstractmethod
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""

    @property
    @abc.abstractmethod
    def full_url(self) -> str:
        """Return full storage URL including credentials and options."""

    def dict(self, secret: t.Literal[None, "str", "val"] = None, **kwargs) -> dict:
        """Return model as dictionary with optional secret serialization."""
        data = super().dict(**kwargs)
        for key, value in data.items():
            if isinstance(value, SecretStr):
                if secret == "str":  # noqa, serialize as **
                    data[key] = str(value)  # pragma: no cover
                if secret == "val":  # noqa, serialize as val, noqa
                    data[key] = value.get_secret_value()
        return data

    def apply_override(self, override: "StorageConfigOverride"):
        """Apply property overrides."""
        expected_class = f"{type(self).__name__}Override"
        actual_class = type(override).__name__
        assert (
            expected_class == actual_class
        ), f"expected override of class {expected_class} but got {actual_class}"

        for key in override.schema().get("properties", {}).keys():
            value = getattr(override, key)
            if value is not None:
                setattr(self, key, value)


class StorageConfigOverride(BaseModel):
    """Storage config override model."""


class S3Config(StorageConfig):
    """Amazon S3 storage config."""

    type: t.Literal["s3"] = Field("s3", title="S3 storage type")
    bucket: str = Field(
        title="AWS S3 bucket name",
        example="s3-bucket",
        min_length=3,
        max_length=63,
        regex=r"^[a-z0-9-.]+$",
    )
    prefix: str = Field("", title="Common object key prefix", example="prefix")
    connector_creds: bool = Field(
        False, title="Use connector's pre-configured credentials"
    )
    access_key_id: t.Optional[str] = Field(
        title="AWS Access Key ID",
        example="AKIAIOSFODNN7EXAMPLE",
        min_length=16,
        max_length=128,
    )
    secret_access_key: t.Optional[SecretStr] = Field(
        title="AWS Secret Access Key",
        example="wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        min_length=40,
    )

    @classmethod
    def from_url(cls, url: str) -> "S3Config":
        """Return Amazon S3 storage config parsed from a URL."""
        parsed = parse_url(url)
        params = {
            "type": parsed.pop("scheme"),
            "bucket": parsed.pop("host"),
            "prefix": parsed.pop("path", "").strip("/"),
            "access_key_id": parsed.pop("access_key_id", None),
            "secret_access_key": parsed.pop("secret_access_key", None),
            "connector_creds": parsed.pop("connector_creds", False),
        }
        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        return format_url(scheme=self.type, host=self.bucket, path=self.prefix)

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        data = self.dict(secret="val")  # noqa: S106
        qparams = {
            "access_key_id": data["access_key_id"],
            "secret_access_key": data["secret_access_key"],
        }
        if self.connector_creds:
            qparams["connector_creds"] = True
        return self.safe_url + qs(**qparams)

    @root_validator(pre=True)
    @classmethod
    def load_creds(cls, values: dict) -> dict:
        """Load creds from the env if enabled."""
        if values.get("connector_creds"):
            # drop creds if passed
            values.pop("access_key_id", None)
            values.pop("secret_access_key", None)
            return values
        if LOAD_ENV:
            if not values.get("access_key_id"):
                values["access_key_id"] = os.getenv("AWS_ACCESS_KEY_ID")
            if not values.get("secret_access_key"):
                values["secret_access_key"] = os.getenv("AWS_SECRET_ACCESS_KEY")
        if REQUIRE_CREDS:
            assert values.get("access_key_id"), "access_key_id required"
            assert values.get("secret_access_key"), "secret_access_key required"
        return values

    strip_prefix = validator("prefix")(lambda cls, prefix: prefix.strip("/"))


class S3ConfigOverride(StorageConfigOverride):
    """Amazon S3 storage config override."""

    type: t.Literal["s3"] = Field("s3", title="S3 storage type")
    prefix: t.Optional[str] = Field(
        None, title="Common object key prefix", example="prefix"
    )


GOOGLE_SERVICE_ACCOUNT_JSON_EXAMPLE = """{
"type": "service_account",
"project_id": "project-id",
"private_key_id": "key-id",
"private_key": "-----BEGIN PRIVATE KEY-----\\nKEY\\n-----END PRIVATE KEY-----\\n",
"client_id": "client-id",
"client_email": "service-account-email",
"auth_uri": "https://accounts.google.com/o/oauth2/auth",
"token_uri": "https://accounts.google.com/o/oauth2/token",
"auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
"client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/service-account-email"
}
"""


class GSConfig(StorageConfig):
    """Google Cloud Storage config."""

    type: t.Literal["gs"] = Field("gs", title="Google Cloud Storage type")
    bucket: str = Field(
        title="Google Cloud Storage bucket name",
        example="gs-bucket",
        min_length=3,
        max_length=63,
        regex=r"^[a-z0-9-_.]+$",
    )
    prefix: str = Field("", title="Common object key prefix", example="prefix")

    application_credentials: t.Optional[SecretStr] = Field(
        title="Google Service Account Key path or contents",
        examples=[
            "~/google_service_account.json",
            GOOGLE_SERVICE_ACCOUNT_JSON_EXAMPLE,
        ],
    )

    @classmethod
    def from_url(cls, url: str) -> "GSConfig":
        """Return Google Cloud Storage config parsed from a URL."""
        parsed = parse_url(url)
        creds = parsed.pop("application_credentials", None)
        service_account_key = parsed.pop("service_account_key", None)
        if not creds:
            creds = service_account_key
        # TODO consider not splitting qparams on commas when parsing
        # TODO consider urlsafe_b64en/decode
        creds = ",".join(creds) if isinstance(creds, list) else creds
        params = {
            "type": parsed.pop("scheme"),
            "bucket": parsed.pop("host"),
            "prefix": parsed.pop("path", "").strip("/"),
            "application_credentials": creds,
        }
        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        return format_url(scheme=self.type, host=self.bucket, path=self.prefix)

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        creds = self.dict(secret="val")["application_credentials"]  # noqa: S106
        return self.safe_url + qs(application_credentials=creds)

    @validator("application_credentials", always=True)
    @classmethod
    def load_creds(
        cls, application_credentials: t.Optional[SecretStr]
    ) -> t.Optional[SecretStr]:
        """Return creds read from disk if provided as a file path."""
        creds = ""
        if isinstance(application_credentials, SecretStr):
            creds = application_credentials.get_secret_value()
        if LOAD_ENV and not creds:
            creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS") or ""
        if REQUIRE_CREDS:
            assert creds, "application_credentials required"
        # TODO consider using a try/except flow instead
        if LOAD_ENV and creds and not creds.strip().startswith("{"):  # json test
            creds = Path(creds).expanduser().read_text(encoding="utf8")
        # creds are now the portable json contents - run some checks
        if creds:
            creds_obj = json.loads(creds)
            assert isinstance(creds_obj, dict), "invalid gs credentials (not a dict)"
            assert "type" in creds_obj, "invalid gs credentials (missing type)"
        return SecretStr(creds) if creds else None

    strip_prefix = validator("prefix")(lambda cls, prefix: prefix.strip("/"))


class GSConfigOverride(StorageConfigOverride):
    """Google Cloud Storage config override."""

    type: t.Literal["gs"] = Field("gs", title="Google Cloud Storage type")
    prefix: t.Optional[str] = Field(
        None, title="Common object key prefix", example="prefix"
    )


AZ_BLOB_DOMAIN = "blob.core.windows.net"


class AZConfig(StorageConfig):
    """Azure Blob Storage config."""

    type: t.Literal["az"] = Field("az", title="Azure Blob Storage type")
    account: str = Field(
        title="Azure Storage Account name",
        example="azaccount",
        min_length=3,
        max_length=23 + (1 + len(AZ_BLOB_DOMAIN)),
        regex=r"^[a-z0-9]+" + re.escape(f".{AZ_BLOB_DOMAIN}") + r"$",
    )
    container: str = Field(
        title="Azure Blob Container name",
        example="container",
        min_length=3,
        max_length=63,
        regex=r"[a-z0-9-]+",
    )
    prefix: str = Field("", title="Common blob key prefix", example="prefix")

    access_key: t.Optional[SecretStr] = Field(
        title="Azure Storage Account shared Access Key",
        example=(
            "J94I0uS13Cc79AvAq33Hrkt3+C40yq16IF058yQUyiM7"
            "U2qBwGJXQ2VIrLhy0gwGRWMQ2OLTpJ6C9PsEXAMPLE=="
        ),
    )

    tenant_id: t.Optional[str] = Field(
        title="Azure tenant ID",
        example="c88032d3-19d1-4040-b9bf-b84c29a49480",
    )
    client_id: t.Optional[str] = Field(
        title="Registered application Client ID",
        example="94ade9ae-5cd7-44ad-8e18-8331e5e3328e",
    )
    client_secret: t.Optional[SecretStr] = Field(
        title="Registered application Client secret",
        example="o0O8Q~Rou2PCGn.NHGdLLneBQ4xG.fNEXAMPLE~9",
    )

    @classmethod
    def from_url(cls, url: str) -> "AZConfig":
        """Return Azure Blob Storage config parsed from a URL."""
        parsed = parse_url(url)
        path = parsed.pop("path", "").strip("/")
        if "/" in path:
            container, prefix = path.split("/", maxsplit=1)
        else:
            container, prefix = path, ""

        account = parsed.pop("host")
        params = {
            "type": parsed.pop("scheme"),
            "account": account,
            "container": container,
            "prefix": prefix,
            "access_key": parsed.pop("access_key", None),
            "tenant_id": parsed.pop("tenant_id", None),
            "client_id": parsed.pop("client_id", None),
            "client_secret": parsed.pop("client_secret", None),
        }
        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        path = f"{self.container}/{self.prefix}" if self.prefix else self.container
        return format_url(scheme=self.type, host=self.account, path=path)

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        data = self.dict(secret="val")  # noqa: S106
        return self.safe_url + qs(
            access_key=data["access_key"],
            tenant_id=data["tenant_id"],
            client_id=data["client_id"],
            client_secret=data["client_secret"],
        )

    @validator("account", pre=True)
    @classmethod
    def account_url(cls, account: str) -> str:
        """Return account name with default blob domain unless given a URL."""
        return account if "." in account else f"{account}.{AZ_BLOB_DOMAIN}"

    @root_validator(pre=True)
    @classmethod
    def load_creds(cls, values: dict) -> dict:
        """Load creds from the env if enabled."""
        if LOAD_ENV:
            if not values.get("access_key"):
                values["access_key"] = os.getenv("AZURE_ACCESS_KEY")
            if not values.get("tenant_id"):
                values["tenant_id"] = os.getenv("AZURE_TENANT_ID")
            if not values.get("client_id"):
                values["client_id"] = os.getenv("AZURE_CLIENT_ID")
            if not values.get("client_secret"):
                values["client_secret"] = os.getenv("AZURE_CLIENT_SECRET")
        if REQUIRE_CREDS:
            key_groups = [["access_key"], ["tenant_id", "client_id", "client_secret"]]
            msg = "access_key required"  # TODO mention the alternatives
            assert any(all(values.get(key) for key in keys) for keys in key_groups), msg
        return values

    strip_prefix = validator("prefix")(lambda cls, prefix: prefix.strip("/"))


class AZConfigOverride(StorageConfigOverride):
    """Azure Blob Storage config override."""

    type: t.Literal["az"] = Field("az", title="Azure Blob Storage type")
    prefix: t.Optional[str] = Field(
        None, title="Common object key prefix", example="prefix"
    )


class DICOMConfig(StorageConfig):
    """DICOM Storage config."""

    type: t.Literal["dicom"] = Field("dicom", title="DICOM Storage type")
    host: str = Field(title="DICOM SCP / PACS server host or IP")
    port: str = Field(
        title="DICOM SCP / PACS server port",
        regex=r"^[0-9]+$",
    )
    aec: t.Optional[str] = Field(None, title="Called Application Entity Title")
    aet: str = Field("FW-STORAGE", title="Calling Application Entity Title")
    rport: t.Optional[str] = Field(None, title="Return port for moving images (C-MOVE)")

    @classmethod
    def from_url(cls, url: str) -> "DICOMConfig":
        """Return DICOM config parsed from a URL."""
        parsed = parse_url(url)
        params = {
            "type": parsed.pop("scheme"),
            "host": parsed.pop("host"),
            "port": parsed.pop("port"),
            "rport": parsed.pop("password", None),
            "aet": parsed.pop("username", "FW-STORAGE"),
        }

        aec = parsed.pop("path", None)
        if aec:
            params["aec"] = aec.strip("/")
        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        return format_url(
            scheme=self.type,
            host=self.host,
            port=int(self.port),
            username=self.aet,
            password=self.rport,
            path=self.aec,
        )

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        return self.safe_url


class DICOMWebConfig(StorageConfig):
    """DICOMweb Storage config."""

    type: t.Literal["dicomweb"] = Field("dicomweb", title="DICOMWeb Storage type")
    api_url: str = Field(title="API URL")
    auth: t.Optional[AnyAuth] = Field(None, title="Authorization")

    @classmethod
    def from_url(cls, url: str) -> "DICOMWebConfig":
        """Return DICOM config parsed from a URL."""
        parsed = parse_url(url)

        api_url = parsed.pop("host")
        port = parsed.pop("port", None)
        if port:
            api_url = f"{api_url}:{port}"
        path = parsed.pop("path", None)
        if path:
            api_url = f"{api_url}/{path}"
        driver = parsed.pop("driver", None)
        if not api_url.startswith("http"):
            if driver:
                api_url = f"{driver}://{api_url}"
            else:
                api_url = f"https://{api_url}"

        username = parsed.pop("username", None)
        password = parsed.pop("password", None)
        auth: t.Any = None
        if username:
            auth = str(username)
            if password:
                auth = f"{auth}:{str(password)}"
            if isinstance(auth, str) and ":" in auth:
                auth = tuple(auth.split(":", 1))

        params = {"type": parsed.pop("scheme"), "api_url": api_url, "auth": auth}

        assert not parsed, f"unexpected {','.join(parsed)} in url {url!r}"
        return cls(**params)

    @property
    def safe_url(self) -> str:
        """Return safe storage URL without credentials."""
        match = re.match(r"(.*)://(.*)", self.api_url)
        assert match, f"could not parse {self.api_url!r}"
        driver = match.groups()[0]
        host = match.groups()[1]

        if driver == "https":
            driver = None

        auth = self.auth
        if isinstance(auth, tuple):
            auth = ":".join(auth)

        return format_url(scheme=self.type, host=host, username=auth, driver=driver)

    @property
    def full_url(self) -> str:
        """Return full storage URL with credentials."""
        return self.safe_url


Config = t.Union[FSConfig, S3Config, GSConfig, AZConfig, DICOMConfig, DICOMWebConfig]
ConfigOverride = t.Union[
    FSConfigOverride, S3ConfigOverride, GSConfigOverride, AZConfigOverride
]
