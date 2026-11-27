#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
m6_assertion_audit.py — corpus-wide assertion-status (negation) audit for the
TCM-SO normalization pipeline.

A mention is marked NEGATED when one of the markers 无 / 未 / 不 / 否认 occurs
within four characters before the matched lexicon term (punctuation stripped),
following NegEx (Chapman et al., J Biomed Inform 2001).

Inputs
------
  normalization_lexicon.csv   (lexicon_term, canonical_label)
  TCM-SD train.json           (JSONL; fields chief_complaint / description / detection)

Outputs
-------
  assertion_audit_results.json
    records, total_mentions, negated_mentions, negation_rate_pct,
    classes_any, classes_affirmed, classes_only_negated,
    top_negated_terms, per-term counts for the template-artifact term 瘿瘤.

Adjust LEXICON / TRAIN below to your local paths.
"""
import csv, json, os, sys
from collections import Counter, defaultdict

LEXICON = os.environ.get("TCMSO_LEXICON", "documentation/normalization_lexicon.csv")
TRAIN = os.environ.get("TCMSD_TRAIN", "train.json")
OUT = os.environ.get("ASSERTION_OUT", "assertion_audit_results.json")

NEG_MARKERS = ("无", "未", "不", "否认")

def is_negated(txt, pos):
    pre = txt[max(0, pos - 4):pos]
    pre = pre.replace("，", "").replace("、", "").replace("；", "").replace("。", "")
    return any(m in pre for m in NEG_MARKERS)

def main():
    syn2canon = defaultdict(set)
    with open(LEXICON, encoding="utf-8-sig") as f:
        for r in csv.DictReader(f):
            syn2canon[r["lexicon_term"].strip()].add(r["canonical_label"].strip())
    terms = [t for t in syn2canon if t]

    total = neg = n_rec = 0
    class_any, class_affirmed = set(), set()
    term_neg, term_tot = Counter(), Counter()

    with open(TRAIN, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            obj = json.loads(line)
            txt = " ".join(obj.get(k) or "" for k in
                           ("chief_complaint", "description", "detection"))
            n_rec += 1
            hit_terms = [t for t in terms if t in txt]
            for t in hit_terms:
                negated = is_negated(txt, txt.find(t))
                total += 1
                term_tot[t] += 1
                for c in syn2canon[t]:
                    class_any.add(c)
                    if not negated:
                        class_affirmed.add(c)
                if negated:
                    neg += 1
                    term_neg[t] += 1
            if n_rec % 10000 == 0:
                print(f"  {n_rec} records...", flush=True)

    res = {
        "records": n_rec,
        "total_mentions": total,
        "negated_mentions": neg,
        "negation_rate_pct": round(neg / total * 100, 1),
        "classes_any": len(class_any),
        "classes_affirmed": len(class_affirmed),
        "classes_only_negated": sorted(class_any - class_affirmed),
        "top_negated_terms": [(t, term_neg[t], term_tot[t],
                               round(term_neg[t] / term_tot[t] * 100, 1))
                              for t, _ in term_neg.most_common(15)],
        "luoliu": {"term": "瘿瘤", "neg": term_neg.get("瘿瘤", 0),
                   "tot": term_tot.get("瘿瘤", 0)},
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=1)
    print(json.dumps(res, ensure_ascii=False, indent=1))

if __name__ == "__main__":
    main()
