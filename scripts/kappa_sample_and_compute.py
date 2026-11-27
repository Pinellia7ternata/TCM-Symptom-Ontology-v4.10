# -*- coding: utf-8 -*-
"""
M2 — Cross-standard mapping inter-annotator agreement (kappa) sampling & computation.

Part A: build the authoritative sampling frame from the DELIVERED SSSOM mappings (2,329),
        attach the human-confirmation confidence tier (High/Medium) where available,
        mark the remainder as 'inherited' (present in OWL/SSSOM but not in the
        human-confirmation candidate tables — i.e. inherited from T/CACM 1641-2025),
        then draw a STRATIFIED RANDOM SAMPLE (terminology x mapType) and emit a
        double-blind re-annotation sheet for the second/third expert.

Part B: given the filled re-annotation sheet, compute Cohen's kappa (pairwise) and
        Fleiss' kappa (>=3 raters) with 95% CI (analytic + bootstrap), overall and
        per terminology, and emit a manuscript-ready results table.

No third-party deps beyond openpyxl (for xlsx) + stdlib.
"""
import os, re, csv, random, math
import openpyxl

BASE = r"D:\2026年\症状本体"
REPO = os.path.join(BASE, "repository", "mappings")
SUB  = os.path.join(BASE, "文章", "Database_submission")
SEED = 20260917

TERM_FILES = {
    "HPO":      dict(sssom="TCM-SO-HPO.sssom.tsv",
                     xlsx=os.path.join(BASE, "HPO映射候选_人工确认表_已填Y.xlsx"),
                     code_col="HPO_ID(候选)", en_col="症状英文标签",
                     conf_col="置信度", maptype_col="建议mapType"),
    "SNOMEDCT": dict(sssom="TCM-SO-SNOMEDCT.sssom.tsv",
                     xlsx=os.path.join(BASE, "SNOMEDCT映射候选_人工确认表_已填Y.xlsx"),
                     code_col="SNOMED_ID(候选)", en_col="症状英文标签",
                     conf_col="置信度", maptype_col="建议mapType"),
    "ICD11":    dict(sssom="TCM-SO-ICD11.sssom.tsv",
                     xlsx=os.path.join(BASE, "ICD11映射候选_人工确认表_已填Y.xlsx"),
                     code_col="ICD11_ID(候选)", en_col="症状英文标签",
                     conf_col="置信度", maptype_col="建议mapType"),
}

def norm_label(s):
    if s is None: return ""
    return re.sub(r"\s+", " ", str(s).strip().lower())

def norm_code(s):
    if s is None: return ""
    s = str(s).strip()
    s = re.sub(r"^https?://[^ ]*?id/", "", s)
    s = re.sub(r"^(HP|SNOMEDCT|ICD11)[:_]", "", s, flags=re.I)
    return re.sub(r"[^0-9A-Za-z]", "", s)

# ----------------------------------------------------------------------------
# Part A — build frame + stratified sample
# ----------------------------------------------------------------------------
def load_xlsx_confidence(cfg):
    """Return dict: norm_label -> (confidence, norm_code) for confirmed (Y) rows."""
    wb = openpyxl.load_workbook(cfg["xlsx"], read_only=True, data_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))
    wb.close()
    hdr = rows[0]
    ci = {str(h): i for i, h in enumerate(hdr) if h is not None}
    en_i   = ci[cfg["en_col"]]
    conf_i = ci[cfg["conf_col"]]
    code_i = ci[cfg["code_col"]]
    out = {}
    for r in rows[1:]:
        if r[0] != "Y":            # only human-confirmed rows carry a confidence tier
            continue
        lab = norm_label(r[en_i])
        if not lab:
            continue
        out[lab] = (str(r[conf_i]).strip(), norm_code(r[code_i]))
    return out

def build_frame():
    frame = []
    for term, cfg in TERM_FILES.items():
        xconf = load_xlsx_confidence(cfg)
        p = os.path.join(REPO, cfg["sssom"])
        with open(p, encoding="utf-8") as fh:
            lines = [l.rstrip("\n") for l in fh if l.strip() and not l.startswith("#")]
        hdr = lines[0].split("\t")
        hi = {h: i for i, h in enumerate(hdr)}
        for l in lines[1:]:
            c = l.split("\t")
            sx_en   = c[hi["subject_label"]]
            obj_id  = c[hi["object_id"]]
            pred    = c[hi["predicate_id"]]            # skos:exactMatch / skos:closeMatch
            mtype   = "exact" if "exact" in pred else "close"
            lab = norm_label(sx_en)
            if lab in xconf:
                conf = xconf[lab][0]
            else:
                conf = "inherited"                     # in OWL/SSSOM but not human-confirmed table
            frame.append(dict(terminology=term, sx_en=sx_en, obj_id=obj_id,
                              mapType=mtype, confidence=conf))
    return frame

