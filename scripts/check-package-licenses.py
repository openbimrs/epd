#!/usr/bin/env python3
"""Verify that each generated crate carries the exact project licence texts and
notice, and declare the dual-licence expression."""

from __future__ import annotations

import os
import sys
import tarfile
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SHIPPED = ("LICENSE", "NOTICE", "LICENSES/LicenseRef-Commercial.txt")
ROOT_FILES = {name: (ROOT / name).read_bytes() for name in SHIPPED}
EXPRESSION = "AGPL-3.0-or-later OR LicenseRef-Commercial"
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

        if package["license"] != EXPRESSION:
            fail(f"{name} must declare license = {EXPRESSION!r}")

        with tarfile.open(archive, mode="r:gz") as packaged:
            for shipped, expected in ROOT_FILES.items():
                expected_member = f"{archive_root}/{shipped}"
                members = [member for member in packaged.getmembers() if member.name == expected_member]
                if len(members) != 1 or not members[0].isfile():
                    fail(f"{archive.name} must contain exactly one regular {expected_member}")
                extracted = packaged.extractfile(members[0])
                if extracted is None or extracted.read() != expected:
                    fail(f"{archive.name} {shipped} does not match the repository root")
            packaged_manifest = packaged.extractfile(f"{archive_root}/Cargo.toml")
            if packaged_manifest is None or tomllib.loads(packaged_manifest.read().decode("utf-8"))["package"]["license"] != EXPRESSION:
                fail(f"{archive.name} Cargo.toml has an unexpected license expression")

    print(f"verified exact dual-licence texts and expression in {len(PACKAGES)} crate archives")


if __name__ == "__main__":
    main()
