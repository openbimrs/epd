#!/usr/bin/env python3
"""Validate a Pages site and optionally create its exact upload archive.

All generated files are read through pinned directory file descriptors before
packaging. The archive is therefore built from the validated byte snapshot, not
from paths that can be substituted after validation.
"""

from __future__ import annotations

import hashlib
import gzip
import io
import json
import os
import posixpath
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree

REQUIRED = (
    "index.html",
    "architecture/index.html",
    "roadmap/index.html",
    "changelog/index.html",
    "api/index.html",
    "api/openbim_epd/index.html",
    "search/search_index.json",
    ".nojekyll",
)
ROOT_FILES = {
    ".nojekyll",
    "404.html",
    "index.html",
    "sitemap.xml",
    "sitemap.xml.gz",
}
PAGE_FILES = {
    "architecture/index.html",
    "changelog/index.html",
    "roadmap/index.html",
}
RUSTDOC_SPECIAL_FILES = {"api/.lock"}
RUSTDOC_STATIC_PREFIXES = {
    "main",
    "scrape-examples",
    "search",
    "settings",
    "src-script",
    "storage",
}
RUSTDOC_CSS_PREFIXES = {"normalize", "noscript", "rustdoc"}
RUSTDOC_IMAGE_PREFIXES = {"favicon", "favicon-32x32", "rust-logo"}
RUSTDOC_FONT_PREFIXES = {
    "FiraSans-Medium",
    "FiraSans-Regular",
    "NanumBarunGothic",
    "SourceCodePro-It",
    "SourceCodePro-Regular",
    "SourceCodePro-Semibold",
    "SourceSerif4-Bold",
    "SourceSerif4-It",
    "SourceSerif4-Regular",
}
RUSTDOC_LICENSE_PREFIXES = {
    "COPYRIGHT",
    "FiraSans-LICENSE",
    "LICENSE-APACHE",
    "LICENSE-MIT",
    "NanumBarunGothic-LICENSE",
    "SourceCodePro-LICENSE",
    "SourceSerif4-LICENSE",
}
LUNR_MODULES = {
    "ar", "da", "de", "du", "el", "es", "fi", "fr", "he", "hi", "hu",
    "hy", "it", "ja", "jp", "kn", "ko", "multi", "nl", "no", "pt", "ro",
    "ru", "sa", "stemmer.support", "sv", "ta", "te", "th", "tr", "vi", "zh",
}
FORBIDDEN_SIGNATURES = (
    b"%PDF-",
    b"PK\x03\x04",  # ZIP, including XLSX and DOCX containers.
    b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1",  # Legacy OLE documents.
)
PAGE_MARKERS = {
    "index.html": ("ISO 22057:2022", "BeyondSystemBoundary"),
    "architecture/index.html": (
        "Domain model versus exchange formats",
        "Annex B maps information",
    ),
    "roadmap/index.html": ("Versioned provider adapters",),
    "changelog/index.html": ("Added an automated GitHub Pages site",),
}


class ArtifactError(Exception):
    """A generated site or archive violated the publication contract."""


def fail(message: str) -> None:
    raise ArtifactError(message)


def hashed_name_matches(name: str, prefixes: set[str], suffix: str) -> bool:
    alternatives = "|".join(re.escape(prefix) for prefix in sorted(prefixes, key=len, reverse=True))
    return re.fullmatch(rf"(?:{alternatives})-[0-9a-f]{{8}}{re.escape(suffix)}", name) is not None


