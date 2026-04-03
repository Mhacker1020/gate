import argparse
import json
import sys
from pathlib import Path

from gate import __version__
from gate.config import load_config, Config
from gate.registry import pypi, npm
from gate.checks.quarantine import check_quarantine
from gate.checks.cve import check_cve
from gate.hooks.precommit import install_hook, uninstall_hook
import gate.output as out


# ── Result helpers ────────────────────────────────────────────────────────────

def _check_package(name: str, version: str | None, ecosystem: str, config: Config) -> dict:
    result: dict = {"errors": [], "warnings": [], "version": None}

    if ecosystem == "PyPI":
        info = pypi.get_package_info(name, version)
    else:
        info = npm.get_package_info(name, version)

    if info is None:
        result["errors"].append("Package not found in registry")
        return result

    result["version"] = info["version"]

    # Quarantine
    q = check_quarantine(info.get("published"), config.quarantine_days)
    if not q["ok"]:
        if "recent_release" in config.fail_on:
            result["errors"].append(q["message"])
        else:
            result["warnings"].append(q["message"])

    # CVE
    for v in check_cve(name, info["version"], ecosystem):
        result["errors"].append(f"{v['id']}: {v['summary'][:72]}")

    # Install scripts (npm)
    if ecosystem == "npm":
        for script_name, cmd in info.get("install_scripts", {}).items():
            msg = f"install script [{script_name}]: {cmd[:60]}"
            if "install_script" in config.fail_on:
                result["errors"].append(msg)
            else:
                result["warnings"].append(msg)

    return result


def _print_result(name: str, result: dict) -> None:
    ver = result.get("version") or ""
    label = out.bold(name) + (f" {out.dim(ver)}" if ver else "")

    if result["errors"]:
        out.fail(label)
        for msg in result["errors"]:
            out.error(msg)
    elif result["warnings"]:
        out.warn(label)
        for msg in result["warnings"]:
            out.warning(msg)
    else:
        out.ok(label)


# ── Parsers ───────────────────────────────────────────────────────────────────

def _parse_requirements(path: Path) -> list[tuple[str, str | None]]:
    packages = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith(("#", "-", "git+", "http")):
            continue
        for sep in ("==", ">=", "<=", "~=", "!=", ">", "<"):
            if sep in line:
                name = line.split(sep)[0].strip()
                version = line.split("==")[1].strip() if "==" in line else None
                packages.append((name, version))
                break
        else:
            packages.append((line, None))
    return packages


def _parse_package_lock(path: Path) -> list[tuple[str, str | None]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    packages = []
    for pkg_path, pkg_data in data.get("packages", {}).items():
        if not pkg_path:
            continue
        name = pkg_path.removeprefix("node_modules/")
        packages.append((name, pkg_data.get("version")))
    return packages


def _detect_project() -> tuple[list[tuple[str, str | None]], str] | None:
    if Path("requirements.txt").exists():
        return _parse_requirements(Path("requirements.txt")), "PyPI"
    if Path("package-lock.json").exists():
        return _parse_package_lock(Path("package-lock.json")), "npm"
    return None


# ── Commands ──────────────────────────────────────────────────────────────────

def cmd_init(args: argparse.Namespace) -> None:
    ok_flag, msg = install_hook()
    if ok_flag:
        out.ok(msg)
    else:
        print(out.red(f"✗ {msg}"), file=sys.stderr)
        sys.exit(1)


def cmd_uninstall(args: argparse.Namespace) -> None:
    ok_flag, msg = uninstall_hook()
    if ok_flag:
        out.ok(msg)
    else:
        out.warn(msg)


def cmd_check(args: argparse.Namespace) -> None:
    config = load_config()
    ecosystem = "npm" if args.npm else "PyPI"

    if "==" in args.package:
        name, version = args.package.split("==", 1)
    else:
        name, version = args.package, None

    print()
    result = _check_package(name, version, ecosystem, config)
    _print_result(name, result)
    print()

    if result["errors"] and not args.force:
        sys.exit(1)


def cmd_scan(args: argparse.Namespace) -> None:
    config = load_config()
    detected = _detect_project()

    if detected is None:
        out.warn("No requirements.txt or package-lock.json found")
        sys.exit(0)

    packages, ecosystem = detected

    if not args.hook:
        print(f"\nScanning {out.bold(str(len(packages)))} {ecosystem} packages...\n")

    errors = 0
    warnings = 0

    for name, version in packages:
        result = _check_package(name, version, ecosystem, config)
        _print_result(name, result)
        errors += len(result["errors"])
        warnings += len(result["warnings"])

    print()
    if errors:
        print(out.red(f"✗ {errors} error(s)") + f", {warnings} warning(s)")
        print(out.dim("Use --force to override and proceed anyway"))
        if not args.force:
            sys.exit(1)
    elif warnings:
        print(out.green("✓ 0 errors") + f", {out.yellow(f'{warnings} warning(s)')}")
    else:
        print(out.green(f"✓ All {len(packages)} packages passed"))


# ── Entry point ───────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(
        prog="gate",
        description="Supply chain security scanner for npm and pip packages",
    )
    parser.add_argument("--version", action="version", version=f"gate {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("init", help="Install git pre-commit hook")
    sub.add_parser("uninstall", help="Remove git pre-commit hook")

    p_check = sub.add_parser("check", help="Check a single package")
    p_check.add_argument("package", help="Package name or name==version")
    p_check.add_argument("--npm", action="store_true", help="Treat as npm package")
    p_check.add_argument("--force", action="store_true", help="Exit 0 even on errors")

    p_scan = sub.add_parser("scan", help="Scan all packages in lock file")
    p_scan.add_argument("--force", action="store_true", help="Exit 0 even on errors")
    p_scan.add_argument("--hook", action="store_true", help=argparse.SUPPRESS)

    args = parser.parse_args()

    commands = {
        "init": cmd_init,
        "uninstall": cmd_uninstall,
        "check": cmd_check,
        "scan": cmd_scan,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
