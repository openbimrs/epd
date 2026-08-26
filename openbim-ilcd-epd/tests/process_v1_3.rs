use openbim_epd::InformationModule;
use openbim_ilcd_epd::{Document, FormatVersion, ParseErrorKind, ParseOptions};

const FIXTURE: &[u8] = include_bytes!(
    "fixtures/upstream-v1.3/processes/EPDv1.3_example_57a4ae65-d305-421e-b21f-a3f0c35b8abe.xml"
);

#[test]
fn parses_the_official_v1_3_process_fixture() {
    let document = Document::parse(FIXTURE).unwrap();
    let process = document.process();

    assert_eq!(document.format_version(), FormatVersion::V1_3);
    assert_eq!(process.uuid(), "57a4ae65-d305-421e-b21f-a3f0c35b8abe");
    assert_eq!(process.name("en"), Some("Wood panel"));
    assert_eq!(process.name("de"), Some("Holzpanel"));
    assert_eq!(
        process.modules(),
        &[
            InformationModule::A1ToA3,
            InformationModule::A4,
            InformationModule::C3,
            InformationModule::C4,
            InformationModule::D,
        ]
    );
}

#[test]
fn exact_original_bytes_survive_an_unmodified_round_trip() {
    let document = Document::parse(FIXTURE).unwrap();
    assert_eq!(document.as_bytes(), FIXTURE);
    let mut written = Vec::new();
    document.write_original(&mut written).unwrap();
    assert_eq!(written, FIXTURE);
    assert_eq!(document.into_bytes().as_ref(), FIXTURE);
}

#[test]
fn unknown_namespaced_content_is_preserved_exactly() {
    let xml = br#"<?xml version="1.0"?><processDataSet xmlns="http://lca.jrc.it/ILCD/Process" xmlns:common="http://lca.jrc.it/ILCD/Common" xmlns:epd="http://www.iai.kit.edu/EPD/2013" xmlns:epd2="http://www.indata.network/EPD/2019" xmlns:x="urn:example:unknown" epd2:epd-version="1.3"><processInformation><dataSetInformation><common:UUID>57a4ae65-d305-421e-b21f-a3f0c35b8abe</common:UUID><name><baseName xml:lang="en">Synthetic</baseName></name><common:other><x:future answer="42">kept</x:future></common:other></dataSetInformation></processInformation><exchanges><exchange><common:other><epd:amount epd:module="D">1</epd:amount></common:other></exchange></exchanges></processDataSet>"#;
    let document = Document::parse(xml).unwrap();
    assert_eq!(document.as_bytes(), xml);
    assert_eq!(document.process().modules(), &[InformationModule::D]);
}

#[test]
fn rejects_wrong_root_namespace() {
    let xml = minimal_xml("urn:not-ilcd-process", "1.3", "A1");
    assert_kind(&xml, ParseErrorKind::UnexpectedRoot);
}

#[test]
fn rejects_missing_or_unsupported_format_version() {
    let missing = br#"<processDataSet xmlns="http://lca.jrc.it/ILCD/Process"><processInformation><dataSetInformation/></processInformation></processDataSet>"#;
    assert_kind(missing, ParseErrorKind::MissingFormatVersion);
    let unsupported = minimal_xml("http://lca.jrc.it/ILCD/Process", "1.2", "A1");
    assert_kind(&unsupported, ParseErrorKind::UnsupportedFormatVersion);
}

#[test]
fn rejects_invalid_module_in_the_epd_namespace() {
    let xml = minimal_xml("http://lca.jrc.it/ILCD/Process", "1.3", "A0");
    assert_kind(&xml, ParseErrorKind::InvalidInformationModule);
}

#[test]
fn rejects_doctypes_and_malformed_xml() {
    let doctype = br#"<!DOCTYPE processDataSet [<!ENTITY x "boom">]><processDataSet xmlns="http://lca.jrc.it/ILCD/Process"/>"#;
    assert_kind(doctype, ParseErrorKind::DoctypeForbidden);
    assert_kind(b"<processDataSet>", ParseErrorKind::MalformedXml);
}

