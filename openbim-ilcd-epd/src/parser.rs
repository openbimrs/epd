use openbim_epd::InformationModule;
use roxmltree::{Document as XmlDocument, Error as XmlError, Node, ParsingOptions};

use crate::{
    Document, FormatVersion, MultilingualName, ParseError, ParseErrorKind, ProcessDataset,
    COMMON_NAMESPACE, EPD_2013_NAMESPACE, EPD_2019_NAMESPACE, PROCESS_NAMESPACE,
};

const XML_NAMESPACE: &str = "http://www.w3.org/XML/1998/namespace";

/// Resource budgets for parsing untrusted ILCD+EPD XML.
#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct ParseOptions {
    /// Maximum UTF-8 input bytes.
    pub max_bytes: usize,
    /// Maximum XML nodes, including text and comments.
    pub max_nodes: usize,
    /// Maximum nested element depth, counting the root as one.
    pub max_depth: usize,
    /// Maximum attributes on one element.
    pub max_attributes: usize,
}

impl Default for ParseOptions {
    fn default() -> Self {
        Self {
            max_bytes: 16 * 1024 * 1024,
            max_nodes: 1_000_000,
            max_depth: 128,
            max_attributes: 256,
        }
    }
}

impl ParseOptions {
    /// Returns these limits with a different byte budget.
    #[must_use]
    pub const fn with_max_bytes(mut self, max_bytes: usize) -> Self {
        self.max_bytes = max_bytes;
        self
    }

    /// Returns these limits with a different node budget.
    #[must_use]
    pub const fn with_max_nodes(mut self, max_nodes: usize) -> Self {
        self.max_nodes = max_nodes;
        self
    }

    /// Returns these limits with a different element-depth budget.
    #[must_use]
    pub const fn with_max_depth(mut self, max_depth: usize) -> Self {
        self.max_depth = max_depth;
        self
    }

    /// Returns these limits with a different per-element attribute budget.
    #[must_use]
    pub const fn with_max_attributes(mut self, max_attributes: usize) -> Self {
        self.max_attributes = max_attributes;
        self
    }
}

