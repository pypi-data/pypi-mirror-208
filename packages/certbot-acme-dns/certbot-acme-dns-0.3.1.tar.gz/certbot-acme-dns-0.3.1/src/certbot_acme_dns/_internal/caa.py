import logging
from typing import Sequence, Tuple

import dns.exception
import dns.resolver
from certbot.errors import PluginError
from certbot.plugins.dns_common import base_domain_name_guesses
from dns.rdtypes.ANY.CAA import CAA

LOGGER = logging.getLogger(__name__)


class CaaError(PluginError):
    pass


class CaaResolverError(CaaError):
    pass


class CaaUnconfigured(CaaError):
    pass


class CaaSecurityError(CaaError):
    pass


class CaaMaybeInsecure(CaaSecurityError):
    pass


class CaaSecurityChecker:
    def __init__(self, domain: str) -> None:
        self.domain = domain

    def is_secure(self, accounturi: str, caa_identities: Sequence[str]) -> None:
        if not caa_identities:
            raise CaaError("Need at least one CAA identity!")

        actual = {
            (rec.flags, rec.tag, rec.value)
            for rec in self.get_caa_records(self.domain)
            if rec.tag in (b"issue", b"issuewild")
        }

        have_issuewild = bool([x for x in actual if x[1] == b"issuewild"])
        deny_issuewild = (0, b"issuewild", b";") in actual
        can_issuewild: bool = False

        at_least_one_of = set()
        allowed = set()
        allowed.add((0, b"issue", b";"))
        allowed.add((0, b"issuewild", b";"))
        for caa_identity in caa_identities:
            value = f"{caa_identity}; accounturi={accounturi}".encode("ascii")
            issue_record = (0, b"issue", value)
            issuewild_record = (0, b"issuewild", value)

            at_least_one_of.add(issue_record)
            allowed.add(issue_record)
            allowed.add(issuewild_record)

            if (0, b"issuewild", value) in actual:
                can_issuewild = True

        extras = actual.difference(allowed)
        if extras:
            raise CaaMaybeInsecure(
                f"Potentially insecure CAA configuration,"
                f" unexpected CAA records found: {extras}"
            )

        matching = actual.intersection(at_least_one_of)
        if not matching:
            raise CaaUnconfigured(
                "No good RFC 8657 accounturi restricted CAA records found!"
            )

        if have_issuewild and not deny_issuewild and not can_issuewild:
            LOGGER.warning(
                "Selected CA is not allowed to issue wildcard certificates for domain"
                " *.%s. This can be fixed by adding the following DNS record:\n"
                "    %s. IN CAA 0 issuewild \"%s\"",
                self.domain,
                self.domain,
                f"{caa_identities[0]}; accounturi={accounturi}",
            )

        LOGGER.info("Good CAA record set found: %s", matching)

    @staticmethod
    def get_caa_records(domain: str) -> Tuple[CAA, ...]:
        for candidate in base_domain_name_guesses(domain):
            try:
                answer = dns.resolver.resolve(
                    candidate, "CAA", raise_on_no_answer=False
                )
            except dns.exception.DNSException as exc:
                raise CaaResolverError from exc
            if answer.rrset is None:
                LOGGER.debug("No CAA records for candidate domain %s exist.", candidate)
                continue
            break
        else:
            LOGGER.debug("No CAA records found.")
            return ()

        LOGGER.debug("Found CAA records for %s.", answer.name)
        return tuple(answer.rrset)
