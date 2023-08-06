import common  # noqa
from tarvis.common.secrets import get_secret


def test_secret():
    assert get_secret("foo") == "bar"


def test_secret_remap():
    assert get_secret("bar") == "foo"
