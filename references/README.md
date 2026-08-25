# Local standards references

This directory is intentionally excluded from version control and crate
packages, except for this notice.

Keep locally obtained material under `references/schema/`. ISO/CEN standards
and their annex workbooks may be used to
implement and verify source code, but possession does not establish permission
to redistribute those files in this MIT-licensed repository. Keep such material
local unless its redistribution terms have been independently verified.

The Pages build never reads or copies `references/`; its assembled artifact is
checked for PDF, workbook, and schema files before deployment.

The initial scaffold was checked against ISO 22057:2022 and its Annex A/B
workbooks. Annex B maps the standard's data-template concepts to multiple
existing exchange formats; it is not an ISO XML schema.
