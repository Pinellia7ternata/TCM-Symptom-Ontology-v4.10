# scripts/ - analysis and release scripts

Machine-readable companions to the manuscript (Database, TCM-SO v4.10 submission).

## Reproducible normalization evaluation (manuscript M4 / Supplementary S9)

- **m1_normalization.py** - repository-runnable version. Reads
  `documentation/normalization_lexicon.csv` (2,043 lexicon terms) and the TCM-SD
  corpus zip (not redistributed; Ren et al., CCL 2022, CC BY-NC-SA 4.0,
  https://tianchi.aliyun.com/dataset/139034). Reproduces exactly:
  444/1,758 classes attested (25.3%), conservative 236 (13.4%),
  460,692 mention instances (one count per distinct (lexicon term, record)
  co-occurrence), 43,180/43,180 records with >=1 mention, median 10 symptoms
  per record (IQR 8-13).

```
python scripts/m1_normalization.py path/to/TCM_SD_with_knowledge.zip
```

## Original analysis scripts (provenance; local Windows paths preserved)

| script | purpose |
|---|---|
| m4_spotcheck.py | 200-mention double-blind spot-check sample construction (reservoir sampling, seed 20260920) |
| m4_spotcheck_compute.py | double-blind precision / agreement computation (55.5%, Cohen's kappa 0.08) |
| kappa_sample_and_compute.py | 421-mapping stratified double-blind IAA sample and kappa/AC1/AC2 computation |
| kappa_report.py | IAA report assembly |
| m3_translation_tier_audit.py | bilingual definition-tier spot-check and T_B_high coverage proxy |
| m5_provenance.py | mapping provenance decomposition (2,080 new / 249 inherited) |
| make_sssom.py | SSSOM mapping-set export (2,329 mappings, skos predicates) |
| annotate_sssom_curation_status.py | flags the 78 non-consensus rows `curation_status = under_review` |
| composite_definition_outlook.py | composite-symptom definability outlook (Discussion): strict label decomposition (7) and modifier-annotation coverage (1,749 / 99.5%) |

These are the original one-off analysis scripts kept verbatim for transparency;
hardcoded local paths are documented in each file header.
