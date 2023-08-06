import pytest

from astronomer_ci.exceptions import InvalidConfiguration
from astronomer_ci.github import _validate_version


def test_validate_version():
    """Test input validation for
    an Astronomer-style semantic version
    """
    _validate_version("v0.0.0")
    _validate_version("v1.2.3")
    _validate_version("v111.2222.3333")
    _validate_version("v0.0.0-rc.1")
    _validate_version("v0.0.0-alpha.100")
    _validate_version("v100.0.9")
    with pytest.raises(InvalidConfiguration):
        _validate_version("0.0.0")
    with pytest.raises(InvalidConfiguration):
        _validate_version("0.0.0-rc.1")
    with pytest.raises(InvalidConfiguration):
        _validate_version("v0.0.0-.1")
    with pytest.raises(InvalidConfiguration):
        _validate_version("v.0.0")
    with pytest.raises(InvalidConfiguration):
        _validate_version("v1.0")
    with pytest.raises(InvalidConfiguration):
        _validate_version("v1.0.0-rc.")
    with pytest.raises(InvalidConfiguration):
        _validate_version("v1.0.0 ")
    with pytest.raises(InvalidConfiguration):
        _validate_version(" v1.0.0")
    with pytest.raises(InvalidConfiguration):
        _validate_version("v1..0")
    with pytest.raises(InvalidConfiguration):
        _validate_version("v1.0.")