def stratified_sample(frame, n_total=384, floor=40, seed=SEED):
    rng = random.Random(seed)
    # strata = (terminology, mapType)
    strata = {}
    for row in frame:
        k = (row["terminology"], row["mapType"])
        strata.setdefault(k, []).append(row)
    # proportional allocation with a per-stratum floor (capped at stratum size)
    N = len(frame)
    alloc = {}
    for k, items in strata.items():
        prop = max(floor, round(n_total * len(items) / N))
        prop = min(prop, len(items))
        alloc[k] = prop
    # if total exceeds n_total substantially, that's fine (floors); report it
    sample = []
    sid = 0
    for k, items in strata.items():
        take = alloc[k]
        for row in rng.sample(items, take):
            sid += 1
            row = dict(row)
            row["sample_id"] = f"S{sid:04d}"
            sample.append(row)
    return sample, alloc, strata

def write_frame_and_sample(frame, sample, alloc):
    fpath = os.path.join(SUB, "kappa_frame_full.csv")
    with open(fpath, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["terminology","sx_en","obj_id","mapType","confidence"])
        for r in frame:
            w.writerow([r["terminology"], r["sx_en"], r["obj_id"], r["mapType"], r["confidence"]])
    # re-annotation sheet (blank rater columns)
    spath = os.path.join(SUB, "kappa_reannotation_sheet.csv")
    with open(spath, "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["sample_id","terminology","sx_en","obj_id","mapType","confidence",
                    "rater1_acceptable","rater1_mapType",
                    "rater2_acceptable","rater2_mapType",
                    "rater3_acceptable","rater3_mapType"])
        for r in sample:
            w.writerow([r["sample_id"], r["terminology"], r["sx_en"], r["obj_id"],
                        r["mapType"], r["confidence"], "", "", "", "", "", ""])
    return fpath, spath

# ----------------------------------------------------------------------------
# Part B — kappa statistics
# ----------------------------------------------------------------------------
def cohen_kappa_table(table):
    """table: list of lists (rater1 rows x rater2 cols), square, counts. Returns (kappa, se)."""
    n = sum(sum(row) for row in table)
    k = len(table)
    po = sum(table[i][i] for i in range(k)) / n
    colsum = [sum(table[r][c] for r in range(k)) for c in range(k)]
    rowsum = [sum(table[r][c] for c in range(k)) for r in range(k)]
    pe = sum(rowsum[i]*colsum[i] for i in range(k)) / (n*n)
    if (1-pe) == 0:
        return (1.0, 0.0)
    kap = (po-pe)/(1-pe)
    # Fleiss (1969) general variance for unweighted kappa (k x k)
    pi = [[table[r][c]/n for c in range(k)] for r in range(k)]
    p_i_dot = [sum(pi[r]) for r in range(k)]
    p_dot_j = [sum(pi[r][c] for r in range(k)) for c in range(k)]
    s = 0.0
    for i in range(k):
        for j in range(k):
            s += pi[i][j]*pi[j][i]*((p_i_dot[i]+p_dot_j[i])*(p_dot_j[j]+p_i_dot[j]))
    var = (pe + pe*pe - s) / (n*(1-pe)**2)
    return (kap, math.sqrt(max(var,0.0)))

def fleiss_kappa(table):
    """table: list of lists, rows=items, cols=category counts per rater. Standard Fleiss."""
    n_raters = sum(table[0])
    N = len(table)
    k = len(table[0])
    cat_marg = [sum(table[i][j] for i in range(N)) for j in range(k)]
    P_bar = 0.0
    for i in range(N):
        tot = sum(table[i])
        if tot == 0: continue
        sum_sq = sum(table[i][j]**2 for j in range(k))
        P_bar += (sum_sq - n_raters) / (n_raters*(n_raters-1))
    P_bar /= N
    p_j = [cat_marg[j]/(N*n_raters) for j in range(k)]
    P_e = sum(p*p for p in p_j)
    if (1-P_e) == 0: return 1.0
    return (P_bar - P_e)/(1 - P_e)

