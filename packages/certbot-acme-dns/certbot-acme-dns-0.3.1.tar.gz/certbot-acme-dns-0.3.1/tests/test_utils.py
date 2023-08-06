import pytest

from certbot_acme_dns._internal.util import ca_supports_rfc8657


class TestCaSupportsRfc8657:
    def test_false(self, authenticator):
        assert ca_supports_rfc8657("example.com") is False
