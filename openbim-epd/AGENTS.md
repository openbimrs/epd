# openbim-epd instructions

Purpose: format-neutral ISO 22057 EPD data-template contracts. Explicit
exchange-format adapters are sibling crates. Follow `../AGENTS.md`. Read `PLAN.md`
for implementation or roadmap work; keep progress, blockers, and verification
evidence there.

## Boundary

- May depend on released data-template and public IFC contracts when needed.
- Must remain independently buildable from this repository.
- Must never be depended on by IFC, core, codec, or data-template substrate layers.
- Keep package and cross-repository dependency versions explicit.
- Never vendor restricted standards documents or annex workbooks.
- Never present an ILCD+EPD, INIES, openEPD, or another adapter as a universal
  ISO 22057 XML serialization.

## Status

The standard edition, information modules, and composition with the canonical
`openbim-dt` ISO 23387 contract are implemented. Parsing, writing, and format
validation do not belong in this core crate; use an explicit sibling adapter.
