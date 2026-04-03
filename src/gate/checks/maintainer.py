def check_maintainer_change(
    current: list[str],
    previous: list[str],
) -> dict:
    """
    Compare maintainer lists between two versions.
    Returns a dict describing any changes found.
    """
    current_set = set(current)
    previous_set = set(previous)

    added = current_set - previous_set
    removed = previous_set - current_set

    if not added and not removed:
        return {"ok": True, "added": [], "removed": []}

    return {
        "ok": False,
        "added": sorted(added),
        "removed": sorted(removed),
        "message": _format_message(added, removed),
    }


def _format_message(added: set[str], removed: set[str]) -> str:
    parts = []
    if added:
        parts.append(f"new maintainer(s): {', '.join(sorted(added))}")
    if removed:
        parts.append(f"removed maintainer(s): {', '.join(sorted(removed))}")
    return "; ".join(parts)
