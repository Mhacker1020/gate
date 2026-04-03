import json
import urllib.request
import urllib.error
from datetime import datetime, timezone


def get_package_info(name: str, version: str | None = None) -> dict | None:
    encoded = name.replace("/", "%2F")
    url = f"https://registry.npmjs.org/{encoded}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None

    if version is None:
        version = data.get("dist-tags", {}).get("latest")

    if not version or version not in data.get("versions", {}):
        return None

    version_data = data["versions"][version]
    time_str = data.get("time", {}).get(version)
    published = None
    if time_str:
        published = datetime.fromisoformat(time_str.replace("Z", "+00:00"))

    all_scripts = version_data.get("scripts", {})
    install_scripts = {
        k: v for k, v in all_scripts.items()
        if k in ("install", "preinstall", "postinstall", "preuninstall", "postuninstall")
    }

    current_maintainers = _extract_maintainers(version_data.get("maintainers", []))
    previous_maintainers = _get_previous_maintainers(data, version)

    # dist.integrity is the canonical hash from the registry
    remote_integrity = version_data.get("dist", {}).get("integrity")

    return {
        "name": data["name"],
        "version": version,
        "published": published,
        "install_scripts": install_scripts,
        "maintainers": current_maintainers,
        "previous_maintainers": previous_maintainers,
        "remote_integrity": remote_integrity,
    }


def _extract_maintainers(maintainers: list) -> list[str]:
    return [
        m["name"] if isinstance(m, dict) else str(m)
        for m in maintainers
    ]


def _get_previous_maintainers(data: dict, current_version: str) -> list[str] | None:
    """Return maintainer list from the version published just before current_version."""
    times: dict[str, str] = data.get("time", {})
    versions_with_time = {
        v: t for v, t in times.items()
        if v not in ("created", "modified") and v in data.get("versions", {})
    }

    if not versions_with_time:
        return None

    current_time = versions_with_time.get(current_version)
    if not current_time:
        return None

    earlier = [
        v for v, t in versions_with_time.items()
        if t < current_time and v != current_version
    ]

    if not earlier:
        return None

    prev_version = max(earlier, key=lambda v: versions_with_time[v])
    prev_data = data["versions"].get(prev_version, {})
    return _extract_maintainers(prev_data.get("maintainers", []))
