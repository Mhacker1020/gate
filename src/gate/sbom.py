import json
import uuid
from datetime import datetime, timezone

from gate import __version__


def _purl(name: str, version: str, ecosystem: str) -> str:
    """Generate a Package URL (purl) per the purl spec."""
    if ecosystem == "npm":
        # Scoped packages: @scope/name → pkg:npm/%40scope%2Fname@version
        encoded = name.replace("@", "%40").replace("/", "%2F")
        return f"pkg:npm/{encoded}@{version}"
    return f"pkg:pypi/{name.lower()}@{version}"


def generate(
    packages: list[dict],
    ecosystem: str,
) -> dict:
    """
    Generate a CycloneDX 1.6 SBOM document.

    Each entry in packages is a result dict from _check_package(), extended with
    'name' and 'version' keys added by cmd_scan before calling this function.
    """
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    serial = f"urn:uuid:{uuid.uuid4()}"

    components = []
    vulnerabilities = []

    for pkg in packages:
        name = pkg["name"]
        version = pkg.get("version") or "unknown"
        ref = f"urn:cdx:{uuid.uuid4()}"

        component: dict = {
            "type": "library",
            "bom-ref": ref,
            "name": name,
            "version": version,
            "purl": _purl(name, version, ecosystem),
        }
        components.append(component)

        # Attach CVEs as top-level vulnerabilities linked to this component
        for msg in pkg.get("errors", []) + pkg.get("warnings", []):
            # Extract CVE/GHSA IDs from error messages like "CVE-2023-xxx: ..."
            for prefix in ("CVE-", "GHSA-"):
                if msg.startswith(prefix):
                    vuln_id = msg.split(":")[0].strip()
                    description = msg.split(":", 1)[1].strip() if ":" in msg else ""
                    vulnerabilities.append({
                        "id": vuln_id,
                        "description": description,
                        "affects": [{"ref": ref}],
                    })
                    break

    doc = {
        "bomFormat": "CycloneDX",
        "specVersion": "1.6",
        "serialNumber": serial,
        "version": 1,
        "metadata": {
            "timestamp": now,
            "tools": [{"name": "gate", "version": __version__}],
        },
        "components": components,
    }

    if vulnerabilities:
        doc["vulnerabilities"] = vulnerabilities

    return doc


def write(doc: dict, path: str | None) -> None:
    """Write SBOM to file or stdout."""
    output = json.dumps(doc, indent=2)
    if path:
        with open(path, "w", encoding="utf-8") as f:
            f.write(output)
    else:
        print(output)
