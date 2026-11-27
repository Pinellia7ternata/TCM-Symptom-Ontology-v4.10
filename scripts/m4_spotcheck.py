#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
M4 — Expand the normalization spot-check from the original 40-mention single-annotator
pilot to a 200-mention DOUBLE-BLIND spot check by TWO independent raters.

Design notes
------------
* The published normalization metric `total_normalized_mention_instances = 460,692` counts
  (record x synonym) *presence* pairs: for each clinical record, every TCM-SO synonym that
  literally occurs anywhere in the concatenated free text is counted once (multiple in-text
  occurrences of the same synonym within one record are not re-counted). This script reproduces
  EXACTLY that counting population and draws an UNBIASED simple random sample of 200 such
  (record, synonym) presence pairs via reservoir sampling (Algorithm R, fixed seed), so the
  spot-check directly estimates the precision of the very instances that compose the headline
  figure.
* Each sampled mention records: 1-based source record id, a +/-20 char context window, the
  matched synonym, the canonical TCM-SO class it maps to (first/deterministic canonical when a
  synonym is ambiguous), and the synonym length (a transparency aid for raters).
* Two annotation sheets (Rater A / Rater B) present the same 200 pairs in two independently
  shuffled orders, paired by a stable `sample_id`, so the two raters are blinded to each other.
* `m4_spotcheck_compute.py` turns the filled workbook into a precision estimate with Wilson 95%
  CI, per-rater correct rates, and inter-rater agreement (observed agreement, Cohen's kappa,
  Gwet AC1).

Inputs  (identical to m1_normalization.py)
-------
  TCM症状本体_英文翻译总表_v4.2.xlsx   (col 中文标签 = canonical; col 同义词 = synonyms)
  TCM-SD中医领域辨证数据集/TCM_SD_with_knowledge.zip  (to_LJW/train.json JSONL)

Outputs
-------
  clinical_normalization_spotcheck_200.csv   (machine-readable sample, no rater columns; for repo + S9)
  clinical_normalization_spotcheck_200.xlsx  (README + 样本分布 + 标注者A + 标注者B, rater columns blank)
