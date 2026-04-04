# gate

> A supply chain security tool that trusts its own supply chain is not a security tool.

Gate scans npm and pip packages **before** they enter your project — catching threats that traditional vulnerability scanners miss.

```
$ gate check requests

  ⚠ requests 2.33.0
    Published 3 day(s) ago (quarantine window: 7 days)

$ gate check event-stream --npm

  ✗ event-stream 3.3.6
    install script [postinstall]: node -e "..."
      suspicious: eval execution, hardcoded URL
```

[![CI](https://github.com/Mhacker1020/gate/actions/workflows/ci.yml/badge.svg)](https://github.com/Mhacker1020/gate/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/gate-cli)](https://pypi.org/project/gate-cli/)
![Python 3.12+](https://img.shields.io/badge/python-3.12%2B-blue)
![Zero dependencies](https://img.shields.io/badge/dependencies-zero-brightgreen)

## The problem

Most supply chain attacks don't exploit known CVEs. They work in the gap between a malicious package being published and being detected — a window that can last hours or days.

During that window:

- A typosquatted package runs arbitrary code on `pip install`
- A compromised maintainer account pushes a backdoored version
- An install script exfiltrates environment variables or SSH keys

Tools like Trivy, Snyk, and Dependabot catch *known* vulnerabilities. Gate catches what they miss.

## How it works

Gate runs six checks on every package:

| Check | What it catches |
|-------|----------------|
| **CVE scan** | Known vulnerabilities via [OSV.dev](https://osv.dev) |
| **Quarantine window** | Versions published within N days — too new to be trusted |
| **Install script inspection** | npm packages running suspicious hooks (`curl`, `eval`, `base64`, hardcoded IPs...) |
| **Maintainer change** | Flags when package ownership has changed between versions |
| **Hash verification** | Detects tampered packages via lock file integrity checks |
| **SBOM export** | Generates a CycloneDX 1.6 Software Bill of Materials |

The quarantine window is the key insight: a package published 2 hours ago has not been reviewed by the community, scanned by security researchers, or flagged by automated systems. Gate makes that visible.

**Zero runtime dependencies.** Gate is implemented using Python's standard library only — no third-party packages that could themselves be compromised.

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

Gate automatically detects your lock file:

```bash
gate scan
```

Supported lock files: `poetry.lock`, `Pipfile.lock`, `requirements.txt`, `package-lock.json`

Exit code is non-zero if errors are found — suitable for CI pipelines.

### Export a CycloneDX SBOM

```bash
gate scan --sbom                  # print to stdout
gate scan --sbom report.cdx.json  # write to file
```

### Install as a git pre-commit hook

```bash
gate init
```

Gate will run automatically on every `git commit` when lock files change. To remove:

```bash
gate uninstall
```

## Configuration

Create `.gate.toml` in your project root:

```toml
quarantine_days = 14

fail_on = ["critical_cve", "install_script"]
warn_on = ["recent_release", "maintainer_change"]
```

| Option | Default | Description |
|--------|---------|-------------|
| `quarantine_days` | `7` | Days a new release must age before passing |
| `fail_on` | `["critical_cve", "install_script"]` | Conditions that fail the scan (exit 1) |
| `warn_on` | `["recent_release", "maintainer_change"]` | Conditions that warn but allow through |

Move `recent_release` to `fail_on` to strictly enforce the quarantine window.

## Supported ecosystems

| Ecosystem | Lock files | Registry |
|-----------|-----------|----------|
| PyPI | `poetry.lock`, `Pipfile.lock`, `requirements.txt` | pypi.org |
| npm | `package-lock.json` | registry.npmjs.org |

CVE data is sourced from [OSV.dev](https://osv.dev) — Google's open vulnerability database.

## Contributing

```bash
git clone https://github.com/Mhacker1020/gate
cd gate
pip install -e ".[dev]"
python -m pytest
```

## License

MIT
