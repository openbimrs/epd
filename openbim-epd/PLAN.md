# openbim-epd implementation plan

Status: EPD-ILCD v1.3 adapter and ISO 23387 composition implemented.
Last updated: 2026-08-26

This is task state, not ambient context. Follow `AGENTS.md`; claim one task ID,
record blockers and decisions under it, and check it off only with executable
evidence.

The public, capability-oriented roadmap is maintained at `../ROADMAP.md` from
the repository root and published by GitHub Pages. Keep this implementation
queue consistent with that roadmap.

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

## Implemented slice: EPD-ILCD v1.3

### Goal

Ship a separate `openbim-ilcd-epd` adapter for the InData ILCD+EPD v1.3
wire format and compose the ISO 22057 core with `openbim-dt` ISO 23387
contracts without claiming that ISO 22057 defines this XML format.

### Constraints

- Pin evidence to InDataWG release `v1.3` commit
  `7625c7dfc0d5b6bc2020eb0cf0b0503349c914aa`.
- Keep the complete schema/documentation checkout local and ignored under
  `references/specs/ILCD+EPD`; embedded JRC notices prevent assuming every file
  is redistributable merely from repository-level Apache-2.0 metadata.
- Track only attributed upstream XML fixtures covered by the upstream license;
  do not import PDFs, logos, standards documents, or annex workbooks.
- Preserve all unknown XML bytes for lossless unmodified round trips.
- Keep ILCD+EPD namespace/version rules in the adapter crate. The core crate
  remains provider- and serialization-neutral.
- Maintain Rust 1.85 compatibility and direct maintained XML dependencies.

### Deferred coverage

- Exact ISO 22057 Annex A mappings remain deferred until the full property model
  exists; the current adapter does not invent semantic defaults.
- Provider profile validation and format versions other than v1.3 require
  separate fixtures and explicit versioned support.
- Queryable Annex B mappings require a separate evidence-tagged mapping model;
  no Annex B mapping capability is implemented in this slice.

### Workstreams

1. Add an `openbim-dt = 0.2.0` dependency and an owned ISO 22057 data-template
   composition contract to `openbim-epd`.
2. Add `openbim-ilcd-epd` with bounded XML parsing, explicit v1.3 namespace
   identity, typed process identity/title/module views, diagnostics, and exact
   original-byte writing.
3. Import a minimal attributed XML fixture corpus from the pinned upstream
   release under adapter `tests/fixtures`.
4. Document ÖKOBAUDAT, IBU.data, ECO Platform, and InData as known ecosystem
   users without claiming provider API or conformance coverage.

### Validation strategy

- RED/GREEN tests for namespace/version rejection, process identity/title,
  all declared module values, malformed XML, input limits, and exact byte round
  trips.
- Mutation probes against version, namespace, module, and size-limit gates.
- Full locked gate, MSRV, all-features, isolated builds, docs, package dry-runs,
  crate-content audit, and ignored-reference audit.
- Immutable read-only review of the exact candidate tree before publication.

### Risks and rollback

- Provider schema evolution: isolate v1.3 constants and typed views in the
  adapter; future versions receive explicit support rather than aliases.
- Legal provenance: delete tracked fixture candidates if file-level rights are
  ambiguous; retain only synthetic fixtures plus local ignored references.
- Premature modeling: return adapter-specific metadata or explicit mapping gaps
  rather than inventing ISO 22057 semantics.
- Rollback is one standalone commit plus one OpenBIM gitlink commit; do not
  advance the parent until standalone CI passes.

### Next concrete action

Extend the format family only with independently sourced fixtures: either add an
explicit older/newer ILCD+EPD version profile or implement provider-profile
validation without weakening the v1.3 namespace and version gates.

## Work queue

- [ ] `EPD-MODEL` — model Annex A properties without binding the domain model to one wire format
- [ ] `EPD-MAPPING` — represent Annex B mappings with source-format/version evidence
- [x] `EPD-ILCD-V1.3` — bounded versioned adapter, attributed fixtures, and exact unmodified-byte preservation
- [ ] `EPD-OPENEPD` — evaluate a versioned openEPD JSON adapter
- [ ] `EPD-VALIDATE` — validate required properties and declared modules with diagnostic evidence
- [ ] `EPD-IFC` — connect EPD references to public IFC contracts without reversing dependencies

## Completion log

The v1.3 slice is covered by the locked Rust 1.85 gate, exact upstream fixture
checks, bounded-parser and shadowing regressions, mutation probes, package-license
checks, and deterministic Pages-artifact validation. Editing, reconstructed XML
serialization, XSD/provider-profile validation, ZIP handling, and complete Annex
A semantics remain explicitly unimplemented.
