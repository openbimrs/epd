use std::io::{self, Write};

use openbim_epd::InformationModule;

use crate::{parser, ParseError, ParseOptions};

/// Explicitly supported ILCD+EPD wire-format revision.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum FormatVersion {
    /// InData ILCD+EPD v1.3 (`epd2019:epd-version="1.3"`).
    V1_3,
}

impl FormatVersion {
    /// Exact wire value.
    #[must_use]
    pub const fn as_str(self) -> &'static str {
        match self {
            Self::V1_3 => "1.3",
        }
    }
}

/// One ILCD multilingual `baseName` value.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct MultilingualName {
    language: String,
    text: String,
}

impl MultilingualName {
    pub(crate) fn new(language: String, text: String) -> Self {
        Self { language, text }
    }

    /// BCP 47-style language tag carried by `xml:lang`.
    #[must_use]
    pub fn language(&self) -> &str {
        &self.language
    }

    /// Name text after XML entity decoding.
    #[must_use]
    pub fn text(&self) -> &str {
        &self.text
    }
}

/// Typed, adapter-specific view of one ILCD process dataset.
///
/// Fields not represented here remain available in [`Document::as_bytes`].
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ProcessDataset {
    version: FormatVersion,
    uuid: String,
    names: Vec<MultilingualName>,
    modules: Vec<InformationModule>,
}

impl ProcessDataset {
    pub(crate) fn new(
        version: FormatVersion,
        uuid: String,
        names: Vec<MultilingualName>,
        modules: Vec<InformationModule>,
    ) -> Self {
        Self {
            version,
            uuid,
            names,
            modules,
        }
    }

    /// ILCD+EPD wire-format revision.
    #[must_use]
    pub const fn version(&self) -> FormatVersion {
        self.version
    }

    /// ILCD process UUID exactly as represented in XML text.
    #[must_use]
    pub fn uuid(&self) -> &str {
        &self.uuid
    }

    /// Every non-empty multilingual base name in document order.
    #[must_use]
    pub fn names(&self) -> &[MultilingualName] {
        &self.names
    }

    /// First base name matching `xml:lang` exactly.
    #[must_use]
    pub fn name(&self, language: &str) -> Option<&str> {
        self.names
            .iter()
            .find(|name| name.language == language)
            .map(MultilingualName::text)
    }

    /// Unique declared information modules in ISO 22057 normative order.
    #[must_use]
    pub fn modules(&self) -> &[InformationModule] {
        &self.modules
    }
}

/// Parsed ILCD+EPD document retaining the exact original UTF-8 bytes.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct Document {
    original: Box<[u8]>,
    process: ProcessDataset,
}

impl Document {
    pub(crate) fn parsed(original: &[u8], process: ProcessDataset) -> Self {
        Self {
            original: original.into(),
            process,
        }
    }

    /// Parses an ILCD+EPD v1.3 process dataset with default resource limits.
    pub fn parse(input: &[u8]) -> Result<Self, ParseError> {
        Self::parse_with_options(input, ParseOptions::default())
    }

    /// Parses with explicit resource limits.
    pub fn parse_with_options(input: &[u8], options: ParseOptions) -> Result<Self, ParseError> {
        parser::parse(input, options)
    }

    /// Typed process-dataset view.
    #[must_use]
    pub const fn process(&self) -> &ProcessDataset {
        &self.process
    }

    /// Explicit ILCD+EPD wire-format revision.
    #[must_use]
    pub const fn format_version(&self) -> FormatVersion {
        self.process.version()
    }

    /// Exact original XML bytes, including unknown content and formatting.
    #[must_use]
    pub fn as_bytes(&self) -> &[u8] {
        &self.original
    }

    /// Writes the exact original XML bytes without reconstruction.
    pub fn write_original(&self, writer: &mut impl Write) -> io::Result<()> {
        writer.write_all(&self.original)
    }

    /// Consumes the document and returns the exact original XML bytes.
    #[must_use]
    pub fn into_bytes(self) -> Box<[u8]> {
        self.original
    }
}
