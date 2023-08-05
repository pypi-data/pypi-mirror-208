from enum import Enum
from typing import Optional
from urllib.parse import urljoin

from pydantic import AnyHttpUrl, BaseModel, IPvAnyAddress

from .common import BaseResource, NamedModel, PropertyMixin, WithDescription


class SourceType(Enum):
    AD_SERVER = "ad-server"
    ASSET = "asset"
    ASSET_CATALOG = "asset-catalog"
    LIVE = "live"
    SLATE = "slate"

    def __str__(self):
        return str(self.value)


class SourceFormat(Enum):
    DASH = "DASH"
    HLS = "HLS"
    JPEG = "JPEG"
    PNG = "PNG"

    def __str__(self):
        return str(self.value)


# === SOURCES Models ===


class SourceIn(NamedModel, PropertyMixin):
    url: AnyHttpUrl

    @property
    def full_url(self):
        return self.make_full_url()

    def make_full_url(self, *args, **kwargs):
        return self.url


class SourceSparse(SourceIn, BaseResource):
    type: SourceType
    format: Optional[SourceFormat] = None


# === ASSET SOURCE Models ===


class AssetSourceIn(SourceIn, WithDescription):
    backupIp: Optional[IPvAnyAddress] = None


class AssetSource(AssetSourceIn, BaseResource):
    format: Optional[SourceFormat]

    @property
    def type(self):
        return SourceType.ASSET


# === LIVE SOURCE Models ===


class LiveSourceIn(SourceIn, WithDescription):
    backupIp: Optional[IPvAnyAddress] = None


class LiveSource(LiveSourceIn, BaseResource):
    format: Optional[SourceFormat]

    @property
    def type(self):
        return SourceType.LIVE


# === ASSET CATALOG SOURCE Models ===


class AssetCatalogSourceIn(SourceIn, WithDescription):
    backupIp: Optional[IPvAnyAddress] = None
    # TODO - add type and/or validator for path
    assetSample: str

    @property
    def full_url(self):
        return self.make_full_url()

    def make_full_url(self, extra=None, *args, **kwargs):
        u = self.url
        if extra:
            u = urljoin(u, extra)
        else:
            u = urljoin(u, self.assetSample)
        return u


class AssetCatalogSource(AssetCatalogSourceIn, BaseResource):
    @property
    def type(self):
        return SourceType.ASSET_CATALOG


# === AD SERVER SOURCE Models ===


class AdServerSourceIn(SourceIn, WithDescription):
    # TODO - add type and/or validator for queries
    queries: Optional[str]

    @property
    def full_url(self):
        return self.make_full_url()

    def make_full_url(self, *args, **kwargs):
        u = self.url
        if self.queries:
            u = u + "?" + self.queries
        return u


class AdServerSource(AdServerSourceIn, BaseResource):
    @property
    def type(self):
        return SourceType.AD_SERVER


# === SLATE SOURCE Models ===


class SlateSourceIn(SourceIn, WithDescription):
    pass


class SlateSource(SlateSourceIn, BaseResource):
    format: Optional[SourceFormat]

    @property
    def type(self):
        return SourceType.SLATE


# === CHECK RESULTS Model ===


class SeverityLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    def __str__(self):
        return str(self.value)


class SourceCheckResult(BaseModel):
    messageText: str
    severityLevel: SeverityLevel
