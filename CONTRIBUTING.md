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

OpenBIM.rs is dual-licensed: `AGPL-3.0-or-later OR LicenseRef-Commercial`
(see [`LICENSING.md`](LICENSING.md)). To keep the commercial option
possible, every contribution is accepted on the following terms, which you
agree to by submitting it (a pull request, patch, issue attachment or any
other material intended for inclusion):

1. **Licence to the project.** Your contribution is licensed under
   `AGPL-3.0-or-later`.
2. **Licence to the copyright holder.** You also grant the copyright holder
   named in [`NOTICE`](NOTICE) a perpetual, worldwide, non-exclusive,
   royalty-free, irrevocable licence to use, reproduce, modify, distribute,
   sublicense and relicense your contribution, including under proprietary
   or commercial terms, as part of OpenBIM.rs or works derived from it.
3. **You keep your copyright.** These terms grant a licence; they do not
   transfer ownership.
4. **You have the right to grant this.** The contribution is your own work,
   or you have permission to submit it on these terms (for example from
   your employer). Identify third-party material, keep its licence,
   attribution and provenance, and do not submit third-party material whose
   licence does not allow these terms.
5. **Patents.** You grant the same parties a licence under any patent claims
   you can license that your contribution necessarily infringes, on the terms
   of section 11 of the AGPL.

If you cannot agree to these terms, say so in the issue or pull request
before submitting; the contribution can then not be merged.
