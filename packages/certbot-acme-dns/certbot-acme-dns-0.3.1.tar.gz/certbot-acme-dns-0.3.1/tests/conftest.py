import pytest

from argparse import Namespace
try:
    from certbot.configuration import NamespaceConfig
except ImportError:
    from certbot._internal.configuration import NamespaceConfig
from certbot_acme_dns.plugin import Authenticator
from certbot_acme_dns._internal.acme_dns import AcmeDns, AcmeDnsAccount


@pytest.fixture
def acme_dns_account():
    return AcmeDnsAccount(
        server="https://acme-dns.example.com",
        username="foo",
        password="bar",
        fulldomain="moo.acme-dns.example.com",
        subdomain="moo",
    )


@pytest.fixture
def acme_dns(acme_dns_account):
    return AcmeDns(acme_dns_account)


@pytest.fixture
def authenticator(tmpdir):
    namespace = Namespace(
        config_dir=tmpdir / "config",
        logs_dir=tmpdir / "logs",
        work_dir=tmpdir / "work",
        http01_port=12345,
        https_port=443,
        domains=["my.domain.example.com"],
        acme_dns_url="https://acme-dns.example.com",
    )
    return Authenticator(config=NamespaceConfig(namespace), name="acme-dns")
