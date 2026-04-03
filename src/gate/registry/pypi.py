import json
import urllib.request
import urllib.error
from datetime import datetime, timezone


def get_package_info(name: str, version: str | None = None) -> dict | None:
    url = f"https://pypi.org/pypi/{name}/json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read())
    except urllib.error.HTTPError:
        return None
    except Exception:
        return None

    if version is None:
        version = data["info"]["version"]

    releases = data.get("releases", {})
    if version not in releases or not releases[version]:
        return None

    upload_time = min(
        datetime.fromisoformat(f["upload_time"]).replace(tzinfo=timezone.utc)
        for f in releases[version]
        if f.get("upload_time")
    )

    return {
        "name": data["info"]["name"],
        "version": version,
        "published": upload_time,
        "home_page": data["info"].get("home_page"),
    }
