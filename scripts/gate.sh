#!/usr/bin/env bash
# Complete standalone verification gate for openbimrs/epd.
set -euo pipefail

cd "$(dirname "$0")/.."

cargo fmt --all -- --check
python3 -m py_compile scripts/check-docs-site.py
bash -n scripts/build-docs.sh
cargo build --workspace --all-targets --locked
cargo test --workspace --all-features --locked
cargo clippy --workspace --all-targets --all-features --locked -- -D warnings
RUSTDOCFLAGS="-D warnings" cargo doc --workspace --all-features --no-deps --locked
cargo package --allow-dirty --locked -p openbim-epd
