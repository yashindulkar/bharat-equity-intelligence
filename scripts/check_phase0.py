"""Offline Phase 0 repository checks; uses only the Python standard library."""

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = (
    "AGENTS.md",
    "README.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
    ".gitignore",
    ".env.example",
    ".github/workflows/quality.yml",
    "docs/project/MASTER_PLAN.md",
    "docs/project/DEPENDENCY_GRAPH.md",
    "docs/project/ENVIRONMENT_ASSESSMENT.md",
    "docs/project/AGENT_TASKS.md",
    "docs/project/DECISION_LOG.md",
    "docs/project/RISK_REGISTER.md",
    "docs/project/OPEN_QUESTIONS.md",
    "docs/project/RELEASE_CHECKLIST.md",
    "docs/product/PRODUCT_REQUIREMENTS.md",
    "docs/architecture/SYSTEM_ARCHITECTURE.md",
    "docs/data/DATA_SOURCE_MATRIX.md",
    "docs/data/DATA_GOVERNANCE.md",
    "docs/compliance/REGULATORY_BOUNDARY.md",
    "docs/compliance/DATA_LICENSING_MATRIX.md",
    "docs/security/THREAT_MODEL.md",
    "docs/research/BACKTESTING_STANDARD.md",
    "docs/research/FACTOR_RESEARCH_STANDARD.md",
    "docs/risk/CAPITAL_PROTECTION_POLICY.md",
    "docs/agent-reviews/product-workflow.md",
    "docs/agent-reviews/data-licensing.md",
    "docs/agent-reviews/quantitative-point-in-time.md",
    "docs/agent-reviews/portfolio-capital-protection.md",
    "docs/agent-reviews/security-privacy-regulatory.md",
    "docs/agent-reviews/architecture-developer-experience.md",
)

missing = [path for path in REQUIRED if not (ROOT / path).is_file()]
assert not missing, f"missing required files: {missing}"
assert not any(
    (ROOT / ".env.example").read_text().splitlines()[i].split("=", 1)[1]
    for i, line in enumerate((ROOT / ".env.example").read_text().splitlines())
    if re.match(r".*(?:KEY|TOKEN|SECRET)=", line)
)
master = (ROOT / "MASTER_SPEC.md").read_text()
assert "Phase 0 — Discovery and governance" in master
assert "No production code beyond scaffolding" in master
broken_links: list[tuple[str, str]] = []
documents = [*ROOT.glob("*.md"), *(ROOT / "docs").rglob("*.md")]
for document in documents:
    for target in re.findall(r"\[[^]]+\]\(([^)]+)\)", document.read_text()):
        if target.startswith(("http://", "https://", "#")):
            continue
        resolved = (document.parent / target.split("#", 1)[0]).resolve()
        if not resolved.exists():
            broken_links.append((str(document.relative_to(ROOT)), target))
assert not broken_links, f"broken local links: {broken_links}"
print(
    f"PASS: {len(REQUIRED)} required files; env secret placeholders empty; "
    "master anchors and local links valid. This is not a full secret scan."
)
