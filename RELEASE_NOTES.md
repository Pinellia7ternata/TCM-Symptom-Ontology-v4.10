# TCM Symptom Ontology — Release v4.5.0

> Tag `v4.5.0` · Released 2026-07-31 · License CC-BY 4.0 · Previous tag: `v4.4.0`

## Highlights

The TCM Symptom Ontology (TCM-SO) v4.5.0 is, to our knowledge, the first TCM symptom
ontology to combine three co-equal advances:

1. **Largest-scale, standards-anchored coverage** — 1,758 symptom concepts across 31
   clinical categories (1,938 classes total), with 15,199 subclass axioms and 12,928
   existential restrictions, formally grounded in BFO 2.0.
2. **Expert-curated bilingual definitions** — 100% of classes carry Chinese/English labels;
   1,637 symptom classes (93.1%) carry an English textual definition in HPO definitional
   style (half manually translated and reviewed sentence-by-sentence by bilingual TCM experts).
3. **Expert-confirmed alignment to international standards** — 649 HPO, 707 SNOMED CT and
   973 ICD-11 mappings, each typed *exact* / *close*, covering **979 of 1,758 symptom
   classes (55.7%)**.

The release passes full description-logic consistency checking (HermiT/Pellet:
0 unsatisfiable classes).

## What's Changed (since v4.4.0)

This release extends v4.4.0 — which already carried the HPO alignment and the bilingual
layer — with the two remaining international-standard alignments:

- **Added SNOMED CT alignment** — 639 new expert-confirmed mappings, bringing the total to
  **707 mappings** across **428 symptom classes (24.3%)**.
- **Added ICD-11 alignment** — 905 new expert-confirmed mappings, bringing the total to
  **973 mappings** across **664 symptom classes (37.8%)**.
- **Union coverage reaches 55.7%** — **979 of 1,758 symptom classes** now align to at least
  one of HPO / SNOMED CT / ICD-11; 171 classes align to all three.
- **Mapping tables exported as CSV** — `mappings/HPO_mapping.csv` (649),
  `mappings/SNOMEDCT_mapping.csv` (707), `mappings/ICD11_mapping.csv` (973).
- **Machine-readable citation metadata** — `CITATION.cff` added for Zenodo archiving and
  DOI minting.
- **BioPortal submission guide** — `documentation/BioPortal_submission_guide.md` added.
- **Version IRI** updated to `http://OntoTCM.org.cn/ontologies/tcm_v45/4.5.0`.

## What's Included

```
ontology/TCM_Symptom_Ontology_v4.5.owl        # OWL 2 (RDF/XML), 1,938 classes, 6.62 MB
mappings/HPO_mapping.csv                       # 649 rows
mappings/SNOMEDCT_mapping.csv                  # 707 rows
mappings/ICD11_mapping.csv                     # 973 rows
documentation/BioPortal_submission_guide.md
README.md
LICENSE                                       # CC-BY 4.0 (full text)
CITATION.cff
```

## Mapping Summary

| Terminology       | Mappings | Symptom classes | Coverage |
|-------------------|---------:|----------------:|---------:|
| HPO               | 649      | 518             | 29.5%    |
| SNOMED CT         | 707      | 428             | 24.3%    |
| ICD-11            | 973      | 664             | 37.8%    |
| **Union (≥1)**    | —        | **979**         | **55.7%** |
| Triple intersection | —      | 171             | —        |

Each mapping row records the symptom local name, Chinese label, English label, the target
terminology code, the target term, and the `mapType` (*exact* / *close*).

## How to Cite

> Chen C, et al. (2026). *TCM Symptom Ontology: a large-scale bilingual ontology of
> Traditional Chinese Medicine symptoms with HPO / SNOMED CT / ICD-11 alignment*
> (version 4.5). Zenodo. https://doi.org/10.5281/zenodo.21769826

Replace the DOI placeholder with the Zenodo DOI assigned at archiving. Machine-readable
metadata is in `CITATION.cff`.

## License

Released under the Creative Commons Attribution 4.0 International (CC-BY 4.0) license.
Free to download, reuse, and redistribute with attribution.
