import json
import textwrap
import tempfile
from pathlib import Path

from gate.cli import _parse_poetry_lock, _parse_pipfile_lock


# ── poetry.lock ───────────────────────────────────────────────────────────────

POETRY_LOCK = textwrap.dedent("""\
    [[package]]
    name = "requests"
    version = "2.28.0"
    description = "Python HTTP for Humans."
    files = [
        {file = "requests-2.28.0-py3-none-any.whl", hash = "sha256:abcdef1234"},
        {file = "requests-2.28.0.tar.gz", hash = "sha256:deadbeef5678"},
    ]

    [[package]]
    name = "flask"
    version = "3.0.0"
    description = "A simple framework."
    files = []
""")


def _write_tmp(name: str, content: str) -> Path:
    tmp = tempfile.NamedTemporaryFile(mode="w", suffix=name, delete=False, encoding="utf-8")
    tmp.write(content)
    tmp.flush()
    return Path(tmp.name)


def test_poetry_lock_names_and_versions():
    path = _write_tmp(".lock", POETRY_LOCK)
    pkgs = _parse_poetry_lock(path)
    names = [p[0] for p in pkgs]
    assert "requests" in names
    assert "flask" in names


def test_poetry_lock_version():
    path = _write_tmp(".lock", POETRY_LOCK)
    pkgs = {p[0]: p for p in _parse_poetry_lock(path)}
    assert pkgs["requests"][1] == "2.28.0"


def test_poetry_lock_hash_extracted():
    path = _write_tmp(".lock", POETRY_LOCK)
    pkgs = {p[0]: p for p in _parse_poetry_lock(path)}
    assert pkgs["requests"][2] == "sha256:abcdef1234"


def test_poetry_lock_no_files_hash_is_none():
    path = _write_tmp(".lock", POETRY_LOCK)
    pkgs = {p[0]: p for p in _parse_poetry_lock(path)}
    assert pkgs["flask"][2] is None


# ── Pipfile.lock ──────────────────────────────────────────────────────────────

PIPFILE_LOCK = {
    "_meta": {"hash": {"sha256": "abc"}},
    "default": {
        "requests": {
            "version": "==2.28.0",
            "hashes": ["sha256:abcdef1234", "sha256:deadbeef5678"],
        },
        "flask": {
            "version": "==3.0.0",
            "hashes": [],
        },
    },
    "develop": {
        "pytest": {
            "version": "==8.0.0",
            "hashes": ["sha256:pytest1234"],
        }
    },
}


def test_pipfile_lock_names():
    path = _write_tmp(".lock", json.dumps(PIPFILE_LOCK))
    pkgs = _parse_pipfile_lock(path)
    names = [p[0] for p in pkgs]
    assert "requests" in names
    assert "flask" in names
    assert "pytest" in names


def test_pipfile_lock_version():
    path = _write_tmp(".lock", json.dumps(PIPFILE_LOCK))
    pkgs = {p[0]: p for p in _parse_pipfile_lock(path)}
    assert pkgs["requests"][1] == "2.28.0"


def test_pipfile_lock_hash_extracted():
    path = _write_tmp(".lock", json.dumps(PIPFILE_LOCK))
    pkgs = {p[0]: p for p in _parse_pipfile_lock(path)}
    assert pkgs["requests"][2] == "sha256:abcdef1234"


def test_pipfile_lock_no_hashes_is_none():
    path = _write_tmp(".lock", json.dumps(PIPFILE_LOCK))
    pkgs = {p[0]: p for p in _parse_pipfile_lock(path)}
    assert pkgs["flask"][2] is None


def test_pipfile_lock_dev_deps_included():
    path = _write_tmp(".lock", json.dumps(PIPFILE_LOCK))
    pkgs = {p[0]: p for p in _parse_pipfile_lock(path)}
    assert "pytest" in pkgs
    assert pkgs["pytest"][2] == "sha256:pytest1234"
