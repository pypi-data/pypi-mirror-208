import json
from typing import Optional

from bpkio_api.models.common import BaseResource, NamedModel


class TranscodingProfileId(BaseResource):
    pass


class TranscodingProfileIn(NamedModel):
    content: str
    tenantId: Optional[int]


class TranscodingProfile(TranscodingProfileIn, BaseResource):
    @property
    def json_content(self):
        return json.loads(self.content)

    @property
    def num_layers(self):
        return len(self.json_content["transcoding"]["jobs"])
