#!/usr/bin/env python3
"""Recheck pair/header counts and accession overlap using derived public identifiers."""
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
labels=(ROOT/'data/source/prosspec_accession_labels.txt').read_text().splitlines()
analyzed=[next(v.split('=',1)[1] for v in r.split('|') if v.startswith('accession=')) for r in (ROOT/'natural_nia_pro_sequences.fasta').read_text().splitlines() if r.startswith('>')]
# Our curated headers carry an explicit accession= field; no isoform inference is made.
expected=json.loads((ROOT/'data/provenance/prosspec_overlap.json').read_text())
shared=sorted(set(labels)&set(analyzed))
result=dict(prosspec_pairs=len(labels),prosspec_distinct_accession_labels=len(set(labels)),project_analyzed=len(analyzed),shared_accession_labels=shared,shared_accession_count=len(shared))
for key,value in result.items():
    if value!=expected[key]:raise ValueError('Mismatch in '+key)
result['comparison_level']=expected['comparison_level']
(ROOT/'results/prosspec_overlap_recheck.json').write_text(json.dumps(result,indent=2)+'\n')
print('ProSSpeC: %d headers, %d unique labels, %d/%d accession overlap'%(len(labels),len(set(labels)),len(shared),len(analyzed)))
