# EPD repository instructions

This repository owns the OpenBIM.rs implementation of ISO 22057 environmental
product declaration data-template contracts. The published crate is a reserved
scaffold; do not describe parsing, writing, validation, or exchange-format
support as implemented without executable conformance evidence.

## Map

- `openbim-epd/` — canonical published crate; read its `AGENTS.md` before editing
- `docs/` — architecture and maintained documentation
- `ROADMAP.md` — canonical public capability roadmap
- `mkdocs.yml` — GitHub Pages navigation and theme configuration
- `references/schema/` — ignored local standards material; only the parent README is tracked
- `scripts/gate.sh` — complete local/CI verification gate
- `scripts/build-docs.sh` — assembles MkDocs prose, rustdoc, and the checked upload archive
- `scripts/check-docs-site.py` — symlink-free, positive-content site verifier and archive builder
- `scripts/test-docs-security.py` — mutation-sensitive Pages boundary tests
- `CHANGELOG.md` — user-visible changes using Keep a Changelog

## Commands

```bash
./scripts/gate.sh
cargo test --workspace
cargo package -p openbim-epd
python -m pip install -r docs/requirements.txt
./scripts/build-docs.sh
```

The documentation checker uses Node.js to syntax-check generated JavaScript.

Trust command exit codes. Never summarize a Cargo pipeline in a way that hides
the Cargo process status.

## Boundaries

- EPD may depend on released data-template and public IFC contracts when those
  integrations are implemented.
- IFC, core, codec, and lower-level data-template crates must never depend on EPD.
- ISO 22057 defines information and mappings, not a single XML namespace or XSD.
  Format adapters must be explicit, independently versioned capabilities.
- Do not vendor ISO/CEN documents or annex workbooks without verified
  redistribution rights.
- Release-critical metadata is explicit in crate manifests; do not replace it
  with parent-workspace inheritance.

## Documentation discipline

Keep capability tables honest. Update README, rustdoc, `ROADMAP.md`, and
`CHANGELOG.md` together for user-visible changes. Pages copies root canonical
files into its generated source tree; do not create parallel changelog or
roadmap copies under `docs/`.
