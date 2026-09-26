from __future__ import annotations

import argparse
from pathlib import Path


FORBIDDEN_SUFFIXES = {
    ".xls", ".xlsx", ".xlsm", ".pbix", ".db", ".sqlite", ".sqlite3",
    ".parquet", ".feather", ".pkl", ".pickle", ".zip", ".7z", ".rar",
    ".p12", ".pfx", ".pem", ".key",
}

FORBIDDEN_BASENAMES = {
    ".env", "credentials.json", "secrets.json", "id_rsa", "id_ed25519",
}

PRIVATE_KEY_MARKERS = (
    "-----BEGIN PRIVATE KEY-----",
    "-----BEGIN RSA PRIVATE KEY-----",
    "-----BEGIN OPENSSH PRIVATE KEY-----",
    "-----BEGIN EC PRIVATE KEY-----",
)

APPROVED_CSV_PREFIXES = (
    "examples/",
    "evidence/templates/",
    "archive/legacy-scanners/",
)

SKIP_PARTS = {".git", "__pycache__", ".pytest_cache", ".venv", "venv"}


def iter_repository_files(root: Path):
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel = path.relative_to(root)
        if any(part in SKIP_PARTS for part in rel.parts):
            continue
        yield rel, path


def check_repository(root: str | Path = ".") -> list[str]:
    root = Path(root).resolve()
    violations: list[str] = []

    for rel, path in iter_repository_files(root):
        rel_posix = rel.as_posix()
        suffix = path.suffix.lower()
        basename = path.name.lower()

        if suffix in FORBIDDEN_SUFFIXES:
            violations.append(
                f"{rel_posix}: forbidden binary/archive extension {suffix}"
            )

        if basename in FORBIDDEN_BASENAMES:
            violations.append(
                f"{rel_posix}: forbidden credential/secrets filename"
            )

        if suffix == ".csv" and not rel_posix.startswith(APPROVED_CSV_PREFIXES):
            violations.append(
                f"{rel_posix}: CSV is outside approved synthetic/evidence locations"
            )

        try:
            if path.stat().st_size > 2_000_000:
                violations.append(
                    f"{rel_posix}: file exceeds 2 MB public-repository guardrail"
                )
                continue
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

        for marker in PRIVATE_KEY_MARKERS:
            if marker in text:
                violations.append(
                    f"{rel_posix}: private-key material marker detected"
                )

    return sorted(set(violations))


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Fail CI if repository content crosses the public-data boundary."
    )
    parser.add_argument("--root", default=".")
    args = parser.parse_args()

    violations = check_repository(args.root)
    if violations:
        print("PUBLIC BOUNDARY VIOLATIONS:")
        for violation in violations:
            print(f"- {violation}")
        raise SystemExit(1)

    print("public-data boundary check passed")


if __name__ == "__main__":
    main()
