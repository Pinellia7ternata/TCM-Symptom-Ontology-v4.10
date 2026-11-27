# -*- coding: utf-8 -*-
"""Non-destructively add a `curation_status` column to the delivered SSSOM files,
marking the 75 double-blind no-consensus mappings as `under_review`.
Backs up each SSSOM before editing. Matching key: (subject_label, object_id)."""
import csv, shutil, os, re

REPO = r"D:\2026年\症状本体\repository\mappings"
REVIEW = r"D:\2026年\症状本体\文章\Database_submission\mapping_review_list.csv"
TERM_FILE = {"HPO": "TCM-SO-HPO.sssom.tsv",
             "SNOMEDCT": "TCM-SO-SNOMEDCT.sssom.tsv",
             "ICD11": "TCM-SO-ICD11.sssom.tsv"}

def norm(s): return re.sub(r"\s+", " ", str(s).strip())

# load flagged keys per terminology
flag = {k: set() for k in TERM_FILE}
with open(REVIEW, encoding="utf-8") as fh:
    for r in csv.DictReader(fh):
        flag[r["terminology"]].add((norm(r["sx_en"]), r["obj_id"].strip()))

total_expected = sum(len(v) for v in flag.values())
print("flagged keys to mark:", total_expected, dict((k, len(v)) for k, v in flag.items()))

BACKUP = False
matched_total = 0
report = {}
for term, fn in TERM_FILE.items():
    p = os.path.join(REPO, fn)
    bak = p + ".bak_20260917"
    if not os.path.exists(bak):
        shutil.copy2(p, bak)
        print("backup ->", bak)
    lines = [l.rstrip("\n") for l in open(p, encoding="utf-8")]
    # split metadata (#) lines from data lines
    meta = [l for l in lines if l.startswith("#")]
    data = [l for l in lines if not l.startswith("#")]
    hdr = data[0].split("\t")
    if "curation_status" in hdr:
        raise SystemExit(f"{fn} already has curation_status column")
    hdr.append("curation_status")
    out = []
    out.append("\t".join(hdr))
    n_match = 0
    keys = flag[term]
    for row in data[1:]:
        cols = row.split("\t")
        # pad if short
        while len(cols) < len(hdr) - 1:
            cols.append("")
        subj = norm(cols[1])      # subject_label is col index 1
        obj = cols[3].strip()     # object_id is col index 3
        if (subj, obj) in keys:
            cols.append("under_review")
            n_match += 1
        else:
            cols.append("")
        out.append("\t".join(cols))
    with open(p, "w", encoding="utf-8", newline="") as fh:
        for l in meta:
            fh.write(l + "\n")
        fh.write("\n".join(out) + "\n")
    matched_total += n_match
    report[term] = (len(keys), n_match)
    print(f"  {fn}: flagged={len(keys)} matched={n_match}")

print("\nTOTAL matched:", matched_total, "(expected", total_expected, ")")
if matched_total != total_expected:
    print("  WARNING: some flagged keys did NOT match a SSSOM row — check ID formats!")
else:
    print("  OK: all flagged mappings annotated with curation_status=under_review.")
print("per-file:", report)
