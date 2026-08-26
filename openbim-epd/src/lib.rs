//! `openbim-epd` — ISO 22057 EPD data-template contracts.
//!
//! ISO 22057:2022 defines data templates for using environmental product
//! declaration (EPD) information in building information modelling. It builds
//! on the data-template concepts from ISO 23387 and the life-cycle modules used
//! by construction-product EPDs.
//!
//! # No ISO 22057 XML schema
//!
//! ISO 22057 defines the information structure and mappings; it does **not**
//! standardize one XML namespace, XSD, or wire encoding. Its informative mapping
//! material references multiple established exchange formats. Consequently this
//! crate deliberately exposes no invented ISO 22057 XML namespace and does not
//! claim that XML parsing exists.
//!
//! # Status
//!
//! **Format-neutral foundation.** The standard edition, all 18 EPD
//! information-module codes (including aggregated `A1-A3`), and composition
//! with the shared ISO 23387 [`openbim_dt::DataTemplate`] are represented and
//! tested. This core crate does not parse, write, or validate exchange formats;
//! versioned adapters such as `openbim-ilcd-epd` remain separate packages.
//!
//! # Examples
//!
//! ```
//! use openbim_epd::{InformationModule, InformationModuleGroup, StandardEdition};
//!
//! assert_eq!(StandardEdition::CURRENT.designation(), "ISO 22057:2022");
//! assert_eq!(InformationModule::A1ToA3.code(), "A1-A3");
//! assert_eq!(
//!     InformationModule::D.group(),
//!     InformationModuleGroup::BeyondSystemBoundary
//! );
//! ```
//!
//! # Repository boundary
//!
//! EPD consumes shared data-template and, eventually, IFC contracts. IFC, core,
//! and codec crates must never depend on EPD. The `openbimrs/openbim`
//! integration repository pins compatible family revisions without reversing
//! that dependency direction.

#![forbid(unsafe_code)]

/// An edition of the EPD data-template standard represented by this crate.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum StandardEdition {
    /// ISO 22057:2022, the first published edition.
    Iso22057_2022,
}

impl StandardEdition {
    /// The edition used for new EPD data-template work.
    pub const CURRENT: Self = Self::Iso22057_2022;

    /// The normative standard designation.
    #[must_use]
    pub const fn designation(self) -> &'static str {
        match self {
            Self::Iso22057_2022 => "ISO 22057:2022",
        }
    }
}

/// An ISO 22057 EPD template composed from the ISO 23387 vocabulary.
///
/// ISO 22057 specializes BIM data-template concepts; it does not own a second
/// property, unit, quantity-kind, or object-type model. Keeping the underlying
/// [`openbim_dt::DataTemplate`] intact gives EPD and LOIN the same type identity
/// without making either standard depend on the other.
///
/// This type is format-neutral. It does not imply ILCD+EPD XML, provider API,
/// or Annex A conformance.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct EpdDataTemplate {
    standard: StandardEdition,
    data_template: openbim_dt::DataTemplate,
}

impl EpdDataTemplate {
    /// Binds an ISO 23387 data template to the current ISO 22057 edition.
    #[must_use]
    pub const fn new(data_template: openbim_dt::DataTemplate) -> Self {
        Self {
            standard: StandardEdition::CURRENT,
            data_template,
        }
    }

    /// The ISO 22057 edition governing this EPD template.
    #[must_use]
    pub const fn standard(&self) -> StandardEdition {
        self.standard
    }

    /// The shared ISO 23387 data-template contract.
    #[must_use]
    pub const fn data_template(&self) -> &openbim_dt::DataTemplate {
        &self.data_template
    }

    /// Consumes the EPD binding and returns the shared ISO 23387 template.
    #[must_use]
    pub fn into_data_template(self) -> openbim_dt::DataTemplate {
        self.data_template
    }
}

/// A semantic grouping for EPD information-module codes.
///
/// This is deliberately broader than a life-cycle stage: module D represents
/// benefits and loads beyond the product-system boundary.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum InformationModuleGroup {
    /// Product stage: modules A1 to A3 and the aggregated A1-A3 value.
    Product,
    /// Construction-process stage: modules A4 and A5.
    ConstructionProcess,
    /// Use stage: modules B1 to B7.
    Use,
    /// End-of-life stage: modules C1 to C4.
    EndOfLife,
    /// Benefits and loads beyond the product-system boundary: module D.
    BeyondSystemBoundary,
}

/// One of the 18 EPD information-module codes from A1 through D.
///
/// `A1ToA3` represents the aggregated `A1-A3` value that appears alongside
/// the individual A1, A2, and A3 values in the ISO 22057 template.
#[derive(Debug, Clone, Copy, PartialEq, Eq, PartialOrd, Ord, Hash)]
pub enum InformationModule {
    /// Raw-material supply.
    A1,
    /// Transport to the manufacturer.
    A2,
    /// Manufacturing.
    A3,
    /// Aggregated product stage covering A1, A2, and A3.
    A1ToA3,
    /// Transport to the construction site.
    A4,
    /// Construction and installation.
    A5,
    /// Use.
    B1,
    /// Maintenance.
    B2,
    /// Repair.
    B3,
    /// Replacement.
    B4,
    /// Refurbishment.
    B5,
    /// Operational energy use.
    B6,
    /// Operational water use.
    B7,
    /// Deconstruction and demolition.
    C1,
    /// Transport during end of life.
    C2,
    /// Waste processing.
    C3,
    /// Disposal.
    C4,
    /// Benefits and loads beyond the system boundary.
    D,
}

