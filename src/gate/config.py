from dataclasses import dataclass, field
from pathlib import Path
import tomllib


@dataclass
class Config:
    quarantine_days: int = 7
    fail_on: list[str] = field(default_factory=lambda: ["critical_cve", "install_script"])
    warn_on: list[str] = field(default_factory=lambda: ["recent_release", "maintainer_change"])


def load_config(path: Path | None = None) -> Config:
    if path is None:
        path = Path(".gate.toml")

    if not path.exists():
        return Config()

    with path.open("rb") as f:
        data = tomllib.load(f)

    return Config(
        quarantine_days=data.get("quarantine_days", 7),
        fail_on=data.get("fail_on", ["critical_cve", "install_script"]),
        warn_on=data.get("warn_on", ["recent_release"]),
    )
