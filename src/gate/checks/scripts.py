import re

# Patterns that indicate a script is doing something suspicious
_SUSPICIOUS: list[tuple[str, str]] = [
    (r"\bcurl\b",           "network fetch (curl)"),
    (r"\bwget\b",           "network fetch (wget)"),
    (r"\bfetch\b",          "network fetch (fetch)"),
    (r"\bbase64\b",         "base64 encoding"),
    (r"atob\s*\(",          "base64 decode (atob)"),
    (r"Buffer\.from\b",     "binary decoding (Buffer.from)"),
    (r"\beval\s*\(",        "eval execution"),
    (r"Function\s*\(",      "dynamic code execution (Function)"),
    (r"\bexec\s*\(",        "shell execution (exec)"),
    (r"\bspawn\s*\(",       "shell execution (spawn)"),
    (r"\bchild_process\b",  "child process usage"),
    (r"https?://",          "hardcoded URL"),
    (r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "hardcoded IP address"),
    (r"\bpowershell\b",     "PowerShell execution"),
    (r"\bchmod\b",          "permission change"),
    (r"process\.env\b",     "environment variable access"),
]


def analyze_script(script: str) -> list[str]:
    """Return a list of suspicious pattern descriptions found in the script."""
    found = []
    for pattern, description in _SUSPICIOUS:
        if re.search(pattern, script, re.IGNORECASE):
            found.append(description)
    return found


def check_install_scripts(install_scripts: dict[str, str]) -> dict:
    """
    Analyze install scripts for suspicious patterns.
    Returns a dict with 'ok', 'findings' (per script), and 'suspicious' flag.
    """
    if not install_scripts:
        return {"ok": True, "findings": {}}

    findings: dict[str, list[str]] = {}
    for script_name, script_body in install_scripts.items():
        patterns = analyze_script(script_body)
        if patterns:
            findings[script_name] = patterns

    return {
        "ok": len(findings) == 0,
        "findings": findings,
        "raw": install_scripts,
    }
