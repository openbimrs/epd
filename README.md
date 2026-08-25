# OpenBIM.rs EPD

[![CI](https://github.com/openbimrs/epd/actions/workflows/ci.yml/badge.svg)](https://github.com/openbimrs/epd/actions/workflows/ci.yml)
[![crates.io](https://img.shields.io/crates/v/openbim-epd.svg)](https://crates.io/crates/openbim-epd)
[![docs.rs](https://docs.rs/openbim-epd/badge.svg)](https://docs.rs/openbim-epd)
[![MSRV](https://img.shields.io/badge/MSRV-1.85-blue)](https://www.rust-lang.org)

Pure-Rust contracts for using environmental product declaration (EPD) data in
building information modelling, based on ISO 22057:2022.

This repository is the canonical home of the EPD family in
[OpenBIM.rs](https://github.com/openbimrs/openbim). The integration repository
pins it under `packages/epd`.

## Status

The `0.1.0` release is a **reserved scaffold**, not an EPD parser, writer, or
validator.

| Capability | Status |
| --- | --- |
| ISO 22057:2022 edition contract | Implemented and unit-tested |
| All 18 EPD information-module codes, including `A1-A3` | Implemented and unit-tested |
| Semantic grouping (including D beyond the system boundary) | Implemented and unit-tested |
| ISO 22057 XML parsing/writing | Not applicable: the standard defines no single XML serialization |
| ILCD+EPD, INIES, or openEPD adapters | Not implemented |
| EPD data-template model and validation | Not implemented |
| IFC integration | Not implemented |

No exchange-format or validation capability should be inferred from the crate
existing on crates.io.

## Why there is no `epd.xml` schema here

ISO 22057 specifies an information structure for EPD data templates and maps it
to existing practices. It does not assign a universal XML namespace or publish
one normative XSD for all ISO 22057 datasets. Its mapping material covers more
than one external format.

The implementation will therefore keep the ISO 22057 domain model separate from
versioned format adapters. Inventing an `ISO_22057` XML namespace would create a
new private format while falsely presenting it as an ISO serialization.

## Crate

| Crate | Purpose |
| --- | --- |
| [`openbim-epd`](openbim-epd/) | ISO 22057 edition and EPD information-module contracts; future domain model and adapters |

The short `epd` crate name is owned by another crates.io publisher, so this
project ships only the canonical `openbim-epd` name.

## Install

```bash
cargo add openbim-epd
```

```rust
use openbim_epd::{InformationModule, LifeCycleStage, StandardEdition};

assert_eq!(StandardEdition::CURRENT.designation(), "ISO 22057:2022");
assert_eq!(InformationModule::A1.code(), "A1");
assert_eq!(InformationModule::D.stage(), LifeCycleStage::BeyondSystemBoundary);
```

## Architecture

- [`docs/architecture.md`](docs/architecture.md) — repository, dependency, and format boundaries
- [`openbimrs/openbim`](https://github.com/openbimrs/openbim) — integrated workspace and facade
- [ISO 22057:2022](https://www.iso.org/standard/72463.html) — standard catalogue entry

EPD may consume shared data-template and IFC contracts. IFC, core, codec, and
data-template substrate layers must never depend on EPD.

## Standards material

No ISO/CEN document or annex workbook is distributed by this repository or the
crate package. Legally accessed references can be kept under the ignored local
`references/` directory; possession does not establish redistribution rights.

## Development

Requires Rust `1.85` or newer.

```bash
git clone https://github.com/openbimrs/epd.git
cd epd
./scripts/gate.sh
```

The gate checks formatting, build, tests, Clippy, rustdoc, and crates.io package
verification using command exit codes.

## Contributing

See [`CONTRIBUTING.md`](CONTRIBUTING.md). Capability work must add executable
conformance evidence and update the status table without overstating coverage.

## License

MIT — see [`LICENSE`](LICENSE).
