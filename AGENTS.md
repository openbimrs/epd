# EPD repository instructions

This repository owns the OpenBIM.rs implementation of ISO 22057 environmental
product declaration data-template contracts. Capability claims require
executable evidence; process parsing in `openbim-ilcd-epd` does not imply writing,
validation, ZIP packages, provider APIs, or a universal ISO XML format.

## Map

- `openbim-epd/` — format-neutral ISO 22057 core; read its `AGENTS.md` before editing
- `openbim-ilcd-epd/` — explicit InData ILCD+EPD v1.3 adapter; read its `AGENTS.md`
- `docs/` — architecture and maintained documentation
- `ROADMAP.md` — canonical public capability roadmap
- `mkdocs.yml` — GitHub Pages navigation and theme configuration
- `references/specs/` — ignored local standards and full format references; only the parent README is tracked
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
cargo package -p openbim-ilcd-epd
python -m pip install -r docs/requirements.txt
./scripts/build-docs.sh
```

The documentation checker uses Node.js to syntax-check generated JavaScript.

Trust command exit codes. Never summarize a Cargo pipeline in a way that hides
the Cargo process status.

## Boundaries

- `openbim-epd` composes the released `openbim-dt` contract; DT remains lower-level.
- ILCD+EPD element names, namespaces, profile policy, and preservation behavior
  stay in `openbim-ilcd-epd`.
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
