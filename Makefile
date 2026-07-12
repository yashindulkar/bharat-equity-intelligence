.PHONY: setup check compile structure format test test-unit test-property test-leakage test-integration test-security lint typecheck build audit secret-scan demo

setup:
	python3 -m pip install --disable-pip-version-check -r requirements-dev.txt
	uv sync --frozen --extra dev

structure:
	PYTHONPATH=src python3 scripts/check_phase0.py

compile:
	python3 -m compileall -q scripts src tests

lint:
	python3 -m ruff check scripts src tests

format:
	python3 -m ruff format --check scripts src tests

typecheck:
	PYTHONPATH=src python3 -m mypy --strict scripts src

test:
	PYTHONPATH=src pytest -q

test-unit:
	PYTHONPATH=src pytest -q tests/unit
test-property:
	PYTHONPATH=src pytest -q tests/property
test-leakage:
	PYTHONPATH=src pytest -q tests/leakage
test-integration:
	PYTHONPATH=src pytest -q tests/integration
test-security:
	PYTHONPATH=src pytest -q tests/security

build:
	python3 -m build

audit:
	uv export --frozen --extra dev --no-emit-project --format requirements-txt --output-file /tmp/bharat-audit-requirements.txt
	uv run --frozen --extra dev pip-audit -r /tmp/bharat-audit-requirements.txt

secret-scan:
	gitleaks git --redact --config .gitleaks.toml .

demo:
	PYTHONPATH=src python3 -m bharat_equity.cli --json

check: structure compile format lint typecheck test