pub(crate) fn parse(input: &[u8], options: ParseOptions) -> Result<Document, ParseError> {
    if input.len() > options.max_bytes {
        return Err(ParseError::new(
            ParseErrorKind::InputTooLarge,
            format!("{} bytes exceeds limit {}", input.len(), options.max_bytes),
        ));
    }
    let xml = std::str::from_utf8(input)
        .map_err(|error| ParseError::new(ParseErrorKind::InvalidUtf8, error.to_string()))?;
    let parsed = XmlDocument::parse_with_options(
        xml,
        ParsingOptions {
            allow_dtd: false,
            nodes_limit: u32::try_from(options.max_nodes).unwrap_or(u32::MAX),
            entity_resolver: None,
        },
    )
    .map_err(map_xml_error)?;

    enforce_tree_limits(&parsed, options)?;
    let root = parsed.root_element();
    if root.tag_name().namespace() != Some(PROCESS_NAMESPACE)
        || root.tag_name().name() != "processDataSet"
    {
        return Err(ParseError::new(
            ParseErrorKind::UnexpectedRoot,
            format!(
                "expected {{{PROCESS_NAMESPACE}}}processDataSet, found {{{}}}{}",
                root.tag_name().namespace().unwrap_or(""),
                root.tag_name().name()
            ),
        ));
    }

    let version = match root.attribute((EPD_2019_NAMESPACE, "epd-version")) {
        Some("1.3") => FormatVersion::V1_3,
        Some(value) => {
            return Err(ParseError::new(
                ParseErrorKind::UnsupportedFormatVersion,
                format!("unsupported epd-version `{value}`; expected `1.3`"),
            ))
        }
        None => {
            return Err(ParseError::new(
                ParseErrorKind::MissingFormatVersion,
                "missing namespaced epd2019:epd-version attribute",
            ))
        }
    };

    let data_set_information = child_named(root, PROCESS_NAMESPACE, "processInformation")
        .and_then(|node| child_named(node, PROCESS_NAMESPACE, "dataSetInformation"));
    let uuid = data_set_information
        .and_then(|node| child_named(node, COMMON_NAMESPACE, "UUID"))
        .and_then(|node| node.text())
        .map(str::trim)
        .filter(|value| !value.is_empty())
        .ok_or_else(|| {
            ParseError::new(ParseErrorKind::MissingUuid, "missing non-empty common:UUID")
        })?
        .to_owned();
    if !is_canonical_uuid(&uuid) {
        return Err(ParseError::new(
            ParseErrorKind::InvalidUuid,
            format!("`{uuid}` is not a canonical UUID"),
        ));
    }

    let names: Vec<_> = data_set_information
        .and_then(|node| child_named(node, PROCESS_NAMESPACE, "name"))
        .into_iter()
        .flat_map(|node| node.children())
        .filter(|node| element_named(*node, PROCESS_NAMESPACE, "baseName"))
        .filter_map(|node| {
            let text = node.text()?.trim();
            if text.is_empty() {
                return None;
            }
            let language = node.attribute((XML_NAMESPACE, "lang")).unwrap_or("und");
            Some(MultilingualName::new(language.to_owned(), text.to_owned()))
        })
        .collect();
    if names.is_empty() {
        return Err(ParseError::new(
            ParseErrorKind::MissingName,
            "missing non-empty process:name/process:baseName",
        ));
    }

    let mut declared = Vec::new();
    for (container_name, item_name) in [("exchanges", "exchange"), ("LCIAResults", "LCIAResult")] {
        let Some(container) = child_named(root, PROCESS_NAMESPACE, container_name) else {
            continue;
        };
        for item in container
            .children()
            .filter(|node| element_named(*node, PROCESS_NAMESPACE, item_name))
        {
            for other in item
                .children()
                .filter(|node| element_named(*node, COMMON_NAMESPACE, "other"))
            {
                for amount in other
                    .children()
                    .filter(|node| element_named(*node, EPD_2013_NAMESPACE, "amount"))
                {
                    let Some(code) = amount.attribute((EPD_2013_NAMESPACE, "module")) else {
                        continue;
                    };
                    let module = InformationModule::from_code(code).ok_or_else(|| {
                        ParseError::new(
                            ParseErrorKind::InvalidInformationModule,
                            format!("unsupported EPD module code `{code}`"),
                        )
                    })?;
                    if !declared.contains(&module) {
                        declared.push(module);
                    }
                }
            }
        }
    }
    let modules = InformationModule::ALL
        .into_iter()
        .filter(|module| declared.contains(module))
        .collect();

    Ok(Document::parsed(
        input,
        ProcessDataset::new(version, uuid, names, modules),
    ))
}

fn element_named(node: Node<'_, '_>, namespace: &str, local_name: &str) -> bool {
    node.is_element()
        && node.tag_name().namespace() == Some(namespace)
        && node.tag_name().name() == local_name
}

fn child_named<'a, 'input>(
    node: Node<'a, 'input>,
    namespace: &str,
    local_name: &str,
) -> Option<Node<'a, 'input>> {
    node.children().find(|child| {
        child.is_element()
            && child.tag_name().namespace() == Some(namespace)
            && child.tag_name().name() == local_name
    })
}

fn is_canonical_uuid(value: &str) -> bool {
    value.len() == 36
        && value.bytes().enumerate().all(|(index, byte)| match index {
            8 | 13 | 18 | 23 => byte == b'-',
            _ => byte.is_ascii_hexdigit(),
        })
}

fn enforce_tree_limits(parsed: &XmlDocument<'_>, options: ParseOptions) -> Result<(), ParseError> {
    for node in parsed.descendants().filter(roxmltree::Node::is_element) {
        let depth = node.ancestors().filter(roxmltree::Node::is_element).count();
        if depth > options.max_depth {
            return Err(ParseError::new(
                ParseErrorKind::DepthLimitExceeded,
                format!("element depth {depth} exceeds limit {}", options.max_depth),
            ));
        }
        let attributes = node.attributes().len();
        if attributes > options.max_attributes {
            return Err(ParseError::new(
                ParseErrorKind::AttributeLimitExceeded,
                format!(
                    "element has {attributes} attributes; limit is {}",
                    options.max_attributes
                ),
            ));
        }
    }
    Ok(())
}

fn map_xml_error(error: XmlError) -> ParseError {
    let kind = match error {
        XmlError::DtdDetected => ParseErrorKind::DoctypeForbidden,
        XmlError::NodesLimitReached => ParseErrorKind::NodeLimitExceeded,
        _ => ParseErrorKind::MalformedXml,
    };
    ParseError::new(kind, error.to_string())
}
