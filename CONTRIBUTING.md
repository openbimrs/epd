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
python -m pip install -r docs/requirements.txt
./scripts/build-docs.sh
```

7. Update README capability status, rustdoc, `ROADMAP.md`, and `CHANGELOG.md` for
   user-visible behavior. Pages copies those canonical files; do not maintain
   parallel changelog or roadmap documents under `docs/`.

## Conformance work

Representative examples are not enough to claim format or validation support.
Use public, redistributable fixtures; record the source format and version;
exercise required and optional fields; and test unknown-data preservation before
claiming lossless round trips.

## Commits

Use focused commits with imperative subjects. Cross-repository changes publish
lower-level dependencies first and update the `openbimrs/openbim` submodule pin
last.

## Licensing contributions

Unless an explicitly signed agreement says otherwise, every contribution
submitted to this repository is licensed under `AGPL-3.0-or-later`. Submit only
work that you have the right to license. Identify third-party material and
preserve its license, attribution, and provenance.
