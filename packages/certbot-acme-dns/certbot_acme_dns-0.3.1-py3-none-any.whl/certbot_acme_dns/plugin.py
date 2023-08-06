"""ACME DNS Authenticator plugin for Certbot."""
import functools
import logging
import time
from typing import Any, Callable, Iterable, List, Optional, Tuple, Union, cast

import zope.component  # type: ignore
import zope.interface  # type: ignore

try:
    from acme.client import ClientV2
except ImportError:
    from acme.client import BaseClient as ClientV2  # type: ignore[attr-defined,no-redef]

from certbot._internal.account import Account, AccountFileStorage
from certbot._internal.client import acme_from_config_key
from certbot.display.util import CANCEL, OK
from certbot.errors import PluginError
from certbot.interfaces import IAuthenticator, IPluginFactory
from certbot.plugins.dns_common import DNSAuthenticator
from certbot.plugins.storage import PluginStorage

try:
    from certbot.display.util import menu, notification
except ImportError:
    from certbot.interfaces import IDisplay  # type: ignore[attr-defined]

    def menu(
        message: str,
        choices: Union[List[str], List[Tuple[str, str]]],
        default: Optional[int] = None,
        cli_flag: Optional[str] = None,
        force_interactive: bool = False,
    ) -> Tuple[str, int]:
        """Backwards compatibility wrapper for the menu display utility."""
        return zope.component.getUtility(IDisplay).menu(  # type: ignore[no-any-return]
            message=message,
            choices=choices,
            default=default,
            cli_flag=cli_flag,
            force_interactive=force_interactive,
        )

    def notification(
        message: str,
        pause: bool = True,
        wrap: bool = True,
        force_interactive: bool = False,
        decorate: bool = True,
    ) -> None:
        """Backwards compatibility wrapper for the notification display utility."""
        return zope.component.getUtility(IDisplay).notification(  # type: ignore[no-any-return]
            message=message,
            pause=pause,
            wrap=wrap,
            force_interactive=force_interactive,
            decorate=decorate,
        )


from ._internal.acme_dns import AcmeDns, AcmeDnsAccount
from ._internal.caa import CaaSecurityChecker, CaaUnconfigured
from ._internal.util import CnameUnconfigured, ca_supports_rfc8657, check_cname

LOGGER = logging.getLogger(__name__)


@zope.interface.implementer(IAuthenticator)
@zope.interface.provider(IPluginFactory)
class Authenticator(DNSAuthenticator):
    """
    ACME DNS Authenticator

    This Authenticator fulfills dns-01 challenges using an ACME DNS
    server running the acme-dns software [1].

    [1] https://github.com/joohoi/acme-dns
    """

    description = "Obtains certificates using an ACME DNS server."

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.storage = PluginStorage(self.config, self.name)

    def more_info(self) -> str:
        return self.description

    @classmethod
    def add_parser_arguments(
        cls, add: Callable[..., None], default_propagation_seconds: int = 10
    ) -> None:
        super().add_parser_arguments(
            add, default_propagation_seconds=default_propagation_seconds
        )
        add(
            "server",
            type=str,
            default="https://auth.acme-dns.io",
            help="URL of the ACME DNS server.",
        )
        add(
            "is-trusted",
            default=False,
            action="store_true",
            help="[INSECURE] Ignore that the chosen CA does not support RFC 8657.",
        )

    def _setup_credentials(self) -> None:
        pass

    def _perform(self, domain: str, validation_name: str, validation: str) -> None:
        if not any(ca_supports_rfc8657(x) for x in self._caa_identities):
            if self.conf("is-trusted"):
                LOGGER.warning(
                    "Ignoring that the chosen CA does not support RFC 8657"
                    " (INSECURE, unless you self-host the ACME DNS server)."
                )
            else:
                raise PluginError(
                    "CA does not support RFC 8657, unable to proceed securely."
                )

        for is_retry in (False, True):
            try:
                check_cname(
                    source=validation_name,
                    target=self._acme_dns.account.fulldomain,
                )
            except CnameUnconfigured:
                if is_retry:
                    raise
                self._request_dns_config(
                    records=[
                        f"{validation_name}. IN CNAME {self._acme_dns.account.fulldomain}",
                    ],
                )
                continue
            else:
                break

        for is_retry in (False, True):
            try:
                CaaSecurityChecker(domain).is_secure(
                    accounturi=self._account.regr["uri"],
                    caa_identities=self._caa_identities,
                )
            except CaaUnconfigured:
                if is_retry:
                    raise
                caa_identity = self._caa_identities[0]
                account_uri = self._account.regr["uri"]
                value = f"{caa_identity}; accounturi={account_uri}"
                self._request_dns_config(
                    records=[
                        f"{domain}. IN CAA 0 issue \"{value}\"",
                    ],
                )
                continue
            else:
                break

        self._acme_dns.update(validation)

    def _cleanup(self, domain: str, validation_name: str, validation: str) -> None:
        pass

    def _request_dns_config(self, records: Iterable[str]) -> None:
        notification(
            (
                "Please configure the following DNS record(s):\n\t"
                + "\n\t".join(records)
            ),
            pause=True,
            wrap=False,
            force_interactive=True,
        )
        self._wait_dns_propagation()

    def _wait_dns_propagation(self) -> None:
        notification(
            f"Waiting {self.conf('propagation-seconds')} seconds"
            f" for DNS changes to propagate.",
            pause=False,
            decorate=False,
        )
        time.sleep(self.conf("propagation-seconds"))

    @functools.cached_property
    def _caa_identities(self) -> List[str]:
        try:
            return cast(List[str], self._client.directory.meta.caa_identities)
        except AttributeError as exc:
            raise PluginError(
                "Unable to determine CA's supported CAA hostnames."
            ) from exc

    @functools.cached_property
    def _account(self) -> Account:
        storage = AccountFileStorage(self.config)
        return storage.load(self.config.account)

    @functools.cached_property
    def _client(self) -> ClientV2:
        return acme_from_config_key(self.config, self._account.key)

    @functools.cached_property
    def _acme_dns(self) -> AcmeDns:
        try:
            all_accounts = self.storage.fetch("accounts")
        except KeyError:
            all_accounts = []

        server = self.conf("server")
        server_accounts = [
            AcmeDnsAccount(**acc) for acc in all_accounts if acc["server"] == server
        ]

        if len(server_accounts) > 1:
            code, index = menu(
                "Please choose an ACME DNS account",
                [x.username for x in server_accounts],
                force_interactive=True,
            )
            if code == CANCEL:
                raise PluginError("Cancelled.")
            if code != OK:
                raise PluginError("Invalid selection!")
            return AcmeDns(server_accounts[index])

        if len(server_accounts) == 1:
            return AcmeDns(server_accounts[0])

        ret = AcmeDns.register(server=server)
        all_accounts.append(ret.account.asdict())
        self.storage.put("accounts", all_accounts)
        self.storage.save()
        return ret
