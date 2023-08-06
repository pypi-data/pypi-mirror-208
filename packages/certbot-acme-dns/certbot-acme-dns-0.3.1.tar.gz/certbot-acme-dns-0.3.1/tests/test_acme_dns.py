import dataclasses
import pytest
import requests

from certbot_acme_dns._internal.acme_dns import AcmeDns, AcmeDnsError


class TestAcmeDnsAccount:
    def test_asdict(self, acme_dns_account):
        d = acme_dns_account.asdict()
        assert d["server"] == acme_dns_account.server
        assert d["username"] == acme_dns_account.username
        assert d["password"] == acme_dns_account.password
        assert d["fulldomain"] == acme_dns_account.fulldomain
        assert d["subdomain"] == acme_dns_account.subdomain


class TestAcmeDns:
    def test_register_success(self, acme_dns_account, requests_mock):
        requests_mock.post(
            acme_dns_account.server + "/register",
            json={
                "username": acme_dns_account.username,
                "password": acme_dns_account.password,
                "fulldomain": acme_dns_account.fulldomain,
                "subdomain": acme_dns_account.subdomain,
            },
        )
        acc = AcmeDns.register(server=acme_dns_account.server).account
        assert acc.username == acme_dns_account.username
        assert acc.password == acme_dns_account.password
        assert acc.fulldomain == acme_dns_account.fulldomain
        assert acc.subdomain == acme_dns_account.subdomain

    def test_register_network_failure(self, acme_dns_account, requests_mock):
        requests_mock.post(
            acme_dns_account.server + "/register",
            exc=requests.exceptions.RequestException,
        )
        with pytest.raises(AcmeDnsError):
            AcmeDns.register(server=acme_dns_account.server)

    def test_register_server_failure(self, acme_dns_account, requests_mock):
        requests_mock.post(
            acme_dns_account.server + "/register",
            text="something went wrong",
            status_code=500,
        )
        with pytest.raises(AcmeDnsError):
            AcmeDns.register(server=acme_dns_account.server)

    def test_update_success(self, acme_dns, requests_mock):
        requests_mock.post(
            acme_dns.account.server + "/update",
            request_headers={
                "X-Api-User": acme_dns.account.username,
                "X-Api-Key": acme_dns.account.password,
            },
            additional_matcher=lambda x: x.json() == {
                "subdomain": acme_dns.account.subdomain,
                "txt": "xxx",
            },
        )
        acme_dns.update(validation="xxx")

    def test_update_network_failure(self, acme_dns, requests_mock):
        requests_mock.post(
            acme_dns.account.server + "/update",
            request_headers={
                "X-Api-User": acme_dns.account.username,
                "X-Api-Key": acme_dns.account.password,
            },
            additional_matcher=lambda x: x.json() == {
                "subdomain": acme_dns.account.subdomain,
                "txt": "xxx",
            },
            exc=requests.exceptions.RequestException,
        )
        with pytest.raises(AcmeDnsError):
            acme_dns.update(validation="xxx")

    def test_update_server_failure(self, acme_dns, requests_mock):
        requests_mock.post(
            acme_dns.account.server + "/update",
            request_headers={
                "X-Api-User": acme_dns.account.username,
                "X-Api-Key": acme_dns.account.password,
            },
            additional_matcher=lambda x: x.json() == {
                "subdomain": acme_dns.account.subdomain,
                "txt": "xxx",
            },
            text="something went wrong",
            status_code=500,
        )
        with pytest.raises(AcmeDnsError):
            acme_dns.update(validation="xxx")