def bootstrap_ci(b1, b2, nboot=2000, seed=SEED):
    rng = random.Random(seed)
    n = len(b1)
    pairs = list(zip(b1, b2))
    kaps = []
    for _ in range(nboot):
        s = [rng.choice(pairs) for _ in range(n)]
        a = [x[0] for x in s]; b = [x[1] for x in s]
        t = _binary_table(a, b)
        kap, _ = cohen_kappa_table(t)
        kaps.append(kap)
    kaps.sort()
    lo = kaps[int(0.025*nboot)]
    hi = kaps[int(0.975*nboot)]
    return lo, hi

def _binary_table(a, b):
    # a,b lists of 0/1 (0=not acceptable,1=acceptable)
    t = [[0,0],[0,0]]
    for x,y in zip(a,b):
        t[x][y]+=1
    return t

def compute_from_file(filled_csv):
    with open(filled_csv, encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    # collect raters present
    raters = []
    for r in rows:
        for rk in ["rater1_acceptable","rater2_acceptable","rater3_acceptable"]:
            if r.get(rk, "").strip():
                if rk not in raters: raters.append(rk)
    def to01(v):
        v = (v or "").strip().lower()
        return 1 if v in ("y","yes","1","accept","acceptable","正确","是") else 0
    results = {}
    # overall pairwise Cohen
    for ri in raters:
        for rj in raters:
            if raters.index(ri) >= raters.index(rj): continue
            a = [to01(r[ri]) for r in rows if r[ri].strip() and r[rj].strip()]
            b = [to01(r[rj]) for r in rows if r[ri].strip() and r[rj].strip()]
            t = _binary_table(a,b)
            kap, se = cohen_kappa_table(t)
            lo, hi = bootstrap_ci(a,b)
            results[f"{ri}__vs__{rj}"] = dict(kappa=round(kap,3), se=round(se,3),
                                             ci=f"[{lo:.3f}, {hi:.3f}]", n=len(a))
    # per terminology
    per_term = {}
    for term in TERM_FILES:
        sub = [r for r in rows if r["terminology"]==term]
        if len(raters)>=2 and sub:
            ri, rj = raters[0], raters[1]
            a = [to01(r[ri]) for r in sub if r[ri].strip() and r[rj].strip()]
            b = [to01(r[rj]) for r in sub if r[ri].strip() and r[rj].strip()]
            if a:
                t=_binary_table(a,b); kap,se=cohen_kappa_table(t); lo,hi=bootstrap_ci(a,b)
                per_term[term]=dict(kappa=round(kap,3),ci=f"[{lo:.3f}, {hi:.3f}]",n=len(a))
    # Fleiss if >=3 raters
    fleiss = None
    if len(raters) >= 3:
        # build item x category(2) table
        tbl=[]
        for r in rows:
            cnt=[0,0]
            ok=False
            for rk in raters:
                if r[rk].strip():
                    cnt[to01(r[rk])]+=1; ok=True
            if ok: tbl.append(cnt)
        if tbl: fleiss = round(fleiss_kappa(tbl),3)
    return results, per_term, fleiss, raters

# ----------------------------------------------------------------------------
def main():
    frame = build_frame()
    n_conf = sum(1 for r in frame if r["confidence"]!="inherited")
    n_inh  = sum(1 for r in frame if r["confidence"]=="inherited")
    print(f"[frame] total delivered mappings = {len(frame)} "
          f"(human-confirmed tiers = {n_conf}, inherited = {n_inh})")
    # confidence distribution
    from collections import Counter
    print("  confidence tiers:", dict(Counter(r["confidence"] for r in frame)))
    print("  mapType:", dict(Counter(r["mapType"] for r in frame)))
    sample, alloc, strata = stratified_sample(frame)
    fpath, spath = write_frame_and_sample(frame, sample, alloc)
    print(f"[sample] total sampled = {len(sample)}; per-stratum alloc = {{")
    for k,v in alloc.items():
        print(f"    {k}: pop={len(strata[k])}, sample={v}")
    print("  }")
    print(f"[write] frame   -> {fpath}")
    print(f"[write] sheet   -> {spath}")
    print("\n--- To compute kappa after experts fill the sheet, run: ---")
    print(f"  results, per_term, fleiss, raters = compute_from_file(r'{spath}')")

if __name__ == "__main__":
    main()
