# EPD repository instructions

This repository owns the OpenBIM.rs implementation of ISO 22057 environmental
product declaration data-template contracts. The published crate is a reserved
scaffold; do not describe parsing, writing, validation, or exchange-format
support as implemented without executable conformance evidence.

## Map

- `openbim-epd/` — canonical published crate; read its `AGENTS.md` before editing
- `docs/` — architecture and maintained documentation
- `references/` — ignored local standards material; only its README is tracked
- `scripts/gate.sh` — complete local/CI verification gate
- `CHANGELOG.md` — user-visible changes using Keep a Changelog

## Commands

```bash
./scripts/gate.sh
cargo test --workspace
cargo package -p openbim-epd
```

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

Keep capability tables honest. Update README, rustdoc, and CHANGELOG together
for user-visible changes.
