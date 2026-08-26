# openbim-ilcd-epd instructions

Purpose: explicit InData ILCD+EPD XML adapters. This crate is not the ISO 22057
core and must never be presented as a universal ISO 22057 serialization.

- Version every supported wire contract explicitly; v1.3 is not an alias for
  older or future revisions.
- Parse namespaces, not prefixes.
- Keep direct XML dependencies local to this crate.
- Preserve unknown XML bytes for exact unmodified round trips.
- Bound input size and XML complexity before claiming safe parsing.
- Upstream fixtures require exact source commit and license provenance.
- Do not package the local schema/reference checkout.
