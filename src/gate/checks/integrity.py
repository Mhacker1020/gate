def check_integrity(local: str, remote: str) -> dict:
    """
    Compare a locally stored integrity hash against the value from the registry.

    Both values are expected in standard format:
      npm:  "sha512-<base64>"
      PyPI: "sha256:<hex>"
    """
    if not local or not remote:
        return {"ok": True, "skipped": True, "message": "No hash to compare"}

    match = local.strip() == remote.strip()
    return {
        "ok": match,
        "skipped": False,
        "local": local,
        "remote": remote,
        "message": None if match else "Hash mismatch — package may have been tampered with",
    }


def parse_requirements_hashes(path) -> dict[str, dict[str, str]]:
    """
    Parse hashes from a requirements.txt file that was generated with
    pip-compile --generate-hashes or pip install --require-hashes.

    Returns: {package_name_lower: {version: "sha256:<hex>"}}

    Example line:
        requests==2.28.0 \\
            --hash=sha256:ae72a32d...
    """
    import re
    from pathlib import Path

    text = Path(path).read_text(encoding="utf-8")
    # Join continuation lines
    text = re.sub(r"\\\n\s*", " ", text)

    result: dict[str, dict[str, str]] = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            continue

        # Extract name==version
        spec_part = line.split()[0]
        name, version = spec_part.split("==", 1)
        name = name.strip().lower()
        version = version.strip()

        # Extract first sha256 hash
        match = re.search(r"--hash=sha256:([a-f0-9]+)", line)
        if match:
            result.setdefault(name, {})[version] = f"sha256:{match.group(1)}"

    return result
