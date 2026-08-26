# Roadmap

`openbim-epd` is an honest ISO 22057:2022 contract scaffold. This roadmap
separates the small implemented vocabulary from future EPD data modeling,
validation, and provider-format adapters.

## Current baseline

Implemented and released:

- the ISO 22057:2022 edition designation;
- all 18 information-module values, including aggregated `A1-A3`;
- exact code lookup and semantic grouping;
- module D represented as benefits and loads beyond the product-system boundary;
- standalone Rust gates, API documentation, and OpenBIM facade integration.

Implemented on unreleased `main`:

- composition with the canonical `openbim-dt` ISO 23387 `DataTemplate` contract;
- an explicit `openbim-ilcd-epd` v1.3 process XML adapter;
- bounded, DTD-free parsing of process identity, multilingual names, and declared
  ISO 22057 information modules;
- exact original-byte preservation for unmodified parsed documents;
- an attributed, XML-only 45-file fixture mirror from the pinned InData v1.3
  release.

Not implemented:

- generic EPD dataset parsing or writing;
- ILCD+EPD editing/writing, XSD validation, ZIP package handling, or provider APIs;
- generic or provider-specific validation;
- a complete ISO 22057 Annex A data-template model;
- INIES or openEPD adapters;
- IFC association behavior.

## Delivery principles

1. **Format-neutral domain first.** Provider wire names and version quirks must
   not become the ISO 22057 domain model.
2. **Explicit adapters.** Every exchange adapter names its actual format and
   supported version. There is no universal ISO 22057 XML schema.
3. **Evidence-backed coverage.** Capability claims require redistributable
   fixtures, executable tests, and documented source/version evidence.
4. **Lossless before convenient.** Unknown provider data must survive round trips
   before an adapter can claim lossless behavior.
5. **Dependency direction stays downward.** EPD may consume public data-template
   and IFC contracts; those lower layers never depend on EPD.

## Milestones

### 1. ISO 22057 domain model

- Model Annex A concepts as typed, format-neutral Rust contracts.
- Record cardinality, units, identifiers, provenance, and optionality without
  copying restricted standards text into the repository.
- Preserve extension points for information not yet modeled.

**Exit evidence:** model tests cover required/optional boundaries and demonstrate
that no provider-specific wire vocabulary leaks into public domain types.

### 2. Mapping evidence

- Represent Annex B mappings with explicit source format and version metadata.
- Distinguish exact, transformed, conditional, and unavailable mappings.
- Make mapping gaps queryable rather than silently defaulted.

**Exit evidence:** executable mapping tables cover a legally redistributable
fixture set and fail when source/version evidence is missing.

### 3. Validation and diagnostics

- Validate declared information modules and modeled property requirements.
- Return structured diagnostics with stable paths and source evidence.
- Keep unsupported provider-format data distinct from invalid ISO-domain data.

**Exit evidence:** positive, negative, and mutation tests prove each diagnostic
gate can reject a targeted defect.

### 4. Versioned provider adapters

In progress:

- ILCD+EPD v1.3 process XML: bounded parsing and exact unmodified-byte
  preservation are implemented in the separate `openbim-ilcd-epd` crate.

Next ILCD+EPD slices:

- map additional v1.3 process fields to explicit ISO 22057 concepts;
- add ZIP package topology and reference-integrity checks;
- define editing/writing semantics without dropping unknown provider extensions;
- add XSD/profile validation only when diagnostics identify the exact upstream
  schema and profile version.

Evaluate independently:

- INIES;
- openEPD/EC3;
- other formats only when public specifications and fixtures permit verification.

Each adapter receives its own capability table. Parsing support never implies
writing, validation, conformance, or editable lossless round trips.

### 5. IFC integration

- Associate EPD identities and evidence with public IFC contracts.
- Keep relationship/provenance behavior explicit.
- Avoid introducing EPD policy into IFC parsing or model crates.

**Exit evidence:** integration tests demonstrate dependency isolation and stable
round trips for supported references.

## Standards material boundary

Purchased or otherwise restricted standards files remain local under
`references/specs/`. The documentation and release pipelines must never copy
that directory into Git, crates, build artifacts, or GitHub Pages.
