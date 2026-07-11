.PHONY: check compile structure test lint typecheck

structure:
	PYTHONPATH=src python3 scripts/check_phase0.py

compile:
	python3 -m compileall -q scripts src tests

lint:
	python3 -m ruff check scripts src tests

typecheck:
	PYTHONPATH=src python3 -m mypy --strict scripts/check_phase0.py src/bharat_equity tests/unit/test_scaffold.py

test:
	PYTHONPATH=src pytest -q

check: structure compile lint typecheck test
