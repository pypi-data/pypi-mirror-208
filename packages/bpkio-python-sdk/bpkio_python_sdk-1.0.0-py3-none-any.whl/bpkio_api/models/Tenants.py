from datetime import datetime
from typing import Optional

from pydantic import PrivateAttr

from bpkio_api.models.common import BaseResource, NamedModel


class Tenant(BaseResource, NamedModel):
    # TODO - Turn to enum
    commercialPlan: str
    # TODO - Turn to enum
    state: str
    sendAnalytics: Optional[bool] = False
    creationDate: datetime
    updateDate: datetime

    _fqdn: str = PrivateAttr()
