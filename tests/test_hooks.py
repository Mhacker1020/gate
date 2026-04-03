import os
import stat
import tempfile
from pathlib import Path
from unittest.mock import patch

from gate.hooks.precommit import install_hook, uninstall_hook, GATE_MARKER


def _make_git_repo(tmp: str) -> Path:
    root = Path(tmp)
    (root / ".git" / "hooks").mkdir(parents=True)
    return root


def test_install_creates_hook():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_git_repo(tmp)
        with patch("gate.hooks.precommit.Path") as mock_path:
            # Run with real filesystem in temp dir
            pass

        # Test directly by changing cwd
        original = os.getcwd()
        try:
            os.chdir(root)
            ok, msg = install_hook()
            assert ok is True
            hook = root / ".git" / "hooks" / "pre-commit"
            assert hook.exists()
            assert GATE_MARKER in hook.read_text()
            # Executable bit set on Unix; chmod is a no-op on Windows NTFS
            if os.name != "nt":
                assert hook.stat().st_mode & stat.S_IXUSR
        finally:
            os.chdir(original)


def test_install_is_idempotent():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_git_repo(tmp)
        original = os.getcwd()
        try:
            os.chdir(root)
            install_hook()
            ok, msg = install_hook()
            assert ok is True
            assert "already" in msg
            # Marker appears only once
            content = (root / ".git" / "hooks" / "pre-commit").read_text()
            assert content.count(GATE_MARKER) == 1
        finally:
            os.chdir(original)


def test_install_appends_to_existing_hook():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_git_repo(tmp)
        hook = root / ".git" / "hooks" / "pre-commit"
        hook.write_text("#!/bin/sh\necho existing\n")
        original = os.getcwd()
        try:
            os.chdir(root)
            ok, _ = install_hook()
            assert ok is True
            content = hook.read_text()
            assert "existing" in content
            assert GATE_MARKER in content
        finally:
            os.chdir(original)


def test_install_fails_outside_git_repo():
    with tempfile.TemporaryDirectory() as tmp:
        original = os.getcwd()
        try:
            os.chdir(tmp)
            ok, msg = install_hook()
            assert ok is False
        finally:
            os.chdir(original)


def test_uninstall_removes_hook():
    with tempfile.TemporaryDirectory() as tmp:
        root = _make_git_repo(tmp)
        original = os.getcwd()
        try:
            os.chdir(root)
            install_hook()
            ok, msg = uninstall_hook()
            assert ok is True
            content = (root / ".git" / "hooks" / "pre-commit").read_text()
            assert GATE_MARKER not in content
        finally:
            os.chdir(original)
