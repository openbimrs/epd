//! Explicit ILCD+EPD v1.3 XML adapter.
//!
//! [`openbim_epd`] models the format-neutral ISO 22057 contract. This crate
//! models one external exchange format: the InData ILCD+EPD v1.3 extension of
//! ILCD XML. The two must not be conflated.
//!
//! Parsing retains the exact original UTF-8 bytes. Typed views cover only the
//! process identity, multilingual base names, format version, and declared
//! information modules. Unknown XML remains in those original bytes and is
//! emitted unchanged by [`Document::write_original`]. This is not XSD or
//! provider conformance validation.

#![forbid(unsafe_code)]

mod error;
mod model;
mod parser;

pub use error::{ParseError, ParseErrorKind};
pub use model::{Document, FormatVersion, MultilingualName, ProcessDataset};
pub use parser::ParseOptions;

/// ILCD process-dataset namespace.
pub const PROCESS_NAMESPACE: &str = "http://lca.jrc.it/ILCD/Process";
/// ILCD common namespace.
pub const COMMON_NAMESPACE: &str = "http://lca.jrc.it/ILCD/Common";
/// EPD extension namespace introduced by the 2013 format.
pub const EPD_2013_NAMESPACE: &str = "http://www.iai.kit.edu/EPD/2013";
/// EPD extension namespace carrying the format-version attribute.
pub const EPD_2019_NAMESPACE: &str = "http://www.indata.network/EPD/2019";
/// EPD extension namespace introduced by ILCD+EPD v1.3.
pub const EPD_2024_NAMESPACE: &str = "http://www.indata.network/EPD/2024";
