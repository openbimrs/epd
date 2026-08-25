# Contributing

Contributions are welcome, especially those that turn reserved ISO 22057 EPD
contracts into conformance-tested behavior.

## Before opening a pull request

1. Read `AGENTS.md` and the affected crate's nested instructions.
2. Keep EPD above data-template/IFC contracts; do not introduce reverse dependencies.
3. Add tests before claiming parsing, writing, adapter, or validation behavior.
4. Keep restricted standards material local under `references/`. Commit fixtures
   only when their redistribution rights are known.
5. Name every format adapter and supported version explicitly. Do not describe an
   external XML or JSON format as the universal ISO 22057 serialization.
6. Run:

```bash
./scripts/gate.sh
```

7. Update README capability status, rustdoc, and `CHANGELOG.md` for user-visible behavior.

## Conformance work

Representative examples are not enough to claim format or validation support.
Use public, redistributable fixtures; record the source format and version;
exercise required and optional fields; and test unknown-data preservation before
claiming lossless round trips.

## Commits

Use focused commits with imperative subjects. Cross-repository changes publish
lower-level dependencies first and update the `openbimrs/openbim` submodule pin
last.
