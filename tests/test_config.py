import tempfile
from pathlib import Path

from gate.config import load_config, Config


def test_defaults_when_no_file():
    with tempfile.TemporaryDirectory() as tmp:
        config = load_config(Path(tmp) / ".gate.toml")

    assert config.quarantine_days == 7
    assert "critical_cve" in config.fail_on
    assert "install_script" in config.fail_on
    assert "recent_release" in config.warn_on


def test_loads_custom_quarantine_days():
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False, mode="w") as f:
        f.write("quarantine_days = 14\n")
        path = Path(f.name)

    try:
        config = load_config(path)
        assert config.quarantine_days == 14
    finally:
        path.unlink()


def test_loads_custom_fail_on():
    with tempfile.NamedTemporaryFile(suffix=".toml", delete=False, mode="w") as f:
        f.write('fail_on = ["critical_cve"]\n')
        path = Path(f.name)

    try:
        config = load_config(path)
        assert config.fail_on == ["critical_cve"]
        assert "install_script" not in config.fail_on
    finally:
        path.unlink()


def test_default_config_is_dataclass():
    config = Config()
    assert isinstance(config, Config)