#[test]
fn enforces_configured_resource_limits() {
    let bytes = minimal_xml("http://lca.jrc.it/ILCD/Process", "1.3", "A1");
    let options = ParseOptions::default().with_max_bytes(bytes.len() - 1);
    assert_eq!(
        Document::parse_with_options(&bytes, options)
            .unwrap_err()
            .kind(),
        ParseErrorKind::InputTooLarge
    );

    let options = ParseOptions::default().with_max_nodes(2);
    assert_eq!(
        Document::parse_with_options(&bytes, options)
            .unwrap_err()
            .kind(),
        ParseErrorKind::NodeLimitExceeded
    );

    let options = ParseOptions::default().with_max_attributes(0);
    assert_eq!(
        Document::parse_with_options(&bytes, options)
            .unwrap_err()
            .kind(),
        ParseErrorKind::AttributeLimitExceeded
    );

    let deep = br#"<processDataSet xmlns="http://lca.jrc.it/ILCD/Process" xmlns:epd2="http://www.indata.network/EPD/2019" epd2:epd-version="1.3"><a><b><c/></b></a></processDataSet>"#;
    let options = ParseOptions::default().with_max_depth(2);
    assert_eq!(
        Document::parse_with_options(deep, options)
            .unwrap_err()
            .kind(),
        ParseErrorKind::DepthLimitExceeded
    );
}

#[test]
fn validates_required_process_identity_and_name() {
    let xml =
        String::from_utf8(minimal_xml("http://lca.jrc.it/ILCD/Process", "1.3", "A1")).unwrap();
    let missing_uuid = xml.replace(
        "<common:UUID>57a4ae65-d305-421e-b21f-a3f0c35b8abe</common:UUID>",
        "",
    );
    assert_kind(missing_uuid.as_bytes(), ParseErrorKind::MissingUuid);
    let invalid_uuid = xml.replace("57a4ae65-d305-421e-b21f-a3f0c35b8abe", "not-a-uuid");
    assert_kind(invalid_uuid.as_bytes(), ParseErrorKind::InvalidUuid);
    let missing_name = xml.replace(
        "<name><baseName xml:lang=\"en\">Synthetic</baseName></name>",
        "",
    );
    assert_kind(missing_name.as_bytes(), ParseErrorKind::MissingName);
}

#[test]
fn identity_is_read_from_data_set_information_not_an_extension() {
    let xml = String::from_utf8(minimal_xml("http://lca.jrc.it/ILCD/Process", "1.3", "A1"))
        .unwrap()
        .replace(
            "<processInformation>",
            "<common:UUID>00000000-0000-0000-0000-000000000000</common:UUID><name><baseName xml:lang=\"en\">Shadow</baseName></name><processInformation>",
        );
    let document = Document::parse(xml.as_bytes()).unwrap();
    assert_eq!(
        document.process().uuid(),
        "57a4ae65-d305-421e-b21f-a3f0c35b8abe"
    );
    assert_eq!(document.process().name("en"), Some("Synthetic"));
}

#[test]
fn semantic_fields_are_scoped_to_their_schema_paths() {
    let xml = String::from_utf8(minimal_xml("http://lca.jrc.it/ILCD/Process", "1.3", "A1"))
        .unwrap()
        .replace(
            "<name>",
            "<common:other><baseName xml:lang=\"en\">Sibling shadow</baseName><epd:amount epd:module=\"A0\">99</epd:amount></common:other><name><common:other><baseName xml:lang=\"en\">Nested shadow</baseName></common:other>",
        );
    let document = Document::parse(xml.as_bytes()).unwrap();
    assert_eq!(document.process().name("en"), Some("Synthetic"));
    assert_eq!(document.process().modules(), &[InformationModule::A1]);
}

#[test]
fn version_marker_must_use_the_indata_namespace() {
    let xml = String::from_utf8(minimal_xml("http://lca.jrc.it/ILCD/Process", "1.3", "A1"))
        .unwrap()
        .replace("epd2:epd-version=\"1.3\"", "epd-version=\"1.3\"");
    assert_kind(xml.as_bytes(), ParseErrorKind::MissingFormatVersion);
}

#[test]
fn rejects_non_utf8_input() {
    assert_kind(&[0xff, 0xfe], ParseErrorKind::InvalidUtf8);
}

fn minimal_xml(root_namespace: &str, version: &str, module: &str) -> Vec<u8> {
    format!(
        r#"<processDataSet xmlns="{root_namespace}" xmlns:common="http://lca.jrc.it/ILCD/Common" xmlns:epd="http://www.iai.kit.edu/EPD/2013" xmlns:epd2="http://www.indata.network/EPD/2019" epd2:epd-version="{version}"><processInformation><dataSetInformation><common:UUID>57a4ae65-d305-421e-b21f-a3f0c35b8abe</common:UUID><name><baseName xml:lang="en">Synthetic</baseName></name></dataSetInformation></processInformation><exchanges><exchange><common:other><epd:amount epd:module="{module}">1</epd:amount></common:other></exchange></exchanges></processDataSet>"#
    )
    .into_bytes()
}

fn assert_kind(xml: &[u8], expected: ParseErrorKind) {
    assert_eq!(Document::parse(xml).unwrap_err().kind(), expected);
}
