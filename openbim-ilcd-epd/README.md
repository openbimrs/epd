# openbim-ilcd-epd

Explicit Rust adapter for the **InData ILCD+EPD v1.3** XML format used across
the ÖKOBAUDAT, IBU.data, ECO Platform, and InData ecosystems.

This crate is a format adapter above [`openbim-epd`](../openbim-epd). ISO
22057:2022 defines EPD data-template information and mappings; it does **not**
define a universal XML exchange schema. Parsing ILCD+EPD therefore does not by
itself establish ISO 22057, provider, or XML Schema conformance.

## Initial capability target

- bounded, namespace-aware parsing of v1.3 process datasets;
- typed process UUID, multilingual title, and EN 15804 module views;
- exact preservation and writing of original XML bytes, including unknown
  extensions;
- explicit errors for wrong namespaces, missing/unsupported format versions,
  malformed XML, invalid modules, and configured resource limits.

XML Schema validation, editable serialization, linked-dataset resolution,
provider APIs, and full Annex B mapping remain separate future capabilities.
