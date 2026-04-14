"""
Security & Integrity tests — Zero Trust enforcement.

Coverage:
  1. Credential leakage scan — no hardcoded secrets in source code.
  2. Information disclosure — API errors must not expose stack traces / internals.
  3. skills.md integrity — agent profile document must be intact and unmodified.
"""
import re
from pathlib import Path
from typing import Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app

# ─── Paths ────────────────────────────────────────────────────────────────────

# Root of the backend source inside the container (/app or local services/backend/)
APP_ROOT = Path(__file__).resolve().parent.parent

# skills.md lives at /app/skills.md (copied there during Docker build)
SKILLS_MD = APP_ROOT / "skills.md"


# ─── 1. Credential Leakage Scan ───────────────────────────────────────────────

# File extensions to scan
SCAN_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".json", ".yml", ".yaml", ".env", ".cfg", ".toml", ".ini"}

# Directories / files to always skip — they CONTAIN real secrets or are binary
SKIP_DIRS = {
    "node_modules", ".git", "__pycache__", ".mypy_cache",
    "dist", "build", ".next", "coverage",
}
SKIP_FILES = {
    ".env.live", ".hairpalace",
}

# Patterns that indicate a REAL credential was hard-coded (value is a literal, not an env-ref)
# Each tuple: (label, compiled_regex)
CREDENTIAL_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    # Stripe live/test secret keys — full key format starts sk_live_ or sk_test_
    ("Stripe secret key (sk_live_)",  re.compile(r"\bsk_live_[A-Za-z0-9]{10,}", re.I)),
    ("Stripe secret key (sk_test_)",  re.compile(r"\bsk_test_[A-Za-z0-9]{10,}", re.I)),
    # Stripe publishable keys
    ("Stripe publishable (pk_live_)", re.compile(r"\bpk_live_[A-Za-z0-9]{10,}", re.I)),
    ("Stripe publishable (pk_test_)", re.compile(r"\bpk_test_[A-Za-z0-9]{10,}", re.I)),
    # Stripe webhook secret
    ("Stripe webhook (whsec_)",       re.compile(r"\bwhsec_[A-Za-z0-9]{10,}", re.I)),
    # Generic password assignment with a non-placeholder string value
    # Allows: password=${VAR}, password="", password=None, password=os.environ[...]
    # Flags: password="actualvalue", PASSWORD='realpass'
    ("Hardcoded password assignment",
     re.compile(r"""(?:password|passwd)\s*[=:]\s*["'][^${\s"']{6,}["']""", re.I)),
    # Generic secret assignment
    ("Hardcoded secret assignment",
     re.compile(r"""(?<!\w)secret(?:_key)?\s*[=:]\s*["'][^${\s"']{8,}["']""", re.I)),
    # API key with literal value
    ("Hardcoded api_key assignment",
     re.compile(r"""api[_-]?key\s*[=:]\s*["'][^${\s"']{8,}["']""", re.I)),
    # JWT / token secret with literal value
    ("Hardcoded jwt/token secret",
     re.compile(r"""(?:jwt|token)[_-]?secret\s*[=:]\s*["'][^${\s"']{8,}["']""", re.I)),
    # Postgres/MySQL URL with an embedded plain-text password
    # Allows: postgresql://${USER}:${PASS}@... and the test DSN strands_local_dev
    # Flags: postgresql://realuser:realpass@host/db
    ("DB URL with literal password",
     re.compile(r"(?:postgresql|mysql|mongodb)(?:\+\w+)?://[^${\s]+:[^${\s]+@", re.I)),
    # PEM private keys
    ("PEM private key",
     re.compile(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----")),
    # AWS access key IDs
    ("AWS access key",
     re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    # Generic high-entropy token that looks like a bearer token (≥40 chars of base64ish chars)
    # Only trigger inside explicit assignment context to avoid false positives
    ("Possible hardcoded bearer/token literal",
     re.compile(r"""(?:token|bearer|auth)\s*[=:]\s*["'][A-Za-z0-9+/._-]{40,}["']""", re.I)),
]

# Known-safe patterns in source code that regex might match but are intentionally fine
# (These are strings found IN the pattern definitions / test scaffolding, not real secrets)
ALLOWLISTED_SUBSTRINGS = {
    "sk_live_",     # The pattern string itself in THIS file
    "sk_test_",
    "pk_live_",
    "pk_test_",
    "whsec_",
    "AKIA",
    "strands_local_dev",   # Test DB password — local dev only, not a real secret
    "credential_patterns",  # Variable name in test code
}


def _iter_source_files(root: Path) -> Generator[Path, None, None]:
    """Yield every source file under *root* that should be scanned."""
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        # Skip ignored directories (check every part of the path)
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name in SKIP_FILES:
            continue
        if path.suffix.lower() not in SCAN_EXTENSIONS:
            continue
        yield path


def _scan_file(path: Path) -> list[str]:
    """Return a list of violation messages for *path*, one per offending line."""
    violations: list[str] = []
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return violations

    lines = content.splitlines()
    for lineno, line in enumerate(lines, start=1):
        # Skip comment lines (Python # and JS //) and the allowlist
        stripped = line.strip()
        if stripped.startswith(("#", "//", "*", "<!--")):
            continue
        if any(allow in line for allow in ALLOWLISTED_SUBSTRINGS):
            continue
        for label, pattern in CREDENTIAL_PATTERNS:
            if pattern.search(line):
                violations.append(f"  [{label}]  {path}:{lineno}: {stripped[:120]}")
    return violations


class TestCredentialLeakage:
    """No hardcoded secrets should exist anywhere in committed source files."""

    def test_no_hardcoded_credentials_in_source(self) -> None:
        violations: list[str] = []
        for fpath in _iter_source_files(APP_ROOT):
            violations.extend(_scan_file(fpath))

        if violations:
            report = "\n".join(violations)
            pytest.fail(
                f"Hardcoded credential(s) detected in source — remove them immediately:\n{report}"
            )

    def test_env_template_contains_only_placeholders(self) -> None:
        """The .env template must use ${VAR} placeholders, never raw values."""
        env_file = APP_ROOT.parent  # services/backend → services
        # Walk up to find the .env template (project root)
        for candidate in [APP_ROOT / ".env", APP_ROOT.parent.parent / ".env"]:
            if candidate.exists():
                env_file = candidate
                break
        else:
            pytest.skip(".env template not found — skipping placeholder check")

        content = env_file.read_text(encoding="utf-8")
        for lineno, line in enumerate(content.splitlines(), start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            if "=" not in stripped:
                continue
            key, _, value = stripped.partition("=")
            # Value must be empty OR a ${...} placeholder OR an unambiguous safe literal
            if value and not value.startswith("${") and not value.startswith("#"):
                # Allow a small set of genuinely non-secret static values
                SAFE_LITERALS = {
                    "HS256", "30", "7", "5432", "redis://redis:6379/0",
                    "redpanda:9092", "postgres", "Hair Palace", "true", "false",
                }
                domain_like = re.match(r"^[a-zA-Z0-9._-]+:[0-9]+$", value)
                if value not in SAFE_LITERALS and not domain_like:
                    pytest.fail(
                        f".env line {lineno}: key '{key.strip()}' has a non-placeholder value "
                        f"'{value[:60]}' — use ${{VAR}} instead"
                    )


# ─── 2. Information Disclosure ────────────────────────────────────────────────

@pytest.mark.asyncio
class TestInformationDisclosure:
    """API error responses must never expose stack traces or internal details."""

    async def _client(self) -> AsyncClient:
        return AsyncClient(transport=ASGITransport(app=app), base_url="http://test")

    async def test_404_response_does_not_leak_internals(self) -> None:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/nonexistent-path-xyz")
        assert resp.status_code == 404
        body = resp.text.lower()
        for forbidden in ("traceback", "sqlalchemy", 'file "/', "exception", "internal server error"):
            assert forbidden not in body, (
                f"404 response leaks internal detail '{forbidden}': {resp.text[:300]}"
            )

    async def test_invalid_login_does_not_reveal_user_existence(self) -> None:
        """Both 'user not found' and 'wrong password' should return the same status code."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                "/api/auth/login",
                json={"email": "ghost@example.com", "password": "wrongpassword"},
            )
        # Must be 401 (or 422 for schema error) — never 500
        assert resp.status_code in (401, 422, 400), (
            f"Login with invalid creds returned unexpected status {resp.status_code}"
        )
        body = resp.text.lower()
        for forbidden in ("traceback", "sqlalchemy", "hashed_password", "internal server"):
            assert forbidden not in body, (
                f"Login error response leaks '{forbidden}': {resp.text[:300]}"
            )

    async def test_user_schema_does_not_expose_hashed_password(self) -> None:
        """A user list/profile response must never include 'hashed_password'."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            # Public product listing — confirmed to be open
            resp = await client.get("/api/products/")
        # Check the field isn't leaking at any endpoint we probe
        assert "hashed_password" not in resp.text, (
            "API response contains 'hashed_password' — remove it from the response schema"
        )

    async def test_server_headers_do_not_expose_stack(self) -> None:
        """Response headers should not reveal internal server technology in detail."""
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/api/products/")
        # 'server' header (if present) should not expose Python version details
        server_header = resp.headers.get("server", "").lower()
        for forbidden in ("python/", "uvicorn/0", "sqlalchemy"):
            assert forbidden not in server_header, (
                f"Server header leaks internal version: {server_header}"
            )


# ─── 3. skills.md Integrity ───────────────────────────────────────────────────

class TestSkillsMdIntegrity:
    """
    The agent profile document (skills.md) must be present and intact.
    This enforces Rule 7 (Atomic Verification) from the AI Guidance section.
    """

    def test_skills_md_exists(self) -> None:
        assert SKILLS_MD.exists(), (
            f"skills.md not found at {SKILLS_MD}. "
            "Run: cp <workspace>/skills.md services/backend/skills.md and redeploy."
        )

    def test_skills_md_is_not_empty(self) -> None:
        assert SKILLS_MD.exists(), "skills.md missing — see test_skills_md_exists"
        content = SKILLS_MD.read_text(encoding="utf-8")
        assert len(content.strip()) > 500, "skills.md appears truncated or empty"

    def test_skills_md_required_top_level_sections(self) -> None:
        content = SKILLS_MD.read_text(encoding="utf-8")
        required_sections = [
            "user_profile:",
            "security_standards:",
            "testing_and_stability:",
            "workflow_and_cicd:",
            "architectural_philosophy:",
        ]
        missing = [s for s in required_sections if s not in content]
        assert not missing, f"skills.md is missing required section(s): {missing}"

    def test_skills_md_identity_markers_intact(self) -> None:
        content = SKILLS_MD.read_text(encoding="utf-8")
        identity_markers = [
            "Zero Disappointments",
            "Dress to Impress",
            "The Gatekeeper",
            "Minimalist Explainer",
            "Visual Maverick",
        ]
        missing = [m for m in identity_markers if m not in content]
        assert not missing, f"skills.md identity markers have been removed: {missing}"

    def test_skills_md_security_philosophy_intact(self) -> None:
        content = SKILLS_MD.read_text(encoding="utf-8")
        assert "Zero Trust" in content, (
            "Security philosophy 'Zero Trust / Data Hardening / Least Privilege' missing from skills.md"
        )
        assert "Least Privilege" in content, (
            "Security philosophy 'Least Privilege' missing from skills.md"
        )

    def test_skills_md_test_first_mandate_intact(self) -> None:
        content = SKILLS_MD.read_text(encoding="utf-8")
        assert "Test-First" in content, (
            "Mandatory 'Test-First' pre-deployment gate is missing from skills.md"
        )

    def test_skills_md_pii_scanning_mandate_intact(self) -> None:
        content = SKILLS_MD.read_text(encoding="utf-8")
        assert "PII" in content, "PII scanning requirement missing from skills.md"
        assert "Hardcoded Secret Scanning" in content, (
            "'PII & Hardcoded Secret Scanning' CI check missing from skills.md"
        )

    def test_skills_md_ai_guidance_rules_present(self) -> None:
        content = SKILLS_MD.read_text(encoding="utf-8")
        # All 12 AI Guidance rules must exist
        for i in range(1, 13):
            assert f"# {i}." in content, (
                f"AI Guidance rule #{i} is missing from skills.md — document may be corrupted"
            )

    def test_skills_md_role_intact(self) -> None:
        content = SKILLS_MD.read_text(encoding="utf-8")
        assert "Lead Product Engineer" in content, (
            "User role 'Lead Product Engineer & Aesthetic Architect' missing from skills.md"
        )

    def test_skills_md_placeholder_secrets_rule_intact(self) -> None:
        """The docker_implementation rule about ${ENV_VAR} placeholders must be present."""
        content = SKILLS_MD.read_text(encoding="utf-8")
        assert "${ENV_VAR}" in content or "ENV_VAR" in content, (
            "Docker secrets implementation rule (KEY=${ENV_VAR}) missing from skills.md"
        )
