.PHONY: check test lint typecheck

check:
	PYTHONPATH=src python3 scripts/check_phase0.py
	PYTHONPATH=src pytest -q

test:
	PYTHONPATH=src pytest -q

lint: check

typecheck: check
