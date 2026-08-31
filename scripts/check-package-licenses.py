#!/usr/bin/env python3
"""Verify that each generated crate carries the exact project AGPL notice."""

from __future__ import annotations

import os
import sys
import tarfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT_LICENSE = (ROOT / "LICENSE").read_bytes()
PACKAGES = (ROOT / "openbim-epd", ROOT / "openbim-ilcd-epd")
TARGET_DIR = Path(os.environ.get("CARGO_TARGET_DIR", ROOT / "target"))
if not TARGET_DIR.is_absolute():
    TARGET_DIR = ROOT / TARGET_DIR


def fail(message: str) -> None:
    print(f"package license check failed: {message}", file=sys.stderr)
    raise SystemExit(1)


def main() -> None:
    for package_dir in PACKAGES:
        manifest = tomllib.loads((package_dir / "Cargo.toml").read_text(encoding="utf-8"))
        package = manifest["package"]
        name = package["name"]
        version = package["version"]
        archive_root = f"{name}-{version}"
        archive = TARGET_DIR / "package" / f"{archive_root}.crate"
        if not archive.is_file():
            fail(f"missing package archive: {archive}")

        with tarfile.open(archive, mode="r:gz") as packaged:
            expected_member = f"{archive_root}/LICENSE"
            members = [member for member in packaged.getmembers() if member.name == expected_member]
            if len(members) != 1 or not members[0].isfile():
                fail(f"{archive.name} must contain exactly one regular {expected_member}")
            extracted = packaged.extractfile(members[0])
            if extracted is None or extracted.read() != PROJECT_LICENSE:
                fail(f"{archive.name} license does not match repository LICENSE")

    print(f"verified exact AGPL-3.0-or-later license in {len(PACKAGES)} crate archives")


if __name__ == "__main__":
    main()
