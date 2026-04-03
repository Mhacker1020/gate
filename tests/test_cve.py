import json
from io import BytesIO
from unittest.mock import patch, MagicMock

from gate.checks.cve import check_cve


def _mock_response(data: dict) -> MagicMock:
    mock = MagicMock()
    mock.read.return_value = json.dumps(data).encode()
    mock.__enter__ = lambda s: s
    mock.__exit__ = MagicMock(return_value=False)
    return mock


def test_no_vulns():
    with patch("urllib.request.urlopen", return_value=_mock_response({"vulns": []})):
        result = check_cve("safe-pkg", "1.0.0", "PyPI")
    assert result == []


def test_single_cve():
    payload = {
        "vulns": [{
            "id": "GHSA-xxxx-yyyy-zzzz",
            "aliases": ["CVE-2023-12345"],
            "summary": "A bad vulnerability",
        }]
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        result = check_cve("bad-pkg", "1.0.0", "PyPI")

    assert len(result) == 1
    assert result[0]["id"] == "CVE-2023-12345"
    assert result[0]["summary"] == "A bad vulnerability"


def test_prefers_cve_id_over_ghsa():
    payload = {
        "vulns": [{
            "id": "GHSA-xxxx-yyyy-zzzz",
            "aliases": ["CVE-2023-99999"],
            "summary": "Test",
        }]
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        result = check_cve("pkg", "1.0.0", "PyPI")

    assert result[0]["id"] == "CVE-2023-99999"


def test_deduplicates_vulns():
    payload = {
        "vulns": [
            {"id": "GHSA-aaaa", "aliases": ["CVE-2023-11111"], "summary": "First"},
            {"id": "GHSA-bbbb", "aliases": ["CVE-2023-11111"], "summary": "Duplicate"},
        ]
    }
    with patch("urllib.request.urlopen", return_value=_mock_response(payload)):
        result = check_cve("pkg", "1.0.0", "PyPI")

    assert len(result) == 1


def test_network_error_returns_empty():
    with patch("urllib.request.urlopen", side_effect=Exception("timeout")):
        result = check_cve("pkg", "1.0.0", "PyPI")
    assert result == []
