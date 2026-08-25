# openbim-epd implementation plan

Status: name reserved; edition/module contracts implemented; exchange adapters not started.
Last updated: 2026-08-25

This is task state, not ambient context. Follow `AGENTS.md`; claim one task ID,
record blockers and decisions under it, and check it off only with executable
evidence.

## Established boundary

ISO 22057 defines EPD data-template information and mappings, not a universal
XML namespace or XSD. EPD sits above data-template/IFC contracts. Lower layers
must never depend on EPD.

## Implemented scaffold

- `StandardEdition` and the ISO 22057:2022 designation
- all 18 `InformationModule` values, including `A1-A3`, exact codes, and
  `InformationModuleGroup` semantics that keep D beyond the system boundary
- unit tests for exact completeness, round trips, group boundaries, and invalid
  codes

These are typed vocabulary contracts, not a parser, writer, or validator.

## Work queue

- [ ] `EPD-MODEL` — model Annex A properties without binding the domain model to one wire format
- [ ] `EPD-MAPPING` — represent Annex B mappings with source-format/version evidence
- [ ] `EPD-ILCD` — evaluate a versioned ILCD+EPD adapter and public conformance fixtures
- [ ] `EPD-OPENEPD` — evaluate a versioned openEPD JSON adapter
- [ ] `EPD-VALIDATE` — validate required properties and declared modules with diagnostic evidence
- [ ] `EPD-IFC` — connect EPD references to public IFC contracts without reversing dependencies

## Completion log

The scaffold contracts are covered by `cargo test -p openbim-epd`; no exchange
or validation capability is complete.
