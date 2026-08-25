# HERMES.md — OpenBIM.rs EPD

Canonical repository: <https://github.com/openbimrs/epd>
Integration repository: <https://github.com/openbimrs/openbim>

Read `AGENTS.md` before changing the repository and the nested `AGENTS.md`
before editing a crate. Keep the crate independently buildable; the parent
OpenBIM.rs workspace pins this repository as a submodule but is not required for
standalone development.

## Verification

Run `./scripts/gate.sh`. It is the authoritative local and CI gate and decides
success from command exit codes.

Run `./scripts/build-docs.sh` after installing `docs/requirements.txt` when
changing public documentation. It assembles the MkDocs site and rustdoc API in
`target/site/`, opens every supplied path component without following symlinks,
positively validates every generated content type, and creates the exact GitHub
Pages upload archive at `target/pages-artifact.tar`. It also verifies generated
local links and packages an immutable descriptor-backed content snapshot rather
than reopening validated paths. Node.js is required for JavaScript syntax checks.

## Project conventions

- Rust 2021, MSRV 1.85, MIT.
- Pure Rust; unsafe code is forbidden.
- EPD consumes data-template/IFC contracts; those lower layers never depend on EPD.
- ISO 22057 does not define one XML schema. Do not invent a namespace or imply
  that a format-specific parser is ISO 22057 itself.
- Do not vendor standards documents or annex workbooks without confirmed
  redistribution rights. Local material belongs under ignored
  `references/schema/`.
- Use Keep a Changelog and distinguish implemented, reserved, and
  conformance-tested capabilities.
