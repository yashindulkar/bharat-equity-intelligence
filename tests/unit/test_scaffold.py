"""Phase 0 smoke tests; no market or investment behavior."""


def test_package_imports() -> None:
    import bharat_equity

    assert "production behavior" in (bharat_equity.__doc__ or "")
