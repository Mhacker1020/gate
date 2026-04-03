# gate

Supply chain security scanner for npm and pip packages.

Checks packages for known CVEs, quarantines newly published versions, and warns about install scripts — before they hit your project.

```
  ✓ flask 3.1.1
  ✗ requests 2.28.0
    CVE-2023-32681: Unintended leak of Proxy-Authorization header
  ⚠ urllib3 2.3.0
    Published 2 day(s) ago (quarantine window: 7 days)
```

## Why

Supply chain attacks increasingly target the window between a package being published and being detected as malicious. Existing tools (Trivy, Snyk, Dependabot) catch *known* CVEs but miss:

- Newly published malicious versions not yet in any database
- Maintainer takeovers
- Install scripts that run arbitrary code on `pip install`

Gate adds a quarantine window — new versions are flagged until the community has had time to catch problems.

**Zero runtime dependencies.** A supply chain security tool that trusts its own supply chain is not a security tool.

## Installation

```bash
pip install gate-cli
```

Requires Python 3.12+.

## Usage

### Check a single package

```bash
gate check requests
gate check requests==2.28.0
gate check lodash --npm
gate check lodash==4.17.15 --npm
```

### Scan all packages in a project

Automatically detects `requirements.txt` or `package-lock.json`:

```bash
gate scan
```

Exit code is non-zero if errors are found — suitable for CI pipelines.

### Install as a git pre-commit hook

```bash
gate init
```

Gate will run automatically on every `git commit` when lock files change. To remove:

```bash
gate uninstall
```

## Configuration

Create `.gate.toml` in your project root to override defaults:

```toml
quarantine_days = 14

fail_on = ["critical_cve", "install_script"]
warn_on = ["recent_release"]
```

| Option | Default | Description |
|--------|---------|-------------|
| `quarantine_days` | `7` | Days a new release must age before passing |
| `fail_on` | `["critical_cve", "install_script"]` | Conditions that block the commit / exit 1 |
| `warn_on` | `["recent_release"]` | Conditions that warn but allow through |

Move `recent_release` from `warn_on` to `fail_on` to enforce the quarantine window strictly.

## Supported ecosystems

| Ecosystem | Lock file | Registry |
|-----------|-----------|----------|
| PyPI | `requirements.txt` | pypi.org |
| npm | `package-lock.json` | registry.npmjs.org |

CVE data is sourced from [OSV.dev](https://osv.dev) — Google's open vulnerability database.

## Checks

| Check | What it catches |
|-------|----------------|
| CVE scan | Known vulnerabilities via OSV.dev |
| Quarantine window | Versions published within N days |
| Install scripts | npm packages with `postinstall`/`preinstall` hooks |

## Contributing

Gate is open source and built for the community. Contributions welcome.

```bash
git clone https://github.com/mikavihreala/gate
cd gate
pip install -e ".[dev]"
python -m pytest
```

## License

MIT
