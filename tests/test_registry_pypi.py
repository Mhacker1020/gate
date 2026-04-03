import json
from unittest.mock import patch, MagicMock
from datetime import timezone

from gate.registry.pypi import get_package_info


def _mock_response(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.read.return_value = json.dumps(data).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


PYPI_RESPONSE = {
    "info": {
        "name": "requests",
        "version": "2.31.0",
        "home_page": "https://requests.readthedocs.io",
        "requires_dist": [],
    },
    "releases": {
        "2.31.0": [
            {"upload_time": "2023-05-22T14:12:00", "filename": "requests-2.31.0.tar.gz"},
        ],
        "2.28.0": [
            {"upload_time": "2022-06-29T10:00:00", "filename": "requests-2.28.0.tar.gz"},
        ],
    },
}


def test_returns_latest_when_no_version():
    with patch("urllib.request.urlopen", return_value=_mock_response(PYPI_RESPONSE)):
        info = get_package_info("requests")

    assert info is not None
    assert info["name"] == "requests"
    assert info["version"] == "2.31.0"
    assert info["published"].tzinfo == timezone.utc


def test_returns_specific_version():
    with patch("urllib.request.urlopen", return_value=_mock_response(PYPI_RESPONSE)):
        info = get_package_info("requests", "2.28.0")

    assert info["version"] == "2.28.0"


def test_returns_none_for_unknown_version():
    with patch("urllib.request.urlopen", return_value=_mock_response(PYPI_RESPONSE)):
        info = get_package_info("requests", "0.0.1")

    assert info is None


def test_returns_none_on_http_error():
    import urllib.error
    with patch("urllib.request.urlopen", side_effect=urllib.error.HTTPError(
        url="", code=404, msg="Not Found", hdrs=None, fp=None
    )):
        info = get_package_info("nonexistent-package-xyz")

    assert info is None


def test_returns_none_on_network_error():
    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        info = get_package_info("requests")

    assert info is None
