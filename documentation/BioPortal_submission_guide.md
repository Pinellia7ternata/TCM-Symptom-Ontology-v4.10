# BioPortal Submission Guide — TCM Symptom Ontology (v4.5)

This guide records how to submit the TCM Symptom Ontology to the **NCBO BioPortal**
so that it is publicly indexed and resolvable alongside HPO, SNOMED CT, and ICD-11.
BioPortal registration is one of the two open-access prerequisites for a
*Scientific Data* submission (the other is the GitHub/Zenodo archive described in the README).

---

## 1. Pre-submission checklist

Before submitting, confirm the ontology file meets BioPortal's requirements:

| Requirement | Status in v4.5 | Note |
|---|---|---|
| OWL 2 (RDF/XML) format | ✅ | `ontology/TCM_Symptom_Ontology_v4.5.owl` |
| Parses with a standard reasoner | ✅ | HermiT/Pellet: 0 unsatisfiable classes |
| Unique class IRIs | ✅ | `sx_*`, `cat_*`, `bs_*`, `m_*`, `q_*`, `e_*`, `f_*` namespaces |
| Human-readable labels | ✅ | `rdfs:label` (zh + en) on every class |
| Definitions / comments | ✅ | `rdfs:comment` / definition annotations present |
| Version IRI | ✅ | `http://OntoTCM.org.cn/ontologies/tcm_v45/4.5.0` |
| License declared | ✅ | CC-BY 4.0 (see `LICENSE`) |
| Contact person + email | ⚠️ | **fill in before submitting** |
| Publicly resolvable IRI (PURL) | ⚠️ | see §4 |

> ⚠️ The base IRI currently uses `http://OntoTCM.org.cn/ontologies/tcm_v38/ontology`.
> BioPortal does **not** require the IRI to resolve, but a stable PURL is strongly
> recommended for long-term citability. Options are described in §4.

---

## 2. Submit via the web UI (recommended for first submission)

1. Create a free account at <https://bioportal.bioontology.org/> (sign in with ORCID or email).
2. Go to **"New Ontology"** (top-right menu → *Account* → *My Ontologies* → *Add ontology*).
3. Fill the submission form:

   | Field | Value |
   |---|---|
   | **Ontology file** | upload `TCM_Symptom_Ontology_v4.5.owl` |
   | **Acronym / short name** | `TCM-SO` |
   | **Name** | `TCM Symptom Ontology` |
   | **Description** | paste the abstract-style summary from README §1–§2 |
   | **Homepage** | the GitHub repo URL (after you publish it) |
   | **License** | Creative Commons Attribution 4.0 |
   | **Publication** | the *Scientific Data* manuscript (DOI once assigned) |
   | **Contact** | your name + email |
   | **Categories** | Traditional Medicine; Symptoms; Phenotypes |
   | **Has ontologies / mappings** | leave blank unless you also upload the mapping files |

4. Choose **"Process the ontology with the annotator"** = yes (enables text annotation).
5. Submit. BioPortal will (a) parse the OWL, (b) extract the class hierarchy and
   properties, and (c) run the indexing job. Processing time scales with size
   (~1,938 classes / ~6.6 MB → usually a few minutes).
6. After processing, verify the ontology page shows the 31 `cat_*` top categories
   and that `rdfs:label@en` is displayed. Spot-check a known class
   (e.g., `sx_头痛` / *Headache*) to confirm HPO/SNOMED/ICD-11 cross-references render.

---

## 3. Submit via API (for re-submission / version updates)

BioPortal exposes a REST API. After the first UI submission you can update with:

```bash
curl -X POST \
  -H "Authorization: apikey YOUR_BIOPORTAL_APIKEY" \
  -F "file=@ontology/TCM_Symptom_Ontology_v4.5.owl" \
  -F "ontology=GITHUB_REPO_URL_OR_PURL" \
  https://data.bioontology.org/ontologies/TCM-SO/submissions
```

(Replace `YOUR_BIOPORTAL_APIKEY` with the key from *Account → API Key*.)

---

## 4. IRI / PURL recommendation (important for citability)

The current base IRI `http://OntoTCM.org.cn/ontologies/tcm_v38/ontology` embeds a
legacy version token (`v38`) that does not match the actual release (v4.5). Two
clean options:

- **Option A (minimal change, recommended for now):** keep the IRI as-is for this
  submission; the `versionIRI` (`tcm_v45/4.5.0`) already disambiguates the release.
  Cite the version IRI in the paper.
- **Option B (cleaner long-term):** mint a persistent PURL, e.g.
  `https://purl.obolibrary.org/obo/tcso.owl`, and update the base IRI in a future
  v4.6. This requires re-running the writeback script (`step12`) with the new IRI
  and re-validating. **Do this only if you plan ongoing releases** — for the
  current *Scientific Data* submission Option A is sufficient.

---

## 5. Post-submission

- Record the BioPortal ontology ID (`TCM-SO`) and its public URL in the manuscript
  §3.7 (Availability).
- Add the BioPortal link next to the GitHub/Zenodo DOI in the README "How to cite"
  section.
- Keep the **GitHub repo as the canonical source of truth**; re-submit to BioPortal
  whenever a new ontology version is released.

---

*Prepared 2026-07-31. Mirrors the workflow used for HPO, SNOMED CT and ICD-11
cross-references already embedded in the ontology.*
