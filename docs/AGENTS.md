# docs/ instructions

Repository documentation support lives here. `architecture.md` is canonical;
`requirements.txt` pins the Pages toolchain; `assets/` styles the generated
site. Root `README.md`, `ROADMAP.md`, and `CHANGELOG.md` remain canonical and are
copied into a temporary source tree by `scripts/build-docs.sh`.

Keep architecture statements synchronized with executable Cargo boundaries and
CI behavior. Do not copy restricted standards text, schemas, PDFs, or workbooks
into documentation.
