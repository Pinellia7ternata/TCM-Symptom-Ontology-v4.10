# TCM Symptom Ontology — Release v4.13.0 (candidate)

> Tag `v4.13.0` · Released 2026-11-27 · License CC-BY 4.0 · Previous archived release: v4.10 (`ontology/TCM_Symptom_Ontology_v4.10.owl`)

## Highlights

v4.13 is a **quality-repair release** built on v4.10 in three reviewed iterations
(v4.11 → v4.12 → v4.13), each validated with HermiT (0 unsatisfiable classes).

1. **Category repair (main change).** An internal audit found that `cat_睡眠类`
   (sleep category) had been used as a catch-all bucket for **354 symptom classes
   (~20% of the inventory)**, of which only ~19 are genuine sleep symptoms, and that
   all 354 classes additionally carried an erroneous asserted `PsychiatricFinding`
   parent. v4.12/v4.13 reassign **243 classes** to clinically correct homes and remove
   all 243 erroneous `PsychiatricFinding` links:
   - **3 new top-level categories** (mounted on the existing system-class lattice):
     `cat_舌象类` (tongue signs → TongueFinding, 106 classes),
     `cat_二便类` (stool & urine signs → ExcretionFinding, 63 classes),
     `cat_肺系类` (pulmonary symptoms → ThoraxFinding, 13 classes);
   - 5 flatus-family classes → `cat_肛门体征`; 56 abdominal/GI classes → `cat_脘腹_腰部体征`;
   - `cat_睡眠类` now holds 111 classes (≈19 genuine sleep symptoms + 92 classes
     pending expert-panel arbitration, listed in the change log).
2. **New base class + logical definition.** `sx_矢气` (flatus emission) created;
   `sx_矢气频作 ≡ sx_矢气 and hasModifier some FrequentAttack` — the 6th
   frequency-pattern logical definition (20 equivalence axioms in total).
3. **Repository housekeeping (round-2 review R2-1/R2-2).**
   - Added `scripts/` (10 analysis scripts + README) and
     `documentation/normalization_lexicon.csv`, `documentation/no_english_definition_121.csv`,
     completing every path named in the manuscript's Data availability statement;
   - Removed `.bak_20260917` mapping backups, `push_*.bat` helpers, `PUSH_README.md`,
     and the duplicate OWL at repository root (the canonical copy lives in `ontology/`);
   - Fixed citation metadata: the concept DOI is **10.5281/zenodo.22803649**
     (previously a superseded version DOI was quoted).

## Key figures (v4.13)

| Metric | v4.10 | v4.13 |
|---|---:|---:|
| Total classes | 1,943 | **1,947** |
| Symptom classes | 1,758 | 1,759 |
| Top-level categories | 31 | **34** |
| Equivalence axioms | 19 | **20** |
| Existential restrictions | 15,790 | 15,796 |
| Unsatisfiable classes (HermiT) | 0 | 0 |

## Files

- `ontology/TCM_Symptom_Ontology_v4.13.owl` — this release (canonical artifact)
- `ontology/TCM_Symptom_Ontology_v4.10.owl` / `v4.9` / `v4.8` — previous releases, kept for citation stability
- Change logs (in the submission workspace): 187-class and 56-class reassignment tables with per-class old/new parents

## Notes

- Base IRI unchanged (`http://OntoTCM.org.cn/ontologies/tcm_v38/`); version IRI `…/tcm_v413/4.13.0`.
- The 92 unresolved classes remain under `cat_睡眠类` pending expert arbitration in a future release.
- Manuscript alignment: the Database (Oxford) submission describes v4.10; a statistics
  refresh (31→34 categories, 1,943→1,947 classes) is queued for the next manuscript version.

---

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
