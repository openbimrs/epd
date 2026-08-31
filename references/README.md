# Local standards and format references

This directory is intentionally excluded from version control and crate
packages, except for this notice.

Keep locally obtained standards material under `references/specs/`. ISO/CEN
standards and their annex workbooks may be used to implement and verify source
code, but possession does not establish permission to redistribute those files
in this repository, which is licensed under AGPL-3.0-or-later.

## ILCD+EPD v1.3

The public InData source linked by the project is:

- repository: <https://github.com/InDataWG/ILCD-EPD-Data-Format>;
- release branch: `release/v1.3`;
- audited commit: `7625c7dfc0d5b6bc2020eb0cf0b0503349c914aa`;
- local path: `references/specs/ILCD+EPD`.

Reproduce the local reference checkout without vendoring it:

```bash
git clone --depth 1 --branch release/v1.3 --single-branch \
  https://github.com/InDataWG/ILCD-EPD-Data-Format.git \
  references/specs/ILCD+EPD
test "$(git -C references/specs/ILCD+EPD rev-parse HEAD)" = \
  7625c7dfc0d5b6bc2020eb0cf0b0503349c914aa
```

The upstream repository declares Apache-2.0 at its root, but schema files also
carry embedded JRC/European Commission notices. Consequently the full checkout
remains local and is not copied into Git, crates, Pages, or release artifacts.

An XML-only mirror of upstream `sample_data/` is committed under
`openbim-ilcd-epd/tests/fixtures/upstream-v1.3/` with its own source record and
upstream license. It excludes schemas, PDFs, logos, and other documentation and
is excluded from crate packages.

The Pages build never reads or copies `references/`. It rejects symlinks, hard
links, filesystem-boundary crossings, and output outside a narrow generated-file
allowlist before creating the exact archive uploaded for deployment.

The implementation was checked against ISO 22057:2022 and its Annex A/B
workbooks. Annex A expresses EPD information as a BIM data template based on ISO
23386/23387. Annex B maps those concepts to multiple existing exchange formats;
it is not an ISO XML schema.
