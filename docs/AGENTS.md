# docs/ instructions

Repository documentation support lives here. `architecture.md` is canonical;
`requirements.txt` pins the Pages toolchain; `assets/` styles the generated
site; `rustdoc-index.html` is the tracked landing page installed above generated
rustdoc. Root `README.md`, `ROADMAP.md`, and `CHANGELOG.md` remain canonical and
are copied into a temporary source tree by `scripts/build-docs.sh`.

The build packages only positively validated regular files into
`target/artifact.tar`; CI uploads that exact archive using the tar-member name
required by `deploy-pages`. The checker opens
every supplied site-path component without following symlinks, snapshots file
content through pinned directory descriptors, and verifies local links before
packaging. It uses Node.js to syntax-check JavaScript. Keep its artifact
type/path allowlist narrow when generated tooling changes.

Keep architecture statements synchronized with executable Cargo boundaries and
CI behavior. Do not copy restricted standards text, schemas, PDFs, or workbooks
into documentation.
