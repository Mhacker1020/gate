from gate.checks.maintainer import check_maintainer_change


def test_no_change():
    result = check_maintainer_change(["alice", "bob"], ["alice", "bob"])
    assert result["ok"] is True
    assert result["added"] == []
    assert result["removed"] == []


def test_new_maintainer_added():
    result = check_maintainer_change(["alice", "bob", "eve"], ["alice", "bob"])
    assert result["ok"] is False
    assert "eve" in result["added"]
    assert result["removed"] == []
    assert "eve" in result["message"]


def test_maintainer_removed():
    result = check_maintainer_change(["alice"], ["alice", "bob"])
    assert result["ok"] is False
    assert "bob" in result["removed"]
    assert result["added"] == []


def test_maintainer_replaced():
    result = check_maintainer_change(["eve"], ["alice"])
    assert result["ok"] is False
    assert "eve" in result["added"]
    assert "alice" in result["removed"]


def test_empty_previous():
    # First release — no previous to compare against
    result = check_maintainer_change(["alice"], [])
    assert result["ok"] is False
    assert "alice" in result["added"]


def test_order_does_not_matter():
    result = check_maintainer_change(["bob", "alice"], ["alice", "bob"])
    assert result["ok"] is True
