"""Utility functions."""
import re
import typing as t
from functools import partial

from pydantic import BaseModel, Field, root_validator

URL_RE = re.compile(
    r"^"
    r"(?P<scheme>[^+:@/?#]+)(\+(?P<driver>[^:@/?#]+))?://"
    r"((?P<username>[^:@]+)(:(?P<password>[^@]+))?@)?"
    r"(?P<host>[^:@/?#]*)"
    r"(:(?P<port>\d+))?"
    r"((?P<path>/[^?#]*))?"
    r"(\?(?P<query>[^#]+))?"
    r"(#(?P<fragment>.*))?"
    r"$"
)


class URL(BaseModel):
    """URL model with driver & parsed query string."""

    class Config:
        """Forbid extra attrs."""

        extra = "forbid"

    scheme: str
    driver: t.Optional[str] = None
    username: t.Optional[str] = None
    password: t.Optional[str] = None
    host: t.Optional[str] = None
    port: t.Optional[int] = None
    path: t.Optional[str] = None
    query: t.Dict[str, str] = {}
    fragment: t.Optional[str] = None

    @root_validator(pre=True)
    @classmethod
    def flex_load(cls, values: dict) -> dict:
        """Return dict without null values and unknown keys as query params."""
        props = cls.schema()["properties"]
        query = values.pop("query", {})
        extra = [key for key in values if key not in props]
        for key in extra:
            query[key] = values.pop(key)
        values["query"] = filter_none(query)
        values = filter_none(values)
        return values

    def dict(self, merge: bool = True, **kw) -> dict:  # noqa: D417
        """Return model as a dict, w/ the query merged into it by default.

        Args:
            merge: Set to False to retain query as a top-level dict key.
        """
        kw.setdefault("exclude_none", True)
        data = super().dict(**kw)
        if merge:
            data.update(data.pop("query", {}))
        return data

    @classmethod
    def from_string(cls, url: str) -> "URL":
        """Return URL parsed from a string."""
        match = URL_RE.match(url)
        if not match:
            raise ValueError(f"cannot parse url {url!r}")
        parsed = filter_none(match.groupdict())
        params = [p for p in parsed.pop("query", "").split("&") if p]
        query = parsed["query"] = {}
        for param in params:
            param += "=" if "=" not in param else ""
            key, value = param.split("=", maxsplit=1)
            query.setdefault(key, value)
        return cls(**parsed)

    def __str__(self) -> str:
        """Return URL string."""
        url = self.scheme
        if self.driver:
            url += f"+{self.driver}"
        url += "://"
        if self.username:
            url += self.username
            if self.password:
                url += f":{self.password}"
            url += "@"
        if self.host:
            url += self.host
        if self.port:
            url += f":{self.port}"
        if self.path:
            url += self.path
        if self.query:
            query = ""
            for key, value in self.query.items():
                value = value.lower() if value in {"True", "False"} else value
                query += "?" if not query else "&"
                query += f"{key}={value}"
            url += query
        if self.fragment:
            url += f"#{self.fragment}"
        return url


def filter_none(data: dict) -> dict:
    """Return filtered dict without any None values."""
    return {k: v for k, v in data.items() if v is not None}


def true(_) -> bool:
    """Return True, regardless of the value passed. Default ls() filter."""
    return True


def copy_field_func(model: t.Type[BaseModel]) -> t.Callable:
    """Return pydantic Field copier for a given model."""
    return partial(copy_field, model)


def copy_field(model: t.Type[BaseModel], field: str, **kw) -> t.Callable:
    """Return pydantic Field with params copied from another model field."""
    props = model.schema()["properties"][field].copy()
    props.update(kw)
    props.pop("type")
    return Field(**props)
