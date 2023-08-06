import common  # noqa
import tarvis.common.environ


def test_config():
    config = common.container.config
    assert config.get("foo") == "bar"
    assert config.get("platform") == tarvis.common.environ.platform.name
    assert config.get("deployment") == tarvis.common.environ.deployment.name
