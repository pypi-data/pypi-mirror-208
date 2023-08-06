"""ACME DNS API wrapper, exception class and account dataclass."""

import dataclasses
import logging
from typing import Dict
from urllib.parse import urljoin

import requests
from certbot.errors import PluginError

LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class AcmeDnsAccount:
    """Holds ACME DNS account details."""

    server: str
    username: str
    password: str
    fulldomain: str
    subdomain: str

    def asdict(self) -> Dict[str, str]:
        """A dictionary representation of self."""

        return dataclasses.asdict(self)


class AcmeDnsError(PluginError):
    """ACME DNS exception class."""


class AcmeDns:
    """ACME DNS API wrapper."""

    def __init__(self, account: AcmeDnsAccount) -> None:
        self.account = account

    @classmethod
    def register(cls, server: str) -> "AcmeDns":
        """Register a new ACME DNS account."""

        register_url = urljoin(server, "register")
        try:
            response = requests.post(register_url, timeout=30)
        except requests.exceptions.RequestException as exc:
            raise AcmeDnsError(
                f"Network error while trying to register new ACME DNS account: {exc!s}"
            ) from exc
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise AcmeDnsError(
                f"Failed to register new ACME DNS account: {response.text}"
            ) from exc
        creds = response.json()
        account = AcmeDnsAccount(
            server=server,
            username=creds.get("username"),
            password=creds.get("password"),
            fulldomain=creds.get("fulldomain"),
            subdomain=creds.get("subdomain"),
        )
        LOGGER.info("Created new ACME DNS account: %s", account.username)
        return cls(account=account)

    def update(self, validation: str) -> None:
        """Update DNS-01 validation record on the ACME DNS server."""

        update_url = urljoin(self.account.server, "update")
        try:
            response = requests.post(
                update_url,
                headers={
                    "X-Api-User": self.account.username,
                    "X-Api-Key": self.account.password,
                },
                json={
                    "subdomain": self.account.subdomain,
                    "txt": validation,
                },
                timeout=30,
            )
        except requests.exceptions.RequestException as exc:
            raise AcmeDnsError(
                f"Network error while trying to update ACME DNS validation record: {exc!s}"
            ) from exc
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as exc:
            raise AcmeDnsError(
                f"Failed to update ACME DNS validation record: {response.text}"
            ) from exc
        LOGGER.info("Successfully updated ACME DNS validation record.")