def is_allowed_api_file(path: PurePosixPath) -> bool:
    relative = path.as_posix()
    if relative in RUSTDOC_SPECIAL_FILES:
        return True
    if path.suffix.lower() == ".html":
        return True
    if relative in {"api/crates.js", "api/search-index.js", "api/src-files.js"}:
        return True
    if relative == "api/openbim_epd/sidebar-items.js":
        return True
    if re.fullmatch(r"api/search\.desc/openbim_epd/openbim_epd-desc-[0-9]+-\.js", relative):
        return True
    if re.fullmatch(r"api/trait\.impl/(?:[^/]+/)+trait\.[A-Za-z0-9_]+\.js", relative):
        return True
    if path.parts[:2] != ("api", "static.files") or len(path.parts) != 3:
        return False

    name = path.name
    return any(
        (
            hashed_name_matches(name, RUSTDOC_STATIC_PREFIXES, ".js"),
            hashed_name_matches(name, RUSTDOC_CSS_PREFIXES, ".css"),
            hashed_name_matches(name, RUSTDOC_IMAGE_PREFIXES, ".svg"),
            hashed_name_matches(name, RUSTDOC_IMAGE_PREFIXES, ".png"),
            hashed_name_matches(name, RUSTDOC_FONT_PREFIXES, ".woff2"),
            hashed_name_matches(name, RUSTDOC_FONT_PREFIXES, ".ttf.woff2"),
            hashed_name_matches(name, RUSTDOC_LICENSE_PREFIXES, ".txt"),
            hashed_name_matches(name, RUSTDOC_LICENSE_PREFIXES, ".md"),
        )
    )


def is_allowed_asset_file(relative: str) -> bool:
    if relative in {
        "assets/images/favicon.png",
        "assets/stylesheets/extra.css",
        "assets/javascripts/lunr/tinyseg.js",
        "assets/javascripts/lunr/wordcut.js",
    }:
        return True
    if re.fullmatch(r"assets/stylesheets/(?:main|palette)\.[0-9a-f]{8}\.min\.css(?:\.map)?", relative):
        return True
    if re.fullmatch(r"assets/javascripts/bundle\.[0-9a-f]{8}\.min\.js(?:\.map)?", relative):
        return True
    if re.fullmatch(r"assets/javascripts/workers/search\.[0-9a-f]{8}\.min\.js(?:\.map)?", relative):
        return True
    match = re.fullmatch(r"assets/javascripts/lunr/min/lunr\.(.+)\.min\.js", relative)
    return match is not None and match.group(1) in LUNR_MODULES


def is_allowed_file(relative: str) -> bool:
    path = PurePosixPath(relative)
    if relative in ROOT_FILES or relative in PAGE_FILES:
        return True
    if path.parts[0] == "api":
        return is_allowed_api_file(path)
    if path.parts[0] == "assets":
        return is_allowed_asset_file(relative)
    return relative == "search/search_index.json"


def validate_directory_stat(metadata: os.stat_result, expected_device: int, relative: str) -> None:
    if not stat.S_ISDIR(metadata.st_mode):
        fail(f"non-directory entry encountered while scanning: {relative}")
    if metadata.st_dev != expected_device:
        fail(f"directory crosses a filesystem boundary: {relative}")


def validate_regular_stat(metadata: os.stat_result, expected_device: int, relative: str) -> None:
    if not stat.S_ISREG(metadata.st_mode):
        fail(f"non-regular artifact is forbidden: {relative}")
    if metadata.st_nlink != 1:
        fail(f"hard-linked file is forbidden: {relative}")
    if metadata.st_dev != expected_device:
        fail(f"file crosses a filesystem boundary: {relative}")


def decode_utf8(payload: bytes, relative: str, kind: str) -> str:
    try:
        return payload.decode("utf-8")
    except UnicodeDecodeError:
        fail(f"{kind} output is not UTF-8 text: {relative}")


def validate_css(payload: bytes, relative: str) -> None:
    text = decode_utf8(payload, relative, "CSS")
    depth = 0
    quote: str | None = None
    escaped = False
    in_comment = False
    saw_block = False
    saw_declaration = False
    index = 0
    while index < len(text):
        char = text[index]
        next_char = text[index + 1] if index + 1 < len(text) else ""
        if in_comment:
            if char == "*" and next_char == "/":
                in_comment = False
                index += 2
                continue
        elif quote is not None:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == quote:
                quote = None
        elif char == "/" and next_char == "*":
            in_comment = True
            index += 2
            continue
        elif char in {"'", '"'}:
            quote = char
        elif char == "{":
            depth += 1
            saw_block = True
        elif char == "}":
            depth -= 1
            if depth < 0:
                fail(f"CSS output has unbalanced braces: {relative}")
        elif char == ":" and depth > 0:
            saw_declaration = True
        index += 1
    if depth != 0 or quote is not None or in_comment:
        fail(f"CSS output is syntactically incomplete: {relative}")
    if not saw_block or not saw_declaration:
        fail(f"CSS output has no declaration block: {relative}")


