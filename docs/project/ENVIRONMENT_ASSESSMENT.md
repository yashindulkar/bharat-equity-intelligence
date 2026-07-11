# Phase 0 Environment Assessment

Observed on 2026-07-11; these facts describe one workstation and are not permanent project
requirements.

| Item | Observation |
|---|---|
| Operating system | macOS 26.4.1, Apple Silicon |
| Git | 2.50.1 |
| Python | 3.12.4 |
| Node/npm | Node 26.4.0 / npm 11.17.0; not selected for Phase 0 |
| Docker CLI | 28.0.4 present; daemon/build not validated |
| Make | GNU Make 3.81 |
| Initial Python tools | mypy and pytest present; Ruff and `uv` absent before the correction pass |

The correction pass installs the exact Phase 0 tool and resolved dependency versions into an ignored
`.venv` before validation. CI installs those same versions from `requirements-dev.txt`. A hashed lock,
supported-OS matrix, Node LTS selection, container validation, and application package manager are
Phase 1 decisions.

## Correction-pass validation notes

All repository-local Markdown links resolved on 2026-07-11. External authoritative URLs were checked:
CERT-In, RBI, BSE, MeitY and SEBI returned HTTP 200; NSE URLs returned HTTP 200 after an HTTP/1.1
browser-style retry. The MCA policy PDF returned HTTP 403 from its anti-bot edge, so automated reachability
could not be confirmed even though the authoritative URL is retained. External-link availability is not
a deterministic CI gate because official sites may block automated clients.
