use std::fs;
use std::path::Path;

#[test]
fn mirrored_upstream_corpus_is_xml_only_and_well_formed() {
    let root = Path::new(env!("CARGO_MANIFEST_DIR")).join("tests/fixtures/upstream-v1.3");
    let mut xml_count = 0;
    visit(&root, &mut |path| {
        let extension = path.extension().and_then(|value| value.to_str());
        if extension == Some("xml") {
            xml_count += 1;
            let bytes = fs::read(path).unwrap();
            let text = std::str::from_utf8(&bytes).unwrap();
            roxmltree::Document::parse(text).unwrap();
        } else {
            let name = path.file_name().and_then(|value| value.to_str()).unwrap();
            assert!(matches!(
                name,
                "SHA256SUMS" | "SOURCE.md" | "UPSTREAM-LICENSE-APACHE-2.0.txt"
            ));
        }
    });
    assert_eq!(xml_count, 45);
}

fn visit(root: &Path, callback: &mut impl FnMut(&Path)) {
    for entry in fs::read_dir(root).unwrap() {
        let path = entry.unwrap().path();
        if path.is_dir() {
            visit(&path, callback);
        } else {
            callback(&path);
        }
    }
}
