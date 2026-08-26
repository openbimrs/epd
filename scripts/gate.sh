#!/usr/bin/env bash
# Complete standalone verification gate for openbimrs/epd.
set -euo pipefail

cd "$(dirname "$0")/.."

cargo fmt --all -- --check
python3 -m py_compile scripts/check-docs-site.py
python3 -m py_compile scripts/test-docs-security.py
python3 -m py_compile scripts/check-ilcd-fixtures.py
python3 -m py_compile scripts/check-package-licenses.py
python3 scripts/test-docs-security.py
python3 scripts/check-ilcd-fixtures.py
bash -n scripts/build-docs.sh
cargo build --workspace --all-targets --locked
cargo test --workspace --all-features --locked
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --all-features --no-deps --locked
cargo package --allow-dirty --locked -p openbim-epd
cargo package --allow-dirty --locked -p openbim-ilcd-epd
python3 scripts/check-package-licenses.py
