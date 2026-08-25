# openbim-epd instructions

Purpose: ISO 22057 EPD data-template contracts and future explicit
exchange-format adapters. Follow `../AGENTS.md`. Read `PLAN.md` for implementation
or roadmap work; keep progress, blockers, and verification evidence there.

## Boundary

- May depend on released data-template and public IFC contracts when needed.
- Must remain independently buildable from this repository.
- Must never be depended on by IFC, core, codec, or data-template substrate layers.
- Keep package and cross-repository dependency versions explicit.
- Never vendor restricted standards documents or annex workbooks.
- Never present an ILCD+EPD, INIES, openEPD, or another adapter as a universal
  ISO 22057 XML serialization.

## Status

Reserved scaffold. Standard-edition and information-module contracts exist;
parsing, writing, validation, template exchange, and format adapters do not.
