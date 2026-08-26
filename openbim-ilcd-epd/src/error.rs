use std::{error::Error, fmt};

/// Stable category for an ILCD+EPD parse failure.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub enum ParseErrorKind {
    /// Input exceeds the configured byte budget.
    InputTooLarge,
    /// Input is not UTF-8 XML.
    InvalidUtf8,
    /// XML is not well formed.
    MalformedXml,
    /// A document type declaration is forbidden.
    DoctypeForbidden,
    /// XML exceeds the configured node budget.
    NodeLimitExceeded,
    /// XML exceeds the configured element-depth budget.
    DepthLimitExceeded,
    /// One element exceeds the configured attribute budget.
    AttributeLimitExceeded,
    /// The root is not an ILCD process dataset.
    UnexpectedRoot,
    /// The namespaced ILCD+EPD version marker is absent.
    MissingFormatVersion,
    /// The adapter does not support the declared ILCD+EPD version.
    UnsupportedFormatVersion,
    /// The process dataset has no ILCD UUID.
    MissingUuid,
    /// The process dataset UUID is not in canonical UUID form.
    InvalidUuid,
    /// The process dataset has no non-empty base name.
    MissingName,
    /// An EPD module attribute is not an ISO 22057 module code.
    InvalidInformationModule,
}

/// ILCD+EPD parse failure with a stable category and diagnostic detail.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct ParseError {
    kind: ParseErrorKind,
    detail: String,
}

impl ParseError {
    pub(crate) fn new(kind: ParseErrorKind, detail: impl Into<String>) -> Self {
        Self {
            kind,
            detail: detail.into(),
        }
    }

    /// Stable failure category.
    #[must_use]
    pub const fn kind(&self) -> ParseErrorKind {
        self.kind
    }

    /// Human-readable failure detail. Do not parse this string as an API.
    #[must_use]
    pub fn detail(&self) -> &str {
        &self.detail
    }
}

impl fmt::Display for ParseError {
    fn fmt(&self, formatter: &mut fmt::Formatter<'_>) -> fmt::Result {
        write!(
            formatter,
            "ILCD+EPD parse error ({:?}): {}",
            self.kind, self.detail
        )
    }
}

impl Error for ParseError {}
