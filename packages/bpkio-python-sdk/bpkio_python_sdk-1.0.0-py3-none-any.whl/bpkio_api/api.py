import base64
import json
import os
from typing import Optional

from uplink import Consumer
from uplink.auth import BearerToken

from bpkio_api.caching import init_cache
from bpkio_api.credential_provider import TenantProfileProvider
from bpkio_api.defaults import DEFAULT_FQDN
from bpkio_api.endpoints import (
    CategoriesApi,
    ConsumptionApi,
    ServicesApi,
    SourcesApi,
    TenantsApi,
    TranscodingProfilesApi,
    UsersApi,
)
from bpkio_api.exceptions import InvalidApiKeyFormat
from bpkio_api.models import Tenant


class BroadpeakIoApi(Consumer):
    def __init__(
        self,
        *,
        tenant: Optional[str] = None,
        api_key: Optional[str] = None,
        fqdn: str = DEFAULT_FQDN,
        use_cache: bool = True,
        **kwargs,
    ):
        if tenant and api_key:
            raise ValueError("You can't specify both tenant and api_key")

        tp = TenantProfileProvider()

        if tenant:
            t = tp.get_tenant_profile(tenant)
            self._api_key = t.api_key
            self._fqdn = t.fqdn

        elif api_key:
            self._api_key = api_key
            self._fqdn = fqdn or DEFAULT_FQDN

        elif os.environ.get("BPKIO_TENANT"):
            t = tp.get_tenant_profile(os.environ.get("BPKIO_TENANT"))
            self._api_key = t.api_key
            self._fqdn = t.fqdn

        elif os.environ.get("BPKIO_API_KEY"):
            self._api_key = os.environ.get("BPKIO_API_KEY")
            self._fqdn = os.environ.get("BPKIO_FQDN") or DEFAULT_FQDN

        elif tp.has_default_tenant():
            t = tp.get_tenant_profile("default")
            self._api_key = t.api_key
            self._fqdn = t.fqdn

        else:
            raise ValueError(
                "You must specify either api_key or tenant, "
                "or have configured a default tenant"
            )

        base_url = f"https://{self._fqdn}/v1/"

        super().__init__(base_url, auth=BearerToken(self._api_key), **kwargs)

        tenant_id = self.parse_api_key().get("tenantId")
        if use_cache:
            init_cache(self.fqdn, tenant_id)

        self.sources = SourcesApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.services = ServicesApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.tenants = TenantsApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.users = UsersApi(base_url, auth=BearerToken(self._api_key), **kwargs)
        self.transcoding_profiles = TranscodingProfilesApi(
            base_url, auth=BearerToken(self._api_key), **kwargs
        )
        self.consumption = ConsumptionApi(
            base_url, auth=BearerToken(self._api_key), **kwargs
        )
        self.categories = CategoriesApi(
            base_url, auth=BearerToken(self._api_key), **kwargs
        )

    @staticmethod
    def _parse_api_key(candidate: str) -> dict:
        """Parses an API Key (token) and extract the information it contains.

        Args:
            candidate (str): The API key

        Returns:
            dict: The content of the API key
        """
        try:
            parts = candidate.split(".")
            # Padding is required. Length doesn't matter provided it's long enough
            base64_bytes = parts[1] + "========"
            s = base64.b64decode(base64_bytes).decode("utf-8")
            payload = json.loads(s)
            # self.logger.debug("API Key payload: " + str(payload))
            return payload
        except Exception as e:
            raise InvalidApiKeyFormat(reason=e)

    def parse_api_key(self) -> dict:
        """Parses the API Key (token) and extract the information it contains"""
        return self._parse_api_key(self._api_key)

    @staticmethod
    def is_valid_api_key_format(string: str):
        try:
            BroadpeakIoApi._parse_api_key(string)
            return True
        except:
            return False

    def get_tenant_id(self) -> int:
        return self.parse_api_key().get("tenantId")

    def get_self_tenant(self) -> Tenant:
        """Get tenant linked to the current API Key"""

        tenant_id = self.get_tenant_id()
        tenant = self.tenants.retrieve(tenant_id)
        tenant._fqdn = self.fqdn
        return tenant

    @property
    def fqdn(self):
        return self._fqdn

    def uses_default_fqdn(self):
        return self._fqdn == DEFAULT_FQDN

    @staticmethod
    def is_correct_entrypoint(url: str, api_key: str) -> bool:
        """Checks that the URL is a valid Broadpeak.io entrypoint"""
        try:
            api = BroadpeakIoApi(api_key=api_key, fqdn=url)
            api.get_self_tenant()
            return True
        except Exception as e:
            return False
