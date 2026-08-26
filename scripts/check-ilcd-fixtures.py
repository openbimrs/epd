#!/usr/bin/env python3
"""Verify the exact, redistributable ILCD+EPD XML fixture mirror."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path, PurePosixPath

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "openbim-ilcd-epd/tests/fixtures/upstream-v1.3"
MANIFEST = FIXTURES / "SHA256SUMS"
EXPECTED_AUXILIARY = {
    "SHA256SUMS",
    "SOURCE.md",
    "UPSTREAM-LICENSE-APACHE-2.0.txt",
}


def fail(message: str) -> None:
    raise SystemExit(f"ILCD+EPD fixture check failed: {message}")


def main() -> None:
    expected: dict[str, str] = {}
    for line_number, raw_line in enumerate(
        MANIFEST.read_text(encoding="utf-8").splitlines(), start=1
    ):
        if not raw_line or raw_line.startswith("#"):
            continue
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", raw_line)
        if match is None:
            fail(f"malformed SHA256SUMS line {line_number}")
        digest, relative = match.groups()
        path = PurePosixPath(relative)
        if path.is_absolute() or ".." in path.parts or path.suffix != ".xml":
            fail(f"unsafe or non-XML manifest path: {relative}")
        if relative in expected:
            fail(f"duplicate manifest path: {relative}")
        expected[relative] = digest

    actual_paths = {
        path.relative_to(FIXTURES).as_posix()
        for path in FIXTURES.rglob("*.xml")
        if path.is_file()
    }
    if len(expected) != 45 or actual_paths != set(expected):
        fail(
            f"manifest/corpus mismatch: manifest={len(expected)}, "
            f"actual={len(actual_paths)}"
        )

    for relative, expected_digest in expected.items():
        actual_digest = hashlib.sha256((FIXTURES / relative).read_bytes()).hexdigest()
        if actual_digest != expected_digest:
            fail(f"SHA-256 mismatch: {relative}")

    auxiliary = {
        path.relative_to(FIXTURES).as_posix()
        for path in FIXTURES.iterdir()
        if path.is_file() and path.suffix != ".xml"
    }
    if auxiliary != EXPECTED_AUXILIARY:
        fail(f"unexpected top-level fixture files: {sorted(auxiliary)}")

    source = (FIXTURES / "SOURCE.md").read_text(encoding="utf-8")
    if "7625c7dfc0d5b6bc2020eb0cf0b0503349c914aa" not in source:
        fail("SOURCE.md does not pin the audited upstream commit")
    license_text = (FIXTURES / "UPSTREAM-LICENSE-APACHE-2.0.txt").read_text(
        encoding="utf-8"
    )
    if "Apache License" not in license_text or "Version 2.0" not in license_text:
        fail("upstream Apache-2.0 license notice is missing")

    print(f"verified {len(expected)} exact ILCD+EPD XML fixtures")


if __name__ == "__main__":
    main()
