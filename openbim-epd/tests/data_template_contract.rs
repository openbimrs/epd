use std::str::FromStr;

use openbim_dt::{Concept, DataTemplate, DateTime, Guid, MultiLanguageText, Subject};
use openbim_epd::{EpdDataTemplate, StandardEdition};

fn text(value: &str) -> MultiLanguageText {
    MultiLanguageText::new("en", value).unwrap()
}

#[test]
fn iso_22057_template_composes_the_shared_iso_23387_contract() {
    let concept = Concept::new(
        Guid::from_str("10000000-0000-0000-0000-000000000000").unwrap(),
        DateTime::from_str("2026-08-26T00:00:00Z").unwrap(),
        text("Environmental product declaration"),
        text("Synthetic test template"),
    );
    let template = DataTemplate::new(Subject::new(concept));
    let epd = EpdDataTemplate::new(template.clone());

    assert_eq!(epd.standard(), StandardEdition::CURRENT);
    assert_eq!(epd.data_template(), &template);
    assert_eq!(epd.into_data_template(), template);
}
