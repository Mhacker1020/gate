import json
from unittest.mock import patch, MagicMock

from gate.registry.npm import get_package_info


def _mock_response(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.read.return_value = json.dumps(data).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


NPM_RESPONSE = {
    "name": "lodash",
    "dist-tags": {"latest": "4.17.21"},
    "time": {
        "4.17.21": "2021-02-20T15:42:16.891Z",
        "4.17.15": "2019-07-19T17:25:23.071Z",
    },
    "versions": {
        "4.17.21": {
            "scripts": {},
            "maintainers": [{"name": "jdalton"}],
        },
        "4.17.15": {
            "scripts": {
                "postinstall": "node setup.js",
            },
            "maintainers": [{"name": "jdalton"}],
        },
    },
}


def test_returns_latest_version():
    with patch("urllib.request.urlopen", return_value=_mock_response(NPM_RESPONSE)):
        info = get_package_info("lodash")

    assert info is not None
    assert info["name"] == "lodash"
    assert info["version"] == "4.17.21"
    assert info["published"] is not None


def test_returns_specific_version():
    with patch("urllib.request.urlopen", return_value=_mock_response(NPM_RESPONSE)):
        info = get_package_info("lodash", "4.17.15")

    assert info["version"] == "4.17.15"


def test_detects_install_scripts():
    with patch("urllib.request.urlopen", return_value=_mock_response(NPM_RESPONSE)):
        info = get_package_info("lodash", "4.17.15")

    assert "postinstall" in info["install_scripts"]
    assert info["install_scripts"]["postinstall"] == "node setup.js"


def test_no_install_scripts_when_clean():
    with patch("urllib.request.urlopen", return_value=_mock_response(NPM_RESPONSE)):
        info = get_package_info("lodash", "4.17.21")

    assert info["install_scripts"] == {}


def test_returns_none_for_unknown_version():
    with patch("urllib.request.urlopen", return_value=_mock_response(NPM_RESPONSE)):
        info = get_package_info("lodash", "0.0.1")

    assert info is None


def test_returns_none_on_network_error():
    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        info = get_package_info("lodash")

    assert info is None
