#!/usr/bin/env python3
"""Recompute RF diagnostics from archived trees; no new inference claimed."""
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from evolution_analysis import parse_newick
from publication_analysis import split_comparison
base=parse_newick((ROOT/'nia_pro_phylogeny.nwk').read_text())
original=json.loads((ROOT/'build/publication_natural/natural_review_summary.json').read_text())
results=[]
for expected in original['phylogeny_sensitivity']:
    tag=expected['analysis']; tree=parse_newick((ROOT/('build/publication_natural/'+tag+'.treefile')).read_text())
    result=split_comparison(base,tree)
    assert abs(result['normalized_rf']-expected['normalized_rf'])<1e-12
    result['analysis']=tag;results.append(result)
(ROOT/'results/natural_recheck.json').write_text(json.dumps(results,indent=2)+'\n')
print('Three archived-tree RF comparisons recomputed and matched')
