import os
from datetime import datetime
from enum import Enum
from typing import List, Optional
from urllib.parse import urljoin, urlparse

from pydantic import BaseModel, HttpUrl

from bpkio_api.models.common import BaseResource, NamedModel, PropertyMixin
from bpkio_api.models.Sources import (
    AdServerSource,
    SlateSource,
    SourceFormat,
    SourceSparse,
)
from bpkio_api.models.TranscodingProfiles import (
    TranscodingProfile,
    TranscodingProfileId,
)


class ServiceType(Enum):
    AD_INSERTION = "ad-insertion"
    VIRTUAL_CHANNEL = "virtual-channel"
    CONTENT_REPLACEMENT = "content-replacement"

    def __str__(self):
        return str(self.value)


# === SERVICES Models ===


class ServiceIn(NamedModel, PropertyMixin):
    environmentTags: Optional[List[str]] = []


class WithCommonServiceFields(BaseResource):
    url: HttpUrl
    creationDate: datetime
    updateDate: datetime

    @property
    def serviceId(self):
        return self.url.path.split("/")[1]

    @property
    def full_url(self):
        return self.make_full_url()

    def make_full_url(self, *args, **kwargs):
        return self.url

    @property
    def format(self):
        ext = os.path.splitext(urlparse(self.url).path)[1]
        match ext:
            case ".m3u8":
                return SourceFormat.HLS
            case ".mpd":
                return SourceFormat.DASH


class ServiceSparse(ServiceIn, WithCommonServiceFields):
    type: ServiceType


# === AD-INSERTION SERVICE Models ===


class VodAdInsertionModel(BaseModel):
    adServer: AdServerSource


class LiveAdReplacementModel(BaseModel):
    adServer: AdServerSource
    gapFiller: Optional[SlateSource] = None


class AdBreakInsertionModel(BaseModel):
    adServer: AdServerSource
    gapFiller: Optional[SlateSource] = None


class LiveAdPreRollModel(BaseModel):
    adServer: AdServerSource
    maxDuration: Optional[float]
    offset: Optional[float]


class AdInsertionServiceIn(ServiceIn):
    vodAdInsertion: Optional[VodAdInsertionModel]
    liveAdPreRoll: Optional[LiveAdPreRollModel]
    liveAdReplacement: Optional[LiveAdReplacementModel]

    # TODO: parse the specific sub-type of source
    source: SourceSparse
    enableAdTranscoding: Optional[bool]
    enableServerSideAdTracking: Optional[bool]
    enableSSATCheckChunk: Optional[bool]

    # TODO - migrate to TranscodingProfile Model
    transcodingProfile: Optional[TranscodingProfileId]

    @property
    def sub_type(self):
        for prop in ["vodAdInsertion", "liveAdPreRoll", "liveAdReplacement"]:
            if getattr(self, prop):
                return prop


class AdInsertionService(AdInsertionServiceIn, WithCommonServiceFields):
    @property
    def type(self):
        return ServiceType.AD_INSERTION

    @property
    def full_url(self):
        return self.make_full_url()

    def make_full_url(self, extra=None, *args, **kwargs):
        if extra:
            return urljoin(self.url, extra)

        return self.url


# === CONTENT-REPLACEMENT SERVICE Models ===


class ContentReplacementServiceIn(ServiceIn):
    # TODO: parse the specific sub-type of source
    source: SourceSparse
    replacement: SourceSparse


class ContentReplacementService(ContentReplacementServiceIn, WithCommonServiceFields):
    @property
    def type(self):
        return ServiceType.CONTENT_REPLACEMENT


# === CONTENT-REPLACEMENT SERVICE Models ===


class VirtualChannelServiceIn(ServiceIn):
    # TODO: parse the specific sub-type of source
    baseLive: BaseResource

    enableAdTranscoding: Optional[bool] = False
    enableServerSideAdTracking: Optional[bool] = False
    enableSSATCheckChunk: Optional[bool] = False
    adBreakInsertion: Optional[AdBreakInsertionModel] = None

    # TODO - migrate to TranscodingProfile Model
    transcodingProfile: Optional[BaseResource] = None


class VirtualChannelService(VirtualChannelServiceIn, WithCommonServiceFields):
    @property
    def type(self):
        return ServiceType.VIRTUAL_CHANNEL
