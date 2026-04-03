import json
from gate.sbom import generate, _purl


# ── purl generation ───────────────────────────────────────────────────────────

def test_purl_pypi():
    assert _purl("requests", "2.28.0", "PyPI") == "pkg:pypi/requests@2.28.0"


def test_purl_pypi_lowercased():
    assert _purl("Requests", "2.28.0", "PyPI") == "pkg:pypi/requests@2.28.0"


def test_purl_npm():
    assert _purl("lodash", "4.17.21", "npm") == "pkg:npm/lodash@4.17.21"


def test_purl_npm_scoped():
    purl = _purl("@babel/core", "7.0.0", "npm")
    assert purl.startswith("pkg:npm/")
    assert "babel" in purl
    assert "7.0.0" in purl


# ── generate ─────────────────────────────────────────────────────────────────

def _make_pkg(name: str, version: str, errors: list[str] | None = None) -> dict:
    return {"name": name, "version": version, "errors": errors or [], "warnings": []}


def test_structure():
    doc = generate([_make_pkg("requests", "2.28.0")], "PyPI")
    assert doc["bomFormat"] == "CycloneDX"
    assert doc["specVersion"] == "1.6"
    assert "serialNumber" in doc
    assert "metadata" in doc
    assert len(doc["components"]) == 1


def test_component_fields():
    doc = generate([_make_pkg("flask", "3.0.0")], "PyPI")
    comp = doc["components"][0]
    assert comp["name"] == "flask"
    assert comp["version"] == "3.0.0"
    assert comp["purl"] == "pkg:pypi/flask@3.0.0"
    assert "bom-ref" in comp


def test_vulnerabilities_extracted():
    pkg = _make_pkg("lodash", "4.17.15", errors=[
        "CVE-2021-23337: Command Injection in lodash",
        "CVE-2020-8203: Prototype Pollution",
    ])
    doc = generate([pkg], "npm")
    assert "vulnerabilities" in doc
    ids = [v["id"] for v in doc["vulnerabilities"]]
    assert "CVE-2021-23337" in ids
    assert "CVE-2020-8203" in ids


def test_no_vulnerabilities_key_when_clean():
    doc = generate([_make_pkg("flask", "3.0.0")], "PyPI")
    assert "vulnerabilities" not in doc


def test_multiple_packages():
    packages = [
        _make_pkg("requests", "2.28.0"),
        _make_pkg("flask", "3.0.0"),
    ]
    doc = generate(packages, "PyPI")
    assert len(doc["components"]) == 2


def test_tool_metadata():
    doc = generate([_make_pkg("x", "1.0")], "PyPI")
    tools = doc["metadata"]["tools"]
    assert any(t["name"] == "gate" for t in tools)


def test_serializable_to_json():
    doc = generate([_make_pkg("requests", "2.28.0")], "PyPI")
    output = json.dumps(doc)
    assert "CycloneDX" in output
