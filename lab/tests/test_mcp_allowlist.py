from pathlib import Path

import yaml

ALLOWED_SAMPLE = {"docs.search", "vector.search"}


def test_allowlist_contains_promoted_tools():
    cfg = yaml.safe_load(Path("config/mcp/allowlist.yaml").read_text(encoding="utf-8"))
    assert "allow" in cfg and isinstance(cfg["allow"], list)
    allow = set(cfg["allow"])
    # positive assertions: promoted tools present
    assert ALLOWED_SAMPLE.issubset(allow), f"Missing tools: {ALLOWED_SAMPLE - allow}"


def test_allowlist_denies_non_listed_tool():
    cfg = yaml.safe_load(Path("config/mcp/allowlist.yaml").read_text(encoding="utf-8"))
    allow = set(cfg.get("allow", []))
    assert "system.shell" not in allow  # sentinel: should remain disallowed
