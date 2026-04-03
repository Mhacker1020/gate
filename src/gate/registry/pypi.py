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

    files = releases[version]
    upload_time = min(
        datetime.fromisoformat(f["upload_time"]).replace(tzinfo=timezone.utc)
        for f in files
        if f.get("upload_time")
    )

    # PyPI exposes the uploader username per file
    uploaders = list({f["uploader"] for f in files if f.get("uploader")})

    # Prefer the source distribution hash, fall back to first wheel
    remote_integrity = None
    sdist = next((f for f in files if f.get("packagetype") == "sdist"), None)
    ref = sdist or files[0]
    sha256 = ref.get("digests", {}).get("sha256")
    if sha256:
        remote_integrity = f"sha256:{sha256}"

    previous_uploaders = _get_previous_uploaders(releases, version)

    return {
        "name": data["info"]["name"],
        "version": version,
        "published": upload_time,
        "home_page": data["info"].get("home_page"),
        "maintainers": uploaders,
        "previous_maintainers": previous_uploaders,
        "remote_integrity": remote_integrity,
    }


def _get_previous_uploaders(releases: dict, current_version: str) -> list[str] | None:
    """Return uploaders from the release published just before current_version."""
    def earliest_upload(files: list) -> datetime | None:
        times = [
            datetime.fromisoformat(f["upload_time"]).replace(tzinfo=timezone.utc)
            for f in files
            if f.get("upload_time")
        ]
        return min(times) if times else None

    current_time = earliest_upload(releases.get(current_version, []))
    if not current_time:
        return None

    candidates = []
    for ver, files in releases.items():
        if ver == current_version or not files:
            continue
        t = earliest_upload(files)
        if t and t < current_time:
            candidates.append((t, files))

    if not candidates:
        return None

    _, prev_files = max(candidates, key=lambda x: x[0])
    return list({f["uploader"] for f in prev_files if f.get("uploader")}) or None
