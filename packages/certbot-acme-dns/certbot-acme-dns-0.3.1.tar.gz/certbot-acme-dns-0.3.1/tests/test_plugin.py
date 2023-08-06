def test_description(authenticator):
    assert authenticator.more_info() == authenticator.description
