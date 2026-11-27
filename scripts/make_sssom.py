# -*- coding: utf-8 -*-
"""M4 修复：由三个映射 CSV 生成 SSSOM TSV 映射集（typed predicates for all 2,329 mappings）。
SSSOM: https://github.com/mapping-commons/sssom
谓词 CURIE: skos:exactMatch / skos:closeMatch
subject: TCM-SO:sx_xxx (CURIE, 前缀映射到本体类 IRI)
object: HP:xxxxxxx / SNOMEDCT:xxxxxxxxx / ICD11:xxxx
"""
import csv, os, io, sys
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from datetime import date

BASE = r'D:\2026年\症状本体\repository\mappings'
MAPPING_DATE = '2026-09-17'

CONFIGS = [
    dict(csv='HPO_mapping.csv', out='TCM-SO-HPO.sssom.tsv',
         code_col='hpo_id', term_col='hpo_term',
         obj_prefix='HP', obj_uri='http://purl.obolibrary.org/obo/HP_',
         source='The Human Phenotype Ontology (release 2021)'),
    dict(csv='SNOMEDCT_mapping.csv', out='TCM-SO-SNOMEDCT.sssom.tsv',
         code_col='snomedCT_id', term_col='snomedCT_term',
         obj_prefix='SNOMEDCT', obj_uri='http://snomed.info/id/',
         source='SNOMED CT (International Edition)'),
    dict(csv='ICD11_mapping.csv', out='TCM-SO-ICD11.sssom.tsv',
         code_col='icd11_id', term_col='icd11_term',
         obj_prefix='ICD11', obj_uri='https://icd.who.int/browse11/l-m/en#',
         source='ICD-11 for Mortality and Morbidity Statistics (MMS)'),
]

HEADER = """# mapping_set_id: https://github.com/Pinellia7ternata/TCM-Symptom-Ontology/mappings/{out}
# license: https://creativecommons.org/licenses/by/4.0/
# mapping_provider: https://github.com/Pinellia7ternata/TCM-Symptom-Ontology
# mapping_date: {d}
# creator_id: https://github.com/Pinellia7ternata
# mapping_tool: manual expert curation after lexical/semantic pre-screening
# object_source: {source}
# comment_type
# comment: Subject classes are TCM Symptom Ontology (TCM-SO, release v4.10) symptom classes; predicate and object identify the cross-terminology alignment.
# curie_map:
#   TCM-SO: http://OntoTCM.org.cn/ontologies/tcm_v38/f#
#   HP: http://purl.obolibrary.org/obo/HP_
#   SNOMEDCT: http://snomed.info/id/
#   ICD11: https://icd.who.int/browse11/l-m/en#
subject_id\tsubject_label\tpredicate_id\tobject_id\tobject_label\tmapping_justification
"""

for cfg in CONFIGS:
    rows = list(csv.DictReader(open(os.path.join(BASE, cfg['csv']), encoding='utf-8-sig')))
    n = 0
    with open(os.path.join(BASE, cfg['out']), 'w', encoding='utf-8', newline='') as f:
        f.write(HEADER.format(out=cfg['out'], d=MAPPING_DATE, source=cfg['source']))
        for r in rows:
            code = r[cfg['code_col']].strip()
            if not code:
                continue
            # HPO CSV 代码形如 HP:0034269；SNOMED 为裸 SCTID；ICD11 为裸代码
            if code.upper().startswith('HP:'):
                code = code[3:]
            pred = 'skos:exactMatch' if r['mapType'].strip().lower() == 'exact' else 'skos:closeMatch'
            sid = 'TCM-SO:' + r['symptom_localname'].strip()
            sl = r['symptom_en'].strip()
            oid = cfg['obj_prefix'] + ':' + code
            ol = r[cfg['term_col']].strip()
            f.write(f"{sid}\t{sl}\t{pred}\t{oid}\t{ol}\tsemapv:ManualMappingCuration\n")
            n += 1
    print(cfg['out'], 'rows=', n)

# 汇总校验
total = 0
exact = close = 0
for cfg in CONFIGS:
    with open(os.path.join(BASE, cfg['out']), encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or line.startswith('subject_id'):
                continue
            total += 1
            if 'skos:exactMatch' in line:
                exact += 1
            elif 'skos:closeMatch' in line:
                close += 1
print('TOTAL:', total, 'exact:', exact, 'close:', close)
