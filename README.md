# TCM Symptom Ontology (TCM-SO) — Bilingual Release v4.14

> A comprehensive, bilingual (Chinese/English) OWL 2 ontology of Traditional Chinese Medicine (TCM) symptoms, with formal logical axioms and expert-confirmed cross-terminology alignment to **HPO**, **SNOMED CT**, and **ICD-11**.

This repository accompanies the manuscript *"TCM-SO: A Comprehensive, Bilingual, Logically Axiomatized Ontology of Traditional Chinese Medicine Symptoms with HPO, SNOMED CT and ICD-11 Alignment"* (submitted to *Database: The Journal of Biological Databases and Curation*, Oxford). The manuscript describes release v4.10; v4.14 is a quality-repair release (see `RELEASE_NOTES.md`).

---

## 1. What's in this repository

```
TCM-Symptom-Ontology/
├── README.md                                  # this file
├── LICENSE                                    # CC-BY 4.0
├── CITATION.cff                               # citation + DOI metadata (Zenodo)
├── RELEASE_NOTES.md                           # per-release notes
├── ontology/
│   ├── TCM_Symptom_Ontology_v4.14.owl         # current release (OWL 2 RDF/XML)
│   └── TCM_Symptom_Ontology_v4.8/4.9/4.10.owl # previous releases (citation stability)
├── mappings/                                  # expert-confirmed cross-terminology alignments
│   ├── HPO_mapping.csv                        # 649 rows, with mapType
│   ├── SNOMEDCT_mapping.csv                   # 707 rows
│   ├── ICD11_mapping.csv                      # 973 rows
│   ├── TCM-SO-HPO.sssom.tsv                   # SSSOM sets, skos predicates +
│   ├── TCM-SO-SNOMEDCT.sssom.tsv              #   curation_status=under_review flags
│   └── TCM-SO-ICD11.sssom.tsv                 #   (78 rows flagged)
├── documentation/                             # machine-readable supplementary tables
│   ├── mapping_provenance.csv
│   ├── translation_tier_audit.csv
│   ├── clinical_normalization_results.csv
│   ├── clinical_normalization_spotcheck_200.csv / _scored.csv
│   ├── kappa_reannotation_sheet_rated.csv
│   ├── findingSite_category_conflicts.csv
│   ├── normalization_lexicon.csv              # 2,043 lexicon terms
│   ├── no_english_definition_122.csv
│   └── BioPortal_submission_guide.md
└── scripts/                                   # analysis & reproducibility scripts
    ├── m1_normalization.py                    # TCM-SD corpus normalization
    ├── m3_translation_tier_audit.py           # definition-tier audit
    ├── m4_spotcheck.py / m4_spotcheck_compute.py
    ├── m5_provenance.py                       # mapping provenance decomposition
    ├── kappa_sample_and_compute.py / kappa_report.py
    ├── make_sssom.py / annotate_sssom_curation_status.py
    ├── composite_definition_outlook.py
    └── README.md
```

## 2. Ontology at a glance (v4.14)

| Metric | Value |
|---|---|
| Total classes | 1,947 |
| Symptom classes (`sx_`) | 1,759 |
| Top-level categories (`cat_`) | 34 |
| Modifier / value classes | 154 |
| Existential restrictions (`someValuesFrom`) | 15,795 |
| Equivalence axioms | 20 (10 system-level + 10 symptom-level) |
| Property chains | 1 |
| Object / datatype / annotation properties | 20 / 4 / 11 |
| Bilingual labels (zh + en) | 100% of classes |
| English textual definitions | 1,637 / 1,759 symptom classes (93.1%); 886 (50.4%) manually translated |
| Cross-standard mappings | 2,329 (HPO 649, SNOMED CT 707, ICD-11 973); 979 classes (55.7%) aligned |
| Unsatisfiable classes (HermiT) | 0 |

**Logical foundation.** Anchored to BFO 2.0 (symptoms under `DependentContinuant → ClinicalFinding`, disjoint from Disease and Syndrome), with a dual-axis design: an asserted examination-workflow category axis (`cat_`) orthogonal to an inferred anatomical finding-site axis (system `*Finding` classes with equivalence axioms), plus a `findingSite ∘ partOf ⊑ findingSite` property chain.

**v4.14 category repair.** 243 symptom classes were re-homed from a catch-all bucket (`cat_睡眠类`) to clinically correct categories, including three new top-level categories (`cat_舌象类`, `cat_二便类`, `cat_肺系类`); 92 classes await expert arbitration. Details in `RELEASE_NOTES.md`.

**IRIs.** Base IRI `http://OntoTCM.org.cn/ontologies/tcm_v38/ontology`; version IRI `http://OntoTCM.org.cn/ontologies/tcm_v414/4.14.0`.

## 3. Cross-terminology alignment (expert-confirmed)

| Target terminology | Mappings | Symptom classes covered | Coverage |
|---|---:|---:|---:|
| HPO | 649 | 518 | 29.5% |
| SNOMED CT | 707 | 428 | 24.3% |
| ICD-11 | 973 | 664 | 37.8% |
| **Union (≥1 of the three)** | — | **979** | **55.7%** |

- All 2,329 mappings carry skos predicates in the SSSOM sets (522 `exactMatch`, 1,807 `closeMatch`).
- A double-blind 3-rater re-annotation of 421 sampled mappings reached 82.2% consensus acceptance; the 75 non-consensus items (78 rows) are flagged `curation_status=under_review` in the SSSOM sets and queued for re-arbitration (full data in `documentation/kappa_reannotation_sheet_rated.csv`).
- Provenance: 2,080 mappings (89.3%) are new contributions of the 2024–25 workflow; 249 are inherited from the predecessor standard T/CACM 1641—2025.
- SNOMED CT and ICD-11 content remain subject to their own licences; the mappings are annotations for reference only.

## 4. How to use

- **Open in Protégé (≥5.5)** — load `ontology/TCM_Symptom_Ontology_v4.14.owl` and run HermiT (≈10–12 s, 0 unsatisfiable classes).
- **DL query examples** — `ClinicalFinding and (findingSite some Tongue) and (dueTo some FireEvil)` returns heat-related tongue findings; `hasModifier some FrequentAttack` returns the six frequency-defined symptoms.
- **Mappings** — `pandas.read_csv(..., encoding="utf-8-sig")`; SSSOM sets follow the SSSOM spec.
- **Reproduce the evaluations** — see `scripts/README.md`.

## 5. License

Released under **Creative Commons Attribution 4.0 International (CC-BY 4.0)**. See `LICENSE`.

## 6. How to cite

> Chen C, Chen Z, Han Z, Lei L. *TCM Symptom Ontology (TCM-SO)* (version 4.14). Zenodo (2026). Concept DOI: https://doi.org/10.5281/zenodo.22803649

The concept DOI always resolves to the latest archived version.

## 7. Acknowledgements

Symptom inventory compiled from Chinese national TCM terminology standards (GB/T 16751 series, T/CACM 1641—2025) and standard TCM diagnostics textbooks; curated by three senior TCM experts. English definitions produced by a tiered machine-translation + manual-expert pipeline.
