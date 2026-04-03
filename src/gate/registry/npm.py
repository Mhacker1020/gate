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

    return {
        "name": data["name"],
        "version": version,
        "published": published,
        "install_scripts": install_scripts,
    }
