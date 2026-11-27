#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Composite-symptom definability outlook (Discussion, TCM-SO v4.10 submission).

Quantifies the expansion prospect of the logical-definition layer
(manuscript Discussion, "Principal findings"):

  1. Strict label decomposition over the 1,758 canonical Chinese labels:
     a label is directly definable when it fully segments into two or more
     other inventory labels (conjunctive pattern) or matches the pilot's
     frequency pattern (suffix 频作/频发/阵发/阵作/时作 with the base in the
     inventory). Result: 7 classes - the 5 frequency pilots, the conjunction
     pilot 恶寒发热, and one further frequency form (矢气频作).

  2. Modifier-annotation coverage: classes carrying at least one free-text
     modifier annotation (frequencyText / severityText / triggerText /
     reliefText). Result: 1,749 of 1,758 (99.5%). These are free-text values;
     mapping them onto a controlled modifier vocabulary (cf. FrequentAttack)
     is the curation step that would unlock modifier-pattern definitions at
     the scale reported in the Discussion.

Input : TCM症状本体_英文翻译总表_v4.2.xlsx (translation master table; local
        analysis copy - the same content is distributed in the released OWL
        as labels and annotation properties).
Output: printed counts only.
"""
import os, re, sys
import openpyxl

TT = r"D:\2026年\症状本体\TCM症状本体_英文翻译总表_v4.2.xlsx"

wb = openpyxl.load_workbook(TT, read_only=True, data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
wb.close()
h = rows[0]
idx = {c: i for i, c in enumerate(h)}
labels = [str(r[idx["中文标签"]]).strip() for r in rows[1:] if r[idx["中文标签"]] not in (None, "")]
vocab = set(labels)
print("canonical labels:", len(vocab))


def segs(l):
    n = len(l)
    dp = [[] for _ in range(n + 1)]
    dp[0] = [()]
    for i in range(1, n + 1):
        for j in range(i):
            if l[j:i] in vocab and dp[j]:
                for pre in dp[j]:
                    dp[i].append(pre + (l[j:i],))
    return dp[n]


setA = set(l for l in vocab if re.search(r"(频作|频发|阵发|阵作|时作)$", l))
setB = set(l for l in vocab if any(len(p) >= 2 for p in segs(l)))
union_strict = setA | setB
print("strict definable (conjunctive + frequency pattern):", len(union_strict))
print("  ", sorted(union_strict))

MOD_COLS = ["frequencyText", "severityText", "triggerText", "reliefText"]
holders = set()
for r in rows[1:]:
    lab = r[idx["中文标签"]]
    if lab in (None, ""):
        continue
    for m in MOD_COLS:
        v = r[idx[m]]
        if v not in (None, "") and str(v).strip():
            holders.add(str(lab).strip())
            break
print("classes with >=1 free-text modifier annotation:", len(holders),
      "(%.1f%% of %d)" % (100 * len(holders) / len(vocab), len(vocab)))
