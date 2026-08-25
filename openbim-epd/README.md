# openbim-epd

ISO 22057 environmental product declaration (EPD) data-template contracts for
Rust.

## Status

**Reserved scaffold.** Version `0.1.1` does not parse, write, or validate EPD
datasets. It currently provides:

- an explicit ISO 22057:2022 edition contract;
- all 18 EPD information-module codes, including the aggregated `A1-A3` value;
- exact code lookup and semantic grouping, with D explicitly beyond the
  product-system boundary;
- unit tests for those contracts.

ISO 22057 defines EPD data-template information and mappings, not a universal
XML namespace or XSD. This crate deliberately does not invent one. Format
adapters such as ILCD+EPD or openEPD require independent, versioned
implementations and conformance evidence.

See the [repository capability table](https://github.com/openbimrs/epd#status)
before relying on a feature.

## Example

```rust
use openbim_epd::{InformationModule, InformationModuleGroup, StandardEdition};

assert_eq!(StandardEdition::CURRENT.designation(), "ISO 22057:2022");
assert_eq!(InformationModule::B7.code(), "B7");
assert_eq!(InformationModule::C4.group(), InformationModuleGroup::EndOfLife);
assert_eq!(InformationModule::from_code("A0"), None);
```

## Architecture

EPD consumes data-template and, eventually, IFC contracts. IFC, core, codec, and
data-template substrate layers must never depend on EPD. See the
[architecture document](https://github.com/openbimrs/epd/blob/main/docs/architecture.md).

No restricted ISO/CEN source document or annex workbook is vendored in this
crate. Types may be implemented from legitimately accessed specifications, but
standards possession does not establish a right to redistribute source material.

## OpenBIM.rs

- EPD repository: <https://github.com/openbimrs/epd>
- Integration workspace: <https://github.com/openbimrs/openbim>
- API documentation: <https://docs.rs/openbim-epd>

## License

MIT
