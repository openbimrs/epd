# Architecture

## Repository role

`openbimrs/epd` is the canonical source repository for the EPD family.
`openbimrs/openbim` pins a verified commit at `packages/epd` and provides
ecosystem-level integration tests plus the feature-gated `openbim` facade.

The child repository must remain buildable without cloning the integration
workspace. Published crates therefore use explicit metadata and versioned
registry dependencies rather than paths into sibling repositories.

## Dependency direction

```text
codec/core  <-  data templates / IFC  <-  EPD
                                      \
openbim facade  ----------------------> EPD
```

- EPD may use released data-template and public IFC contracts.
- IFC, core, codec, and data-template substrate crates must never depend on EPD.
- The `openbim` facade may optionally re-export EPD.

This direction keeps environmental declarations and format policy out of IFC
model and serialization layers.

## Domain model versus exchange formats

ISO 22057:2022 defines EPD data-template information. It does not standardize a
single wire encoding, XML namespace, or XSD. Annex B maps information to more
than one established external format.

The architecture therefore has two separate future responsibilities:

1. a format-neutral ISO 22057 domain model;
2. explicit adapters, each named and versioned for its actual format.

An ILCD+EPD, INIES, EC3/openEPD, or other adapter must not leak its element names,
identifiers, cardinality quirks, or version assumptions into the domain model.
Parsing must retain source-format/version evidence, and unsupported source data
must not be silently discarded if lossless round trips are claimed.

## Scaffold contracts

The initial crate commits only low-risk normative vocabulary:

- the ISO 22057:2022 standard edition;
- the 18 information-module codes A1 through D, including the aggregated
  `A1-A3` product-stage value;
- exact module codes and semantic groupings, with D represented as beyond the
  product-system boundary rather than as a life-cycle stage.

These types do not imply an EPD dataset model, parser, writer, or validator.

## Standards artifacts

This repository does not vendor ISO/CEN documents or annex workbooks. Local
references stay under ignored `references/`. A fixture can be committed only
when its redistribution terms are known and compatible with the repository
license and intended use.

## Cross-repository delivery

Changes spanning repositories follow dependency order:

1. land and publish lower-level contract changes;
2. update EPD and verify it standalone;
3. push/publish the EPD commit;
4. update and verify the `openbim` submodule pin;
5. publish the integration commit when a facade release is intended.

The superproject pin is the compatibility declaration and rollback point.