def validate_javascript(payload: bytes, relative: str) -> None:
    decode_utf8(payload, relative, "JavaScript")
    descriptor, temporary_name = tempfile.mkstemp(prefix="epd-pages-js-", suffix=".js")
    try:
        with os.fdopen(descriptor, "wb") as temporary:
            temporary.write(payload)
        try:
            result = subprocess.run(
                ["node", "--check", temporary_name],
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
        except FileNotFoundError:
            fail("Node.js is required for positive JavaScript validation")
        except subprocess.TimeoutExpired:
            fail(f"JavaScript validation timed out: {relative}")
        if result.returncode != 0:
            fail(f"JavaScript output is not syntactically valid: {relative}")
    finally:
        Path(temporary_name).unlink(missing_ok=True)


def check_content_signature(payload: bytes, relative: str) -> None:
    if relative in {".nojekyll", "api/.lock"}:
        if payload:
            fail(f"marker file must be empty: {relative}")
        return
    if payload.startswith(FORBIDDEN_SIGNATURES):
        fail(f"restricted binary signature is not publishable: {relative}")

    suffix = PurePosixPath(relative).suffix.lower()
    if suffix == ".html":
        header = decode_utf8(payload[:1024], relative, "HTML").lower()
        if "<!doctype html" not in header:
            fail(f"HTML output has an unexpected signature: {relative}")
        return
    if suffix == ".js":
        validate_javascript(payload, relative)
        return
    if suffix == ".css":
        validate_css(payload, relative)
        return
    if suffix in {".json", ".map"}:
        text = decode_utf8(payload, relative, "JSON")
        try:
            json.loads(text)
        except json.JSONDecodeError:
            fail(f"JSON output is not syntactically valid: {relative}")
        return
    if suffix == ".svg":
        try:
            root = ElementTree.fromstring(payload)
        except ElementTree.ParseError:
            fail(f"SVG output is not well-formed XML: {relative}")
        if root.tag.rsplit("}", 1)[-1] != "svg":
            fail(f"SVG output has an unexpected root element: {relative}")
        return
    if suffix == ".png":
        if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
            fail(f"PNG output has an unexpected signature: {relative}")
        return
    if suffix == ".woff2":
        if not payload.startswith(b"wOF2"):
            fail(f"WOFF2 output has an unexpected signature: {relative}")
        return
    if suffix in {".txt", ".md"}:
        if not decode_utf8(payload, relative, "text").strip():
            fail(f"text output must not be empty: {relative}")
        return
    if relative == "sitemap.xml":
        try:
            root = ElementTree.fromstring(payload)
        except ElementTree.ParseError:
            fail("sitemap.xml is not well-formed XML")
        if root.tag.rsplit("}", 1)[-1] != "urlset":
            fail("sitemap.xml has an unexpected root element")
        return
    if relative == "sitemap.xml.gz":
        try:
            expanded = gzip.decompress(payload)
            root = ElementTree.fromstring(expanded)
        except (gzip.BadGzipFile, EOFError, ElementTree.ParseError):
            fail("sitemap.xml.gz is not a valid compressed sitemap")
        if root.tag.rsplit("}", 1)[-1] != "urlset":
            fail("sitemap.xml.gz has an unexpected root element")
        return
    fail(f"artifact has no positive content validator: {relative}")


def read_regular_file(
    parent_fd: int,
    name: str,
    expected: os.stat_result,
    expected_device: int,
    relative: str,
) -> bytes:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(name, flags, dir_fd=parent_fd)
    try:
        opened = os.fstat(descriptor)
        validate_regular_stat(opened, expected_device, relative)
        if (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino):
            fail(f"file changed while opening it: {relative}")

        before = (opened.st_size, opened.st_mtime_ns, opened.st_ctime_ns)
        with os.fdopen(descriptor, "rb", closefd=False) as source:
            payload = source.read()
        after_stat = os.fstat(descriptor)
        after = (after_stat.st_size, after_stat.st_mtime_ns, after_stat.st_ctime_ns)
        if after != before or len(payload) != opened.st_size:
            fail(f"file changed while reading it: {relative}")
        return payload
    finally:
        os.close(descriptor)


def scan_directory(
    directory_fd: int,
    relative_parts: tuple[str, ...],
    expected_device: int,
    files: dict[str, bytes],
) -> None:
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )

    for name in sorted(os.listdir(directory_fd)):
        relative = PurePosixPath(*relative_parts, name).as_posix()
        metadata = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)

        if stat.S_ISLNK(metadata.st_mode):
            fail(f"symlink is forbidden: {relative}")

        if stat.S_ISDIR(metadata.st_mode):
            validate_directory_stat(metadata, expected_device, relative)
            child_fd = os.open(name, directory_flags, dir_fd=directory_fd)
            try:
                opened = os.fstat(child_fd)
                validate_directory_stat(opened, expected_device, relative)
                if (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
                    fail(f"directory changed while opening it: {relative}")
                scan_directory(child_fd, (*relative_parts, name), expected_device, files)
            finally:
                os.close(child_fd)
            continue

        validate_regular_stat(metadata, expected_device, relative)
        if not is_allowed_file(relative):
            fail(f"unexpected artifact type or path: {relative}")
        payload = read_regular_file(
            directory_fd,
            name,
            metadata,
            expected_device,
            relative,
        )
        check_content_signature(payload, relative)
        files[relative] = payload


def open_site_without_symlink_ancestors(site: Path) -> int:
    for required_flag in ("O_DIRECTORY", "O_NOFOLLOW"):
        if not hasattr(os, required_flag):
            fail(f"platform does not provide required {required_flag} support")

    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW | getattr(os, "O_CLOEXEC", 0)
    current_fd = os.open(site.anchor, directory_flags)
    try:
        for component in site.parts[1:]:
            metadata = os.stat(component, dir_fd=current_fd, follow_symlinks=False)
            if stat.S_ISLNK(metadata.st_mode):
                fail(f"site path contains a symlink component: {component}")
            if not stat.S_ISDIR(metadata.st_mode):
                fail(f"site path component is not a directory: {component}")

            next_fd = os.open(component, directory_flags, dir_fd=current_fd)
            opened = os.fstat(next_fd)
            if (opened.st_dev, opened.st_ino) != (metadata.st_dev, metadata.st_ino):
                os.close(next_fd)
                fail(f"site path component changed while opening it: {component}")
            os.close(current_fd)
            current_fd = next_fd
        return current_fd
    except BaseException:
        os.close(current_fd)
        raise


def scan_site(site_argument: str) -> tuple[Path, dict[str, bytes]]:
    site = Path(os.path.abspath(site_argument))
    root_fd = open_site_without_symlink_ancestors(site)
    try:
        opened_root = os.fstat(root_fd)
        files: dict[str, bytes] = {}
        scan_directory(root_fd, (), opened_root.st_dev, files)
    finally:
        os.close(root_fd)

    missing = [relative for relative in REQUIRED if relative not in files]
    if missing:
        fail("missing required outputs: " + ", ".join(missing))

    for relative, markers in PAGE_MARKERS.items():
        html = files[relative].decode("utf-8")
        for marker in markers:
            if marker not in html:
                fail(f"canonical marker is absent from {relative}: {marker}")

    check_local_links(files)
    return site, files


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.links: list[str] = []

    def handle_starttag(self, _tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key in {"href", "src"} and value:
                self.links.append(value)


def local_link_target(source: str, link: str) -> str | None:
    parsed = urlsplit(link)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return None

    raw_path = unquote(parsed.path)
    if "\\" in raw_path:
        fail(f"local link contains a backslash: {source} -> {link}")
    if raw_path.startswith("/epd/"):
        joined = raw_path.removeprefix("/epd/")
    elif raw_path.startswith("/"):
        joined = raw_path.lstrip("/")
    else:
        joined = posixpath.join(posixpath.dirname(source), raw_path)

    normalized = posixpath.normpath(joined)
    if normalized == ".":
        normalized = ""
    if normalized == ".." or normalized.startswith("../"):
        fail(f"local link escapes the site root: {source} -> {link}")
    return normalized


def check_local_links(files: dict[str, bytes]) -> None:
    available = set(files)
    broken: list[str] = []
    for source, payload in sorted(files.items()):
        if not source.endswith(".html"):
            continue
        parser = LinkCollector()
        parser.feed(payload.decode("utf-8"))
        for link in parser.links:
            target = local_link_target(source, link)
            if target is None:
                continue
            candidates = {target}
            candidates.add(posixpath.join(target, "index.html") if target else "index.html")
            if not any(candidate in available for candidate in candidates):
                broken.append(f"{source} -> {link}")

    if broken:
        shown = ", ".join(broken[:20])
        suffix = f" (+{len(broken) - 20} more)" if len(broken) > 20 else ""
        fail(f"broken local links: {shown}{suffix}")


def verify_archive(archive: Path, expected_hashes: dict[str, str]) -> None:
    seen: dict[str, str] = {}
    with tarfile.open(archive, "r:") as packaged:
        for member in packaged.getmembers():
            path = PurePosixPath(member.name)
            if path.is_absolute() or ".." in path.parts or "\\" in member.name:
                fail(f"unsafe archive member path: {member.name}")
            normalized = path.as_posix()
            if normalized in seen:
                fail(f"duplicate archive member: {normalized}")
            if not member.isfile():
                fail(f"archive member is not a regular file: {normalized}")
            extracted = packaged.extractfile(member)
            if extracted is None:
                fail(f"archive member could not be read: {normalized}")
            seen[normalized] = hashlib.sha256(extracted.read()).hexdigest()

    if seen != expected_hashes:
        missing = sorted(set(expected_hashes) - set(seen))
        extra = sorted(set(seen) - set(expected_hashes))
        changed = sorted(
            name
            for name in set(seen) & set(expected_hashes)
            if seen[name] != expected_hashes[name]
        )
        fail(
            "archive differs from validated site snapshot: "
            f"missing={missing}, extra={extra}, changed={changed}"
        )


def create_archive(files: dict[str, bytes], archive_argument: str | Path) -> Path:
    archive = Path(archive_argument).absolute()
    archive.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{archive.name}.",
        dir=archive.parent,
    )
    os.close(descriptor)
    temporary = Path(temporary_name)

    hashes: dict[str, str] = {}
    try:
        with tarfile.open(temporary, "w", format=tarfile.PAX_FORMAT) as output:
            for relative, payload in sorted(files.items()):
                info = tarfile.TarInfo(relative)
                info.size = len(payload)
                info.mode = 0o644
                info.mtime = 0
                info.uid = 0
                info.gid = 0
                info.uname = ""
                info.gname = ""
                output.addfile(info, fileobj=io.BytesIO(payload))
                hashes[relative] = hashlib.sha256(payload).hexdigest()

        verify_archive(temporary, hashes)
        os.replace(temporary, archive)
    finally:
        temporary.unlink(missing_ok=True)

    return archive


def main() -> None:
    if len(sys.argv) not in (2, 3):
        fail("usage: check-docs-site.py SITE_DIR [ARCHIVE_OUTPUT]")

    site, files = scan_site(sys.argv[1])
    if len(sys.argv) == 3:
        archive = Path(sys.argv[2]).absolute()
        if archive == site or site in archive.parents:
            fail("archive output must be outside the site directory")
        create_archive(files, archive)
        print(f"documentation artifact and upload archive verified: {archive}")
    else:
        print(f"documentation artifact verified: {site}")


if __name__ == "__main__":
    try:
        main()
    except (ArtifactError, OSError, tarfile.TarError, UnicodeError) as error:
        print(f"documentation artifact check failed: {error}", file=sys.stderr)
        raise SystemExit(1) from error
