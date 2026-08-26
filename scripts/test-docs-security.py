#!/usr/bin/env python3
"""Mutation-sensitive tests for the Pages artifact boundary."""

from __future__ import annotations

import hashlib
import importlib.util
import io
import stat
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path, PurePosixPath
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parent.parent
CHECKER = ROOT / "scripts/check-docs-site.py"
WORKFLOW = ROOT / ".github/workflows/pages.yml"
DEPLOY_CONDITION = (
    "if: github.ref == 'refs/heads/main' && github.event_name != 'pull_request'"
)

SPEC = importlib.util.spec_from_file_location("docs_site_checker", CHECKER)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load {CHECKER}")
CHECKER_MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECKER_MODULE)


class DocumentationArtifactSecurityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.site = self.root / "site"
        marker_html = (
            "<!doctype html><title>EPD</title>"
            "ISO 22057:2022 BeyondSystemBoundary "
            "Domain model versus exchange formats Annex B maps information "
            "Versioned provider adapters "
            "Added an automated GitHub Pages site"
        )
        for relative in (
            "index.html",
            "architecture/index.html",
            "roadmap/index.html",
            "changelog/index.html",
            "api/index.html",
            "api/openbim_epd/index.html",
            "api/openbim_ilcd_epd/index.html",
        ):
            path = self.site / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(marker_html, encoding="utf-8")
        search = self.site / "search/search_index.json"
        search.parent.mkdir(parents=True)
        search.write_text("{}", encoding="utf-8")
        (self.site / "LICENSE.txt").write_bytes((ROOT / "LICENSE").read_bytes())
        (self.site / ".nojekyll").touch()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    @property
    def archive(self) -> Path:
        return self.root / "artifact.tar"

    def run_checker(
        self,
        *,
        package: bool = False,
        site: Path | None = None,
    ) -> subprocess.CompletedProcess[str]:
        command = [sys.executable, str(CHECKER), str(site or self.site)]
        if package:
            command.append(str(self.archive))
        return subprocess.run(command, text=True, capture_output=True, check=False)

    def assert_rejected(self, expected_message: str) -> None:
        result = self.run_checker(package=True)
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(expected_message, result.stderr)
        self.assertFalse(self.archive.exists())

    @staticmethod
    def add_archive_root(packaged: tarfile.TarFile, name: str = ".") -> None:
        root = tarfile.TarInfo(name)
        root.type = tarfile.DIRTYPE
        root.mode = 0o755
        packaged.addfile(root)

    def test_packages_only_verified_files_and_directories(self) -> None:
        result = self.run_checker(package=True)
        self.assertEqual(result.returncode, 0, result.stderr)

        with tarfile.open(self.archive, "r:") as packaged:
            members = packaged.getmembers()
        self.assertTrue(members)
        self.assertTrue(all(member.isfile() or member.isdir() for member in members))
        for member in members:
            self.assertEqual(member.mode, 0o755 if member.isdir() else 0o644)
            self.assertEqual(member.mtime, 0)
            self.assertEqual((member.uid, member.gid), (0, 0))
            self.assertEqual((member.uname, member.gname, member.linkname), ("", "", ""))
            self.assertEqual(member.pax_headers, {})
        self.assertEqual(
            {member.name for member in members},
            {
                ".",
                "./.nojekyll",
                "./LICENSE.txt",
                "./api",
                "./api/index.html",
                "./api/openbim_epd",
                "./api/openbim_epd/index.html",
                "./api/openbim_ilcd_epd",
                "./api/openbim_ilcd_epd/index.html",
                "./architecture",
                "./architecture/index.html",
                "./changelog",
                "./changelog/index.html",
                "./index.html",
                "./roadmap",
                "./roadmap/index.html",
                "./search",
                "./search/search_index.json",
            },
        )

    def test_rejects_directory_symlink_before_packaging(self) -> None:
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "restricted.pdf").write_bytes(b"restricted")
        (self.site / "references").symlink_to(outside, target_is_directory=True)
        self.assert_rejected("symlink is forbidden")

    def test_rejects_file_symlink_before_packaging(self) -> None:
        outside = self.root / "restricted.pdf"
        outside.write_bytes(b"restricted")
        (self.site / "leak.html").symlink_to(outside)
        self.assert_rejected("symlink is forbidden")

    def test_rejects_hard_link_before_packaging(self) -> None:
        outside = self.root / "restricted"
        outside.write_bytes(b"restricted")
        (self.site / "leak.html").hardlink_to(outside)
        self.assert_rejected("hard-linked file is forbidden")

    def test_rejects_unexpected_artifact_types(self) -> None:
        for name in (
            "reference.xml",
            "reference.zip",
            "reference.csv",
            "reference.docx",
            "reference",
            "references/restricted.html",
            "notes.html",
        ):
            with self.subTest(name=name):
                path = self.site / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b"restricted")
                self.assert_rejected("unexpected artifact type or path")
                path.unlink()

    def test_rejects_restricted_binary_renamed_as_html(self) -> None:
        path = self.site / "api/restricted.html"
        path.write_bytes(b"%PDF-1.7\nrestricted")
        self.assert_rejected("restricted binary signature")

    def test_requires_exact_project_license(self) -> None:
        license_path = self.site / "LICENSE.txt"
        license_path.unlink()
        self.assert_rejected("missing required outputs: LICENSE.txt")

        license_path.write_text("MIT-ish", encoding="utf-8")
        self.assert_rejected("published project license does not match repository LICENSE")

    def test_requires_nojekyll(self) -> None:
        (self.site / ".nojekyll").unlink()
        self.assert_rejected("missing required outputs: .nojekyll")

    def test_requires_canonical_markers(self) -> None:
        (self.site / "index.html").write_text(
            "<!doctype html><title>wrong project</title>",
            encoding="utf-8",
        )
        self.assert_rejected("canonical marker is absent")

    def test_rejects_broken_local_links(self) -> None:
        with (self.site / "index.html").open("a", encoding="utf-8") as output:
            output.write('<a href="missing/">missing</a>')
        self.assert_rejected("broken local links")

    def test_filesystem_boundary_guards_are_enforced(self) -> None:
        regular = SimpleNamespace(
            st_mode=stat.S_IFREG | 0o644,
            st_nlink=1,
            st_dev=2,
        )
        directory = SimpleNamespace(st_mode=stat.S_IFDIR | 0o755, st_dev=2)
        with self.assertRaises(CHECKER_MODULE.ArtifactError):
            CHECKER_MODULE.validate_regular_stat(regular, 1, "api/leak.html")
        with self.assertRaises(CHECKER_MODULE.ArtifactError):
            CHECKER_MODULE.validate_directory_stat(directory, 1, "api/leak")

    def test_archive_hash_equality_is_enforced(self) -> None:
        _site, snapshot = CHECKER_MODULE.scan_site(str(self.site))
        CHECKER_MODULE.create_archive(snapshot, self.archive)
        expected = {
            relative: hashlib.sha256(payload).hexdigest()
            for relative, payload in snapshot.items()
        }
        expected["index.html"] = "0" * 64
        with self.assertRaises(CHECKER_MODULE.ArtifactError):
            CHECKER_MODULE.verify_archive(self.archive, expected)

    def test_post_scan_file_substitution_cannot_change_archive(self) -> None:
        _site, snapshot = CHECKER_MODULE.scan_site(str(self.site))
        expected = snapshot["api/openbim_epd/index.html"]
        (self.site / "api/openbim_epd/index.html").write_bytes(
            b"%PDF-1.7\npost-validation substitution"
        )

        CHECKER_MODULE.create_archive(snapshot, self.archive)
        with tarfile.open(self.archive, "r:") as packaged:
            packaged_file = packaged.extractfile("./api/openbim_epd/index.html")
            self.assertIsNotNone(packaged_file)
            self.assertEqual(packaged_file.read(), expected)

    def test_post_scan_directory_substitution_cannot_add_external_files(self) -> None:
        _site, snapshot = CHECKER_MODULE.scan_site(str(self.site))
        original_api = self.site / "api-original"
        (self.site / "api").rename(original_api)
        outside = self.root / "outside"
        outside.mkdir()
        (outside / "restricted.pdf").write_bytes(b"restricted")
        (self.site / "api").symlink_to(outside, target_is_directory=True)

        CHECKER_MODULE.create_archive(snapshot, self.archive)
        with tarfile.open(self.archive, "r:") as packaged:
            names = {member.name for member in packaged.getmembers()}
        expected_names = {"."}
        expected_names.update(f"./{directory}" for directory in CHECKER_MODULE.archive_directories(snapshot) if directory != ".")
        expected_names.update(f"./{relative}" for relative in snapshot)
        self.assertEqual(names, expected_names)
        self.assertNotIn("./api/restricted.pdf", names)

    def test_rejects_symlinked_site_ancestor(self) -> None:
        real_parent = self.root / "real-parent"
        real_parent.mkdir()
        moved_site = real_parent / "site"
        self.site.rename(moved_site)
        alias = self.root / "alias"
        alias.symlink_to(real_parent, target_is_directory=True)

        result = self.run_checker(package=True, site=alias / "site")
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("site path contains a symlink component", result.stderr)
        self.assertFalse(self.archive.exists())

    def test_requires_api_landing_page(self) -> None:
        (self.site / "api/index.html").unlink()
        self.assert_rejected("missing required outputs: api/index.html")

    def test_requires_adapter_api_landing_page(self) -> None:
        (self.site / "api/openbim_ilcd_epd/index.html").unlink()
        self.assert_rejected(
            "missing required outputs: api/openbim_ilcd_epd/index.html"
        )

    def test_requires_empty_marker_files(self) -> None:
        (self.site / ".nojekyll").write_text("confidential", encoding="utf-8")
        self.assert_rejected("marker file must be empty: .nojekyll")

    def test_rejects_html_without_doctype(self) -> None:
        path = self.site / "api/restricted.html"
        path.write_text("confidential plaintext", encoding="utf-8")
        self.assert_rejected("HTML output has an unexpected signature")

    def test_positive_content_validators_reject_malformed_assets(self) -> None:
        fixtures = (
            ("api/crates.js", b"confidential plaintext", "JavaScript output is not syntactically valid"),
            ("assets/stylesheets/extra.css", b"confidential plaintext", "CSS output has no declaration block"),
            ("search/search_index.json", b"not json", "JSON output is not syntactically valid"),
            ("api/static.files/favicon-12345678.svg", b"not svg", "SVG output is not well-formed XML"),
            ("assets/images/favicon.png", b"not png", "PNG output has an unexpected signature"),
            ("api/static.files/FiraSans-Regular-12345678.woff2", b"not a font", "WOFF2 output has an unexpected signature"),
            ("assets/javascripts/bundle.12345678.min.js.map", b"not a map", "JSON output is not syntactically valid"),
        )
        for relative, payload, expected in fixtures:
            with self.subTest(relative=relative):
                path = self.site / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                original = path.read_bytes() if path.exists() else None
                path.write_bytes(payload)
                self.assert_rejected(expected)
                if original is None:
                    path.unlink()
                else:
                    path.write_bytes(original)

    def test_allows_exact_second_crate_rustdoc_outputs(self) -> None:
        allowed = (
            "api/openbim_ilcd_epd/sidebar-items.js",
            "api/search.desc/openbim_ilcd_epd/openbim_ilcd_epd-desc-0-.js",
            "api/static.files/FiraMono-Medium-12345678.woff2",
            "api/static.files/FiraSans-Italic-12345678.woff2",
            "api/static.files/SourceSerif4-Semibold-12345678.ttf.woff2",
        )
        for relative in allowed:
            with self.subTest(relative=relative):
                self.assertTrue(
                    CHECKER_MODULE.is_allowed_api_file(PurePosixPath(relative))
                )

    def test_rejects_unknown_api_javascript_path(self) -> None:
        path = self.site / "api/restricted.js"
        path.write_text('const confidential = "secret";\n', encoding="utf-8")
        self.assert_rejected("unexpected artifact type or path: api/restricted.js")

    def test_archive_path_safety_is_enforced(self) -> None:
        payload = b"validated"
        with tarfile.open(self.archive, "w") as packaged:
            member = tarfile.TarInfo("./../escape")
            member.size = len(payload)
            packaged.addfile(member, io.BytesIO(payload))
        expected = {"../escape": hashlib.sha256(payload).hexdigest()}
        with self.assertRaisesRegex(CHECKER_MODULE.ArtifactError, "unsafe archive member path"):
            CHECKER_MODULE.verify_archive(self.archive, expected)

    def test_archive_root_spelling_is_exact(self) -> None:
        with tarfile.open(self.archive, "w") as packaged:
            self.add_archive_root(packaged, "./.")
        with self.assertRaisesRegex(
            CHECKER_MODULE.ArtifactError,
            "archive root member must be named exactly",
        ):
            CHECKER_MODULE.verify_archive(self.archive, {})

    def test_archive_rejects_duplicate_missing_and_extra_members(self) -> None:
        payload = b"validated"
        digest = hashlib.sha256(payload).hexdigest()

        with self.subTest(case="duplicate-root"):
            with tarfile.open(self.archive, "w") as packaged:
                self.add_archive_root(packaged)
                self.add_archive_root(packaged)
            with self.assertRaisesRegex(CHECKER_MODULE.ArtifactError, "duplicate archive member"):
                CHECKER_MODULE.verify_archive(self.archive, {})

        with self.subTest(case="duplicate-file"):
            with tarfile.open(self.archive, "w") as packaged:
                self.add_archive_root(packaged)
                for _ in range(2):
                    member = tarfile.TarInfo("./target")
                    member.size = len(payload)
                    packaged.addfile(member, io.BytesIO(payload))
            with self.assertRaisesRegex(CHECKER_MODULE.ArtifactError, "duplicate archive member"):
                CHECKER_MODULE.verify_archive(self.archive, {"target": digest})

        with self.subTest(case="duplicate-nested-directory"):
            with tarfile.open(self.archive, "w") as packaged:
                self.add_archive_root(packaged)
                for _ in range(2):
                    directory = tarfile.TarInfo("./nested")
                    directory.type = tarfile.DIRTYPE
                    directory.mode = 0o755
                    packaged.addfile(directory)
                member = tarfile.TarInfo("./nested/target")
                member.size = len(payload)
                packaged.addfile(member, io.BytesIO(payload))
            with self.assertRaisesRegex(CHECKER_MODULE.ArtifactError, "duplicate archive member"):
                CHECKER_MODULE.verify_archive(self.archive, {"nested/target": digest})

        with self.subTest(case="missing-file"):
            with tarfile.open(self.archive, "w") as packaged:
                self.add_archive_root(packaged)
            with self.assertRaisesRegex(
                CHECKER_MODULE.ArtifactError,
                "archive differs from validated site snapshot",
            ):
                CHECKER_MODULE.verify_archive(self.archive, {"target": digest})

        with self.subTest(case="extra-file"):
            with tarfile.open(self.archive, "w") as packaged:
                self.add_archive_root(packaged)
                member = tarfile.TarInfo("./extra")
                member.size = len(payload)
                packaged.addfile(member, io.BytesIO(payload))
            with self.assertRaisesRegex(CHECKER_MODULE.ArtifactError, "unexpected archive file"):
                CHECKER_MODULE.verify_archive(self.archive, {})

        with self.subTest(case="extra-directory"):
            with tarfile.open(self.archive, "w") as packaged:
                self.add_archive_root(packaged)
                directory = tarfile.TarInfo("./extra")
                directory.type = tarfile.DIRTYPE
                directory.mode = 0o755
                packaged.addfile(directory)
            with self.assertRaisesRegex(CHECKER_MODULE.ArtifactError, "unexpected archive directory"):
                CHECKER_MODULE.verify_archive(self.archive, {})

    def test_archive_requires_pages_root_prefix(self) -> None:
        payload = b"validated"
        with tarfile.open(self.archive, "w") as packaged:
            self.add_archive_root(packaged)
            member = tarfile.TarInfo("target")
            member.size = len(payload)
            packaged.addfile(member, io.BytesIO(payload))
        expected = {"target": hashlib.sha256(payload).hexdigest()}
        with self.assertRaisesRegex(
            CHECKER_MODULE.ArtifactError,
            "archive member does not use the required ./ root",
        ):
            CHECKER_MODULE.verify_archive(self.archive, expected)

    def test_archive_directory_topology_is_enforced(self) -> None:
        payload = b"validated"
        with tarfile.open(self.archive, "w") as packaged:
            self.add_archive_root(packaged)
            member = tarfile.TarInfo("./api/target")
            member.size = len(payload)
            packaged.addfile(member, io.BytesIO(payload))
        expected = {"api/target": hashlib.sha256(payload).hexdigest()}
        with self.assertRaisesRegex(
            CHECKER_MODULE.ArtifactError,
            "archive directory topology differs from Pages contract",
        ):
            CHECKER_MODULE.verify_archive(self.archive, expected)

    def test_archive_metadata_is_deterministic(self) -> None:
        cases = (
            ("mode", "mode", 0o700, "unexpected mode"),
            ("mtime", "mtime", 1, "unexpected mtime"),
            ("uid", "uid", 1, "unexpected ownership metadata"),
            ("gid", "gid", 1, "unexpected ownership metadata"),
            ("uname", "uname", "owner", "unexpected ownership metadata"),
            ("gname", "gname", "group", "unexpected ownership metadata"),
            ("linkname", "linkname", "target", "unexpected link target"),
            ("pax", "pax_headers", {"comment": "forbidden"}, "unexpected PAX metadata"),
        )
        for case, attribute, value, diagnostic in cases:
            with self.subTest(case=case):
                with tarfile.open(self.archive, "w", format=tarfile.PAX_FORMAT) as packaged:
                    root = tarfile.TarInfo(".")
                    root.type = tarfile.DIRTYPE
                    root.mode = 0o755
                    setattr(root, attribute, value)
                    packaged.addfile(root)
                with self.assertRaisesRegex(CHECKER_MODULE.ArtifactError, diagnostic):
                    CHECKER_MODULE.verify_archive(self.archive, {})

    def test_archive_non_file_types_are_rejected(self) -> None:
        payload = b"validated"
        digest = hashlib.sha256(payload).hexdigest()
        member_types = (
            tarfile.SYMTYPE,
            tarfile.LNKTYPE,
            tarfile.CHRTYPE,
            tarfile.BLKTYPE,
            tarfile.FIFOTYPE,
        )
        for member_type in member_types:
            with self.subTest(member_type=member_type):
                with tarfile.open(self.archive, "w") as packaged:
                    self.add_archive_root(packaged)
                    member = tarfile.TarInfo("./target")
                    member.size = len(payload)
                    packaged.addfile(member, io.BytesIO(payload))
                    alias = tarfile.TarInfo("./alias")
                    alias.type = member_type
                    if member_type in (tarfile.SYMTYPE, tarfile.LNKTYPE):
                        alias.linkname = "./target"
                    packaged.addfile(alias)
                expected = {"target": digest, "alias": digest}
                with self.assertRaisesRegex(
                    CHECKER_MODULE.ArtifactError,
                    "neither a regular file nor directory",
                ):
                    CHECKER_MODULE.verify_archive(self.archive, expected)

    def test_workflow_uploads_checked_archive_only_from_main(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")
        condition_lines = [
            line.strip() for line in workflow.splitlines() if line.strip().startswith("if:")
        ]
        self.assertEqual(condition_lines, [DEPLOY_CONDITION, DEPLOY_CONDITION])
        stripped_lines = [line.strip() for line in workflow.splitlines()]
        self.assertEqual(
            [line for line in stripped_lines if line.startswith("path:")],
            ["path: target/artifact.tar"],
        )
        self.assertEqual(stripped_lines.count("name: github-pages"), 2)
        self.assertEqual(stripped_lines.count("needs: build"), 1)
        self.assertNotIn("actions/upload-pages-artifact@", workflow)
        self.assertEqual(
            [line for line in stripped_lines if "upload-artifact@" in line],
            [
                "uses: actions/upload-artifact@"
                "ea165f8d65b6e75b540449e92b4886f43607fa02 # v4.6.2"
            ],
        )
        self.assertEqual(
            [line for line in stripped_lines if "deploy-pages@" in line],
            [
                "uses: actions/deploy-pages@"
                "cd2ce8fcbc39b97be8ca5fce6e763baed58fa128 # v5.0.0"
            ],
        )


if __name__ == "__main__":
    unittest.main()
