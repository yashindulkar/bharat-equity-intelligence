from pathlib import Path


def test_fixtures_are_synthetic_and_contain_no_secret_markers() -> None:
    text = Path("src/bharat_equity/providers/synthetic.py").read_text()
    assert "SYNTHETIC" in text
    for marker in ("BEGIN PRIVATE KEY", "AKIA", "ghp_"):
        assert marker not in text
