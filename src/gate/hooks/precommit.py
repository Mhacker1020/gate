import stat
from pathlib import Path

GATE_MARKER = "# gate pre-commit hook"
HOOK_SCRIPT = f"""{GATE_MARKER}
if git diff --cached --name-only | grep -qE '(package-lock\\.json|requirements\\.txt|Pipfile\\.lock|poetry\\.lock|pyproject\\.toml)'; then
    gate scan --hook || exit 1
fi
"""


def install_hook() -> tuple[bool, str]:
    git_dir = Path(".git")
    if not git_dir.exists():
        return False, "Not a git repository"

    hook_path = git_dir / "hooks" / "pre-commit"

    if hook_path.exists():
        content = hook_path.read_text()
        if GATE_MARKER in content:
            return True, "Hook already installed"
        with hook_path.open("a") as f:
            f.write("\n" + HOOK_SCRIPT)
    else:
        hook_path.write_text("#!/bin/sh\n" + HOOK_SCRIPT)

    current = hook_path.stat().st_mode
    hook_path.chmod(current | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    return True, "Hook installed"


def uninstall_hook() -> tuple[bool, str]:
    hook_path = Path(".git") / "hooks" / "pre-commit"
    if not hook_path.exists():
        return False, "No pre-commit hook found"

    content = hook_path.read_text()
    if GATE_MARKER not in content:
        return False, "Gate hook not found in pre-commit"

    lines = content.splitlines(keepends=True)
    filtered = []
    skip = False
    for line in lines:
        if GATE_MARKER in line:
            skip = True
        if skip and line.strip() == "fi":
            skip = False
            continue
        if not skip:
            filtered.append(line)

    hook_path.write_text("".join(filtered))
    return True, "Hook removed"
