# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project follows [Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- Added an automated GitHub Pages site with generated Rust API documentation
  and single-source architecture, roadmap, and changelog pages.

## [0.1.1] - 2026-08-25

### Fixed

- Corrected public examples to use `InformationModuleGroup` and `group()` so
  module D is not presented as a life-cycle stage.
- Added a compile-tested crate example and excluded internal agent planning
  files from the published package.
- Pinned CI actions to immutable commits and made Cargo gate operations locked.

## [0.1.0] - 2026-08-25

### Added

- Reserved the `openbim-epd` crate name.
- Added an ISO 22057:2022 standard-edition contract.
- Added all 18 EPD information-module codes, including the aggregated `A1-A3`
  value, and semantic groupings that keep module D explicitly beyond the
  product-system boundary.
- Added standalone documentation, CI, package verification, and explicit
  format-boundary guidance.

[Unreleased]: https://github.com/openbimrs/epd/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/openbimrs/epd/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/openbimrs/epd/releases/tag/v0.1.0
