#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M1 - Quantitative application case: lexicon-based normalization of real-world TCM
clinical free text to TCM-SO (repository-runnable version, 2026-10-08).

Reproduces every number reported in the manuscript (Results, "Application:
normalization of real-world TCM clinical text"; Supplementary Material S9):

  - 444 of 1,758 TCM-SO symptom classes attested (25.3%)
  - conservative estimate (canonical label length >= 3): 236 (13.4%)
  - 460,692 normalized mention instances. Counting unit: one count per distinct
    (lexicon term, record) co-occurrence - a term contributes at most one
    mention per record irrespective of in-record repetitions, and synonym
    strings that map to the same canonical class are counted separately.
  - 43,180/43,180 records with >= 1 mention (100.0%), median 10 distinct
    symptoms per record (IQR 8-13, range 1-27, mean 10.6)

Inputs
------
  documentation/normalization_lexicon.csv  (lexicon_term, canonical_label;
      2,043 distinct terms dumped from the translation master table v4.2)
  TCM-SD corpus zip containing to_LJW/train.json (JSONL). The corpus
      (Ren et al., CCL 2022, CC BY-NC-SA 4.0, academic use) is NOT
      redistributed here; download: https://tianchi.aliyun.com/dataset/139034

Usage
-----
  python scripts/m1_normalization.py path/to/TCM_SD_with_knowledge.zip

Writes clinical_normalization_results.csv to the current directory.
The original analysis run parsed the translation master table directly; the
lexicon CSV round-trip is asserted equal at startup.
"""
import os, sys, json, zipfile, csv, math

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEXICON = os.path.join(HERE, "documentation", "normalization_lexicon.csv")


def load_lexicon(path):
    lex = {}
    with open(path, encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            lex.setdefault(row["lexicon_term"], set()).add(row["canonical_label"])
    return lex


def main():
    if len(sys.argv) < 2:
        sys.exit("usage: python scripts/m1_normalization.py <TCM_SD_with_knowledge.zip>")
    zp = sys.argv[1]

    syn2canon = load_lexicon(LEXICON)
    N_TERMS = len(syn2canon)
    N_SYM = len({c for cs in syn2canon.values() for c in cs})
    print(f"Lexicon terms: {N_TERMS}  (canonical classes covered: {N_SYM})")

    texts = []
    with zipfile.ZipFile(zp) as zf:
        raw = zf.read("to_LJW/train.json").decode("utf-8")
    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        parts = []
        for k in ("chief_complaint", "description", "detection"):
            v = obj.get(k)
            if isinstance(v, str):
                parts.append(v)
        texts.append(" ".join(parts))
    N_REC = len(texts)
    print(f"Corpus records: {N_REC}")

    all_syns = sorted(syn2canon.keys(), key=len, reverse=True)
    distinct_found = set()
    total_instances = 0
    records_with_mention = 0
    syms_per_record = []

    for idx, txt in enumerate(texts):
        found_here = set()
        for s in all_syns:
            if s and s in txt:
                total_instances += 1
                for canon in syn2canon[s]:
                    found_here.add(canon)
                    distinct_found.add(canon)
        if found_here:
            records_with_mention += 1
        syms_per_record.append(len(found_here))
        if idx % 5000 == 0:
            print(f"  processed {idx}/{N_REC}")

    coverage = len(distinct_found) / N_SYM
    detect_rate = records_with_mention / N_REC
    distinct_found_c = {c for c in distinct_found if len(c) >= 3}
    coverage_c = len(distinct_found_c) / N_SYM

    def wilson(p, n, z=1.96):
        denom = 1 + z * z / n
        center = (p + z * z / (2 * n)) / denom
        half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
        return max(0, center - half), min(1, center + half)

    lo, hi = wilson(detect_rate, N_REC)
    sp = sorted(syms_per_record)
    median_load = sp[N_REC // 2]

    print(f"Distinct classes attested : {len(distinct_found)} ({coverage*100:.1f}% of {N_SYM})")
    print(f"  conservative (len>=3)   : {len(distinct_found_c)} ({coverage_c*100:.1f}%)")
    print(f"Total mention instances   : {total_instances}")
    print(f"Records with >=1 mention  : {records_with_mention} ({detect_rate*100:.1f}%)  Wilson95 [{lo*100:.2f}, {hi*100:.2f}]")
    print(f"Median symptoms/record    : {median_load}")

    out = os.path.join(os.getcwd(), "clinical_normalization_results.csv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["corpus_records", N_REC])
        w.writerow(["tcm_so_symptom_classes", N_SYM])
        w.writerow(["distinct_symptoms_attested", len(distinct_found)])
        w.writerow(["coverage_pct", f"{coverage*100:.1f}"])
        w.writerow(["coverage_conservative_pct", f"{coverage_c*100:.1f}"])
        w.writerow(["total_normalized_mention_instances", total_instances])
        w.writerow(["records_with_mention", records_with_mention])
        w.writerow(["detection_rate_pct", f"{detect_rate*100:.1f}"])
        w.writerow(["wilson95_lo_pct", f"{lo*100:.1f}"])
        w.writerow(["wilson95_hi_pct", f"{hi*100:.1f}"])
        w.writerow(["median_symptoms_per_record", median_load])
    print("Wrote", out)


if __name__ == "__main__":
    main()
