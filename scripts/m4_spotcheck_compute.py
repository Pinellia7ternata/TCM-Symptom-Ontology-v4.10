#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
m4_spotcheck_compute.py — turn the filled double-blind spot-check workbook into a
normalization-precision estimate.

Usage:
    python m4_spotcheck_compute.py [path_to_xlsx]

Reads sheets "标注者A_抽检表" and "标注者B_抽检表", pairs rows by 样本号, and reports:
  * per-rater correct rate (fraction judged 1=正确)
  * observed inter-rater agreement
  * Cohen's kappa (binary 0/1)
  * Gwet's AC1 (prevalence-robust)
  * consensus precision (both raters judge correct) with Wilson 95% CI
  * per-rater precision with Wilson 95% CI

Requires the two rater sheets' "判定(1=正确 / 0=错误)" column filled (1/0).
Blank / non-(0,1) cells are reported and skipped from the relevant denominator.
"""
import os, sys, math
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
XLSX = os.path.join(HERE, "clinical_normalization_spotcheck_200.xlsx")
if len(sys.argv) > 1:
    XLSX = sys.argv[1]

DEC_COL = 7   # 判定(1=正确 / 0=错误) is the 7th column in the rater sheets

def load_rater(ws):
    rows = {}
    for r in range(2, ws.max_row + 1):
        sid = ws.cell(row=r, column=1).value
        if sid is None:
            continue
        try:
            sid = int(sid)
        except Exception:
            continue
        val = ws.cell(row=r, column=DEC_COL).value
        rows[sid] = val
    return rows

def wilson(p, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    denom = 1 + z * z / n
    center = (p + z * z / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / denom
    return max(0, center - half), min(1, center + half)

def cohen_kappa(a, b):
    # a,b lists of 0/1
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(1 for x, y in zip(a, b) if x == y) / n
    p1 = sum(a) / n
    p2 = sum(b) / n
    pe = p1 * p2 + (1 - p1) * (1 - p2)
    if pe == 1:
        return 1.0
    return (po - pe) / (1 - pe)

def gwet_ac1(a, b):
    n = len(a)
    if n == 0:
        return float("nan")
    # binary Gwet AC1
    p = sum(1 for x, y in zip(a, b) if x == y) / n
    # marginals
    pa = sum(a) / n
    pb = sum(b) / n
    # AC1 uses observed agreement minus chance where chance = sum over categories of pi^2
    # for binary with raters' marginal proportions:
    pe = pa * pb + (1 - pa) * (1 - pb)
    # Gwet's AC1 chance = sum_i ( (pa_i+pb_i)/2 )^2
    pe_g = ((pa + pb) / 2) ** 2 + ((1 - pa + 1 - pb) / 2) ** 2
    if pe_g == 1:
        return 1.0
    return (p - pe_g) / (1 - pe_g)

wb = openpyxl.load_workbook(XLSX, data_only=True)
wsA = wb["标注者A_抽检表"]
wsB = wb["标注者B_抽检表"]
ra = load_rater(wsA)
rb = load_rater(wsB)

common = sorted(set(ra) & set(rb))
if not common:
    print("No paired sample_ids found. Have both raters filled their sheets?")
    sys.exit(1)

pairs = [(ra[s], rb[s]) for s in common]
filled = [(x, y) for x, y in pairs if x in (0, 1) and y in (0, 1)]
if not filled:
    print(f"Found {len(common)} paired rows but none have both raters' 判定 filled (1/0). "
          "Please fill the 判定 column before computing.")
    sys.exit(0)

a = [x for x, y in filled]
b = [y for x, y in filled]
n = len(filled)

ra_correct = sum(1 for x in a if x == 1)
rb_correct = sum(1 for y in b if y == 1)
both_correct = sum(1 for x, y in filled if x == 1 and y == 1)
agree = sum(1 for x, y in filled if x == y)

print("=" * 60)
print(f"TCM-SO normalization spot-check (double-blind, 2 raters)")
print(f"Paired & fully-filled rows: {n} / {len(common)} paired")
print("-" * 60)
print(f"Rater A correct rate : {ra_correct}/{n} = {ra_correct/n*100:.1f}%   "
      f"Wilson95% [{wilson(ra_correct/n,n)[0]*100:.1f}, {wilson(ra_correct/n,n)[1]*100:.1f}]")
print(f"Rater B correct rate : {rb_correct}/{n} = {rb_correct/n*100:.1f}%   "
      f"Wilson95% [{wilson(rb_correct/n,n)[0]*100:.1f}, {wilson(rb_correct/n,n)[1]*100:.1f}]")
print(f"Consensus correct (both=1): {both_correct}/{n} = {both_correct/n*100:.1f}%   "
      f"Wilson95% [{wilson(both_correct/n,n)[0]*100:.1f}, {wilson(both_correct/n,n)[1]*100:.1f}]")
print(f"Observed agreement  : {agree}/{n} = {agree/n*100:.1f}%")
print(f"Cohen's kappa       : {cohen_kappa(a,b):.3f}")
print(f"Gwet's AC1          : {gwet_ac1(a,b):.3f}")
print("=" * 60)
print("Recommended manuscript figure: consensus-correct precision "
      f"= {both_correct/n*100:.1f}% (95% CI {wilson(both_correct/n,n)[0]*100:.1f}–{wilson(both_correct/n,n)[1]*100:.1f}), "
      f"n = {n}, double-blind 2 raters, Cohen's κ = {cohen_kappa(a,b):.2f}.")