"""
import os, json, zipfile, csv, math, random

BASE = r"D:\2026年\症状本体"
OUT = os.path.join(BASE, "文章", "Database_submission")
K = 200                      # target sample size (>=200 per reviewer requirement)
SEED = 20260920              # fixed for full reproducibility
WINDOW = 20                  # context half-width (chars)

random.seed(SEED)

# ---------- 1. TCM-SO vocabulary (canonical + synonyms) ----------
tt = os.path.join(BASE, "TCM症状本体_英文翻译总表_v4.2.xlsx")
import openpyxl
wb = openpyxl.load_workbook(tt, read_only=True, data_only=True)
ws = wb.active
rows = list(ws.iter_rows(values_only=True))
h = rows[0]
i_label = h.index("中文标签")
i_syn = h.index("同义词")
syn2canon = {}               # synonym string -> ordered list of canonical labels
for r in rows[1:]:
    lab = r[i_label]
    if lab in (None, ""):
        continue
    lab = str(lab).strip()
    syns = [lab]
    s = r[i_syn]
    if s not in (None, ""):
        for part in str(s).replace("、", ",").replace("/", ",").split(","):
            part = part.strip()
            if part:
                syns.append(part)
    for syn in syns:
        syn2canon.setdefault(syn, []).append(lab)
wb.close()
N_SYM = len({lab for labs in syn2canon.values() for lab in labs})
print(f"TCM-SO canonical symptom classes: {N_SYM}; distinct synonym strings: {len(syn2canon)}")

# synonyms sorted by length desc (longer entries win first when scanning, as in m1)
all_syns = sorted(syn2canon.keys(), key=len, reverse=True)

# ---------- 2. Corpus ----------
zp = os.path.join(BASE, "TCM-SD中医领域辨证数据集", "TCM_SD_with_knowledge.zip")
records = []
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
    records.append(" ".join(parts))
N_REC = len(records)
print(f"Corpus records: {N_REC}")

# ---------- 3. Reservoir sample of (record, synonym) presence pairs ----------
reservoir = []     # list of dicts
n_occ = 0          # global occurrence counter (= matches total_instances population)
total_instances = 0
distinct_found = set()

for idx, txt in enumerate(records):
    for s in all_syns:
        if s and s in txt:
            total_instances += 1
            n_occ += 1
            for canon in syn2canon[s]:
                distinct_found.add(canon)
            # reservoir candidate: one (record, synonym) presence pair
            pos = txt.find(s)
            snippet = txt[max(0, pos - WINDOW): pos + len(s) + WINDOW].replace("\n", " ")
            item = {
                "rec_idx": idx + 1,                 # 1-based source record id
                "synonym": s,
                "canonical": syn2canon[s][0],
                "synonym_len": len(s),
                "snippet": snippet,
            }
            if len(reservoir) < K:
                reservoir.append(item)
            else:
                j = random.randint(0, n_occ - 1)
                if j < K:
                    reservoir[j] = item
    if idx % 5000 == 0:
        print(f"  scanned {idx}/{N_REC}  occurrences={n_occ}  reservoir={len(reservoir)}")

assert len(reservoir) == K, f"reservoir size {len(reservoir)} != {K}"
coverage = len(distinct_found) / N_SYM
print(f"\nPopulation (recomputed for consistency): total_instances={total_instances:,} "
      f"distinct_classes={len(distinct_found)} ({coverage*100:.1f}%)")
print(f"Reservoir sampled {K} mention instances (seed={SEED}).")

# stable sample_id 1..K (assigned now, before shuffling rater sheets)
reservoir.sort(key=lambda d: d["rec_idx"])
for i, it in enumerate(reservoir, start=1):
    it["sample_id"] = i

# ---------- 4. Distribution summary ----------
def bucket(L):
    if L <= 2:
        return "1-2 chars"
    if L == 3:
        return "3 chars"
    return "4+ chars"
from collections import Counter
len_buckets = Counter(bucket(it["synonym_len"]) for it in reservoir)
canon_dist = Counter(it["canonical"] for it in reservoir)
top_canon = canon_dist.most_common(15)
distinct_canon = len(canon_dist)
print("Length buckets:", dict(len_buckets))
print("Distinct canonical classes in sample:", distinct_canon)
print("Top canonical:", top_canon)

# ---------- 5. Machine-readable CSV (no rater columns) ----------
csv_path = os.path.join(OUT, "clinical_normalization_spotcheck_200.csv")
with open(csv_path, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["sample_id", "source_record", "synonym", "canonical_class",
                "synonym_len", "context_window"])
    for it in sorted(reservoir, key=lambda d: d["sample_id"]):
        w.writerow([it["sample_id"], it["rec_idx"], it["synonym"], it["canonical"],
                    it["synonym_len"], it["snippet"]])
print(f"Wrote {csv_path}")

# ---------- 6. Annotation XLSX (double-blind) ----------
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

RO = PatternFill("solid", fgColor="DDEBF7")   # read-only (light blue)
FILL = PatternFill("solid", fgColor="FFF2CC")  # rater-fillable (light yellow)
HDR = PatternFill("solid", fgColor="4472C4")
HDRF = Font(bold=True, color="FFFFFF")
THIN = Side(style="thin", color="BFBFBF")
BORD = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
WRAP = Alignment(wrap_text=True, vertical="top")
CEN = Alignment(horizontal="center", vertical="center")

RATER_HEADERS = ["样本号", "来源记录号", "上下文片段", "命中词条",
                 "映射规范类", "词条长度",
                 "判定(1=正确 / 0=错误)", "置信度(1-5)", "误判原因 / 备注"]
RO_COLS = 6       # first 6 columns read-only

def style_header(ws, ncol):
    for c in range(1, ncol + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill = HDR; cell.font = HDRF; cell.alignment = CEN; cell.border = BORD

def write_rater_sheet(ws, items, shuffle_seed):
    rng = random.Random(shuffle_seed)
    order = list(items)
    rng.shuffle(order)
    ws.append(RATER_HEADERS)
    style_header(ws, len(RATER_HEADERS))
    for row_i, it in enumerate(order, start=2):
        vals = [it["sample_id"], it["rec_idx"], it["snippet"], it["synonym"],
                it["canonical"], it["synonym_len"], None, None, None]
        for c, v in enumerate(vals, start=1):
            cell = ws.cell(row=row_i, column=c, value=v)
            cell.border = BORD
            if c <= RO_COLS:
                cell.fill = RO
                cell.alignment = WRAP if c == 3 else CEN
            else:
                cell.fill = FILL
                cell.alignment = CEN
    # column widths
    widths = [8, 11, 46, 12, 16, 9, 16, 11, 26]
    for i, wdt in enumerate(widths, start=1):
        ws.column_dimensions[get_column_letter(i)].width = wdt
    ws.freeze_panes = "A2"

wbk = openpyxl.Workbook()

# --- README sheet ---
ws0 = wbk.active
ws0.title = "说明_README"
readme = [
    ("TCM-SO 归一化抽检表（200 条 · 双盲 · 2 名标注者）", True),
    ("", False),
    ("目的", True),
    ("对稿件 Results “Application: normalization of real-world TCM clinical text” 中报道的"
     "归一化精确率进行更严格的双人双盲抽检，以替代原 40 条单标注者试点，回应审稿人对样本量"
     "与单标注者设计的质疑。", False),
    ("", False),
    ("抽样方法（与已发表口径严格一致）", True),
    (f"· 语料：TCM-SD 43,180 条门诊病历（主诉 / 病情描述 / 四诊摘要拼接的自由文本）。", False),
    (f"· 词表：TCM-SO 1,758 个规范中文症状标签 + 中文同义词，作为归一化词典。", False),
    (f"· 计数口径：已发表 total_normalized_mention_instances = 460,692 按“（记录 × 同义词）"
     f"存在性”对计数——同一记录内某同义词出现多次只计 1 次。本抽样复述该总体，并从中"
     f"以蓄水池抽样（reservoir sampling，seed={SEED}）无偏抽取 200 条（记录, 同义词）存在性配对。", False),
    (f"· 因此本抽检直接估计构成头条数字的同一批实例的精确率，抽样对 460,692 总体中的每条实例等概率。", False),
    ("", False),
    ("标注任务（两位标注者独立、互盲）", True),
    ("· 对每一行：阅读“上下文片段”，判断“命中词条”在该语境下是否确实指向“映射规范类”所代表的"
     "TCM-SO 症状概念。", False),
    ("· 判定列填 1 = 正确（该词条在语境中确为该规范症状的正常化提及）；0 = 错误（误匹配，如同义词"
     "被嵌入其他词、或语境义不符）。", False),
    ("· 置信度 1–5（5 最高）；如有误判请在“误判原因 / 备注”说明。", False),
    ("· 标注者 A 与 B 使用各自工作表，行序独立打乱，但“样本号”跨表配对，便于双盲一致性计算。", False),
    ("", False),
    ("注意事项", True),
    ("· 短词条（1–2 字）更易产生假阳性，请特别留意语境。样本长度分布见“样本分布”工作表。", False),
    ("· 上下文窗口为命中词条两侧各 20 字；必要时可回查 TCM-SD 源记录（source_record 为 train.json 行号）。", False),
    ("", False),
    ("计算", True),
    ("· 两位标注者回填后，运行 m4_spotcheck_compute.py 读取本工作簿，输出：各标注者正确率、"
     "观察一致率、Cohen's κ、Gwet AC1，以及基于双人一致判定的总体精确率 + Wilson 95% CI。", False),
]
for text, bold in readme:
    ws0.append([text])
    if bold:
        ws0.cell(row=ws0.max_row, column=1).font = Font(bold=True, size=12)
ws0.column_dimensions["A"].width = 110

# --- distribution sheet ---
wsd = wbk.create_sheet("样本分布")
wsd.append(["指标", "值"])
style_header(wsd, 2)
rows_dist = [
    ("抽样样本量 (K)", K),
    ("抽样方法", "蓄水池随机抽样 (seed=%d)" % SEED),
    ("总体规模 (已发表 total_instances)", total_instances),
    ("样本中不同规范类数", distinct_canon),
    ("— 词条长度 1–2 字", len_buckets.get("1-2 chars", 0)),
    ("— 词条长度 3 字", len_buckets.get("3 chars", 0)),
    ("— 词条长度 4+ 字", len_buckets.get("4+ chars", 0)),
]
for k_, v_ in rows_dist:
    wsd.append([k_, v_])
wsd.append([])
wsd.append(["样本中频次最高的 15 个规范类", "出现次数"])
style_header(wsd, 2)  # re-style header row (now offset)
for cname, cnt in top_canon:
    wsd.append([cname, cnt])
wsd.column_dimensions["A"].width = 42
wsd.column_dimensions["B"].width = 16

# --- rater sheets ---
wsA = wbk.create_sheet("标注者A_抽检表")
wsB = wbk.create_sheet("标注者B_抽检表")
write_rater_sheet(wsA, reservoir, shuffle_seed=20260921)
write_rater_sheet(wsB, reservoir, shuffle_seed=20260922)

xlsx_path = os.path.join(OUT, "clinical_normalization_spotcheck_200.xlsx")
wbk.save(xlsx_path)
print(f"Wrote {xlsx_path}")
print("DONE")
