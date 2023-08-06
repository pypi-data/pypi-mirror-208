import configparser
from os import environ, path
from pathlib import Path
from typing import Optional

from pydantic import BaseModel

from bpkio_api.defaults import DEFAULT_FQDN

DEFAULT_INI_FILE = path.join(path.expanduser("~"), ".bpkio/tenants")


class TenantProfile(BaseModel):
    label: str
    id: str
    fqdn: Optional[str] = DEFAULT_FQDN
    api_key: str


class TenantProfileProvider:
    config = configparser.ConfigParser()

    def __init__(self, filename: Optional[str] = None) -> None:
        f = Path(filename or DEFAULT_INI_FILE)
        if not f.exists():
            f.parent.mkdir(exist_ok=True, parents=True)
            f.touch()

        self._filename = f
        self._read_ini_file()

    @property
    def inifile(self):
        return self._filename

    def get_tenant_profile(self, tenant_label: str):
        return TenantProfile(
            label=tenant_label,
            api_key=self.config[tenant_label].get("api_key"),
            id=self.config[tenant_label].get("id"),
            fqdn=self.config[tenant_label].get("fqdn", DEFAULT_FQDN),
        )

    def list_tenants(self):
        tenants = []
        for section in self.config.sections():
            tenants.append(
                TenantProfile(
                    label=section,
                    id=self.config[section].get("id"),
                    fqdn=self.config[section].get("fqdn", DEFAULT_FQDN),
                    api_key=self.config[section].get("api_key"),
                )
            )
        return tenants

    def has_tenant_label(self, tenant: str):
        return tenant in self.config

    def has_default_tenant(self):
        return self.has_tenant_label("default")

    # --- Core methods to read and write the `tenants` file ---

    def _get_tenant_section(self, tenant: str | None):
        tenant_section = None
        if tenant:
            if tenant in self.config:
                # tenant is the key in a section of the config file
                tenant_section = self.config[tenant]

            elif tenant.isdigit():
                # by tenant ID, in the first section that contains it
                for section in self.config.sections():
                    if (
                        "id" in self.config[section]
                        and self.config[section]["id"] == tenant
                    ):
                        tenant_section = self.config[section]

            if not tenant_section:
                raise InvalidTenantError(
                    f"There is no tenant `{tenant}` in the file at {self._filename}"
                )

        if not tenant_section and "default" in self.config:
            # default section
            tenant_section = self.config["default"]

        if not tenant_section:
            raise NoTenantSectionError()

        return tenant_section

    def _read_ini_file(self):
        # TODO - warning if the file does not exist
        self.config.read(DEFAULT_INI_FILE)

    def _from_config_file_section(self, tenant: str, key: str) -> str:
        return self.config[tenant][key]

    def _from_env(self, var) -> Optional[str]:
        return environ.get(var)

    def add_tenant(self, key: str, entries: dict):
        self.config[key] = entries
        with open(self._filename, "w") as ini:
            self.config.write(ini)


class InvalidTenantError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)


class NoTenantSectionError(Exception):
    def __init__(self) -> None:
        super().__init__(
            "No valid tenant section could be found in the tenant config file"
        )
