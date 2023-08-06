import logging

import dns.name
import dns.resolver
from certbot.errors import PluginError

LOGGER = logging.getLogger(__name__)


class CnameUnconfigured(PluginError):
    pass


def ca_supports_rfc8657(caa_identity: str) -> bool:
    """
    Check whether a CA implements and honors RFC 8657,
    specifically the accounturi CAA issuance record
    parameter.

    >>> ca_supports_rfc8657("letsencrypt.org")
    True
    """

    return caa_identity in (
        # Let's Encrypt since 2022-12-16
        # https://community.letsencrypt.org/t/enabling-acme-caa-account-and-method-binding/189588
        "letsencrypt.org",
    )


def check_cname(source: str, target: str) -> None:
    try:
        answer = dns.resolver.resolve(source, "CNAME")
    except dns.resolver.NoAnswer as exc:
        raise CnameUnconfigured(f"No CNAME record for {source} found!") from exc

    if answer.rrset is None:
        raise CnameUnconfigured(f"No CNAME record for {source} found!")

    if len(answer.rrset) > 1:
        raise PluginError(f"Multiple CNAME records for {source}: {answer.rrset}")

    if answer.rrset[0].target != dns.name.from_text(target):
        raise PluginError(f"Incorrect CNAME record (expected {target}): {answer.rrset}")