impl InformationModule {
    /// Every module in normative order.
    pub const ALL: [Self; 18] = [
        Self::A1,
        Self::A2,
        Self::A3,
        Self::A1ToA3,
        Self::A4,
        Self::A5,
        Self::B1,
        Self::B2,
        Self::B3,
        Self::B4,
        Self::B5,
        Self::B6,
        Self::B7,
        Self::C1,
        Self::C2,
        Self::C3,
        Self::C4,
        Self::D,
    ];

    /// The compact module code used by EPD datasets.
    #[must_use]
    pub const fn code(self) -> &'static str {
        match self {
            Self::A1 => "A1",
            Self::A2 => "A2",
            Self::A3 => "A3",
            Self::A1ToA3 => "A1-A3",
            Self::A4 => "A4",
            Self::A5 => "A5",
            Self::B1 => "B1",
            Self::B2 => "B2",
            Self::B3 => "B3",
            Self::B4 => "B4",
            Self::B5 => "B5",
            Self::B6 => "B6",
            Self::B7 => "B7",
            Self::C1 => "C1",
            Self::C2 => "C2",
            Self::C3 => "C3",
            Self::C4 => "C4",
            Self::D => "D",
        }
    }

    /// Resolves an exact, case-sensitive EPD module code.
    #[must_use]
    pub const fn from_code(code: &str) -> Option<Self> {
        match code.as_bytes() {
            b"A1" => Some(Self::A1),
            b"A2" => Some(Self::A2),
            b"A3" => Some(Self::A3),
            b"A1-A3" => Some(Self::A1ToA3),
            b"A4" => Some(Self::A4),
            b"A5" => Some(Self::A5),
            b"B1" => Some(Self::B1),
            b"B2" => Some(Self::B2),
            b"B3" => Some(Self::B3),
            b"B4" => Some(Self::B4),
            b"B5" => Some(Self::B5),
            b"B6" => Some(Self::B6),
            b"B7" => Some(Self::B7),
            b"C1" => Some(Self::C1),
            b"C2" => Some(Self::C2),
            b"C3" => Some(Self::C3),
            b"C4" => Some(Self::C4),
            b"D" => Some(Self::D),
            _ => None,
        }
    }

    /// The semantic group containing this information-module code.
    ///
    /// Module D returns [`InformationModuleGroup::BeyondSystemBoundary`]; it is
    /// deliberately not described as a life-cycle stage.
    #[must_use]
    pub const fn group(self) -> InformationModuleGroup {
        match self {
            Self::A1 | Self::A2 | Self::A3 | Self::A1ToA3 => InformationModuleGroup::Product,
            Self::A4 | Self::A5 => InformationModuleGroup::ConstructionProcess,
            Self::B1 | Self::B2 | Self::B3 | Self::B4 | Self::B5 | Self::B6 | Self::B7 => {
                InformationModuleGroup::Use
            }
            Self::C1 | Self::C2 | Self::C3 | Self::C4 => InformationModuleGroup::EndOfLife,
            Self::D => InformationModuleGroup::BeyondSystemBoundary,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn current_edition_has_the_normative_designation() {
        assert_eq!(StandardEdition::CURRENT.designation(), "ISO 22057:2022");
    }

    #[test]
    fn information_modules_are_complete_and_round_trip() {
        const EXPECTED_CODES: [&str; 18] = [
            "A1", "A2", "A3", "A1-A3", "A4", "A5", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "C1",
            "C2", "C3", "C4", "D",
        ];

        assert_eq!(
            InformationModule::ALL.map(InformationModule::code),
            EXPECTED_CODES
        );

        for module in InformationModule::ALL {
            assert_eq!(InformationModule::from_code(module.code()), Some(module));
        }
    }

    #[test]
    fn information_modules_map_to_their_groups() {
        assert_eq!(
            InformationModule::A1.group(),
            InformationModuleGroup::Product
        );
        assert_eq!(
            InformationModule::A3.group(),
            InformationModuleGroup::Product
        );
        assert_eq!(
            InformationModule::A1ToA3.group(),
            InformationModuleGroup::Product
        );
        assert_eq!(
            InformationModule::A4.group(),
            InformationModuleGroup::ConstructionProcess
        );
        assert_eq!(InformationModule::B7.group(), InformationModuleGroup::Use);
        assert_eq!(
            InformationModule::C4.group(),
            InformationModuleGroup::EndOfLife
        );
        assert_eq!(
            InformationModule::D.group(),
            InformationModuleGroup::BeyondSystemBoundary
        );
    }

    #[test]
    fn unknown_module_codes_are_rejected() {
        assert_eq!(InformationModule::from_code("A0"), None);
        assert_eq!(InformationModule::from_code("a1"), None);
        assert_eq!(InformationModule::from_code(""), None);
    }
}
