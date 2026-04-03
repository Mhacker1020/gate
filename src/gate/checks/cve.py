import json
import urllib.request
import urllib.error

OSV_API = "https://api.osv.dev/v1/query"


def check_cve(name: str, version: str, ecosystem: str) -> list[dict]:
    payload = json.dumps({
        "package": {"name": name, "ecosystem": ecosystem},
        "version": version,
    }).encode()

    req = urllib.request.Request(
        OSV_API,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
    except Exception:
        return []

    seen: set[str] = set()
    vulns = []
    for vuln in data.get("vulns", []):
        cve_id = next(
            (a for a in vuln.get("aliases", []) if a.startswith("CVE-")),
            vuln.get("id", ""),
        )
        if cve_id in seen:
            continue
        seen.add(cve_id)
        vulns.append({
            "id": cve_id,
            "summary": vuln.get("summary", "No description"),
        })

    return vulns
