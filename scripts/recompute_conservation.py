#!/usr/bin/env python3
"""Recompute 242 canonical conservation/coverage rows from the frozen MSA."""
import csv,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from publication_analysis import weighted_column
from evolution_analysis import accession_from_label
alignment={};label=None
for line in (ROOT/'nia_pro_alignment.fasta').read_text().splitlines():
    if line.startswith('>'):label=line[1:];alignment[label]=''
    else:alignment[label]+=line.strip()
metadata={r['accession']:r for r in csv.DictReader((ROOT/'homolog_metadata.csv').open())}
columns={}
for r in csv.DictReader((ROOT/'msa_positions.csv').open()):
    if r['canonical_tev_position']:
        pos=int(r['canonical_tev_position']);col=int(r['msa_column'])-1
        if pos in columns and columns[pos]!=col:raise ValueError('Conflicting canonical mapping')
        columns[pos]=col
expected=list(csv.DictReader((ROOT/'build/publication_natural/conservation_sensitivity.csv').open()))
excluded={'A0AUJ5','A4KZ49','Q65730'}
output=[]
for row in expected:
    pos=int(row['canonical_position']);col=columns[pos]
    labels=list(alignment);residues=[alignment[k][col] for k in labels]
    groups=[metadata[accession_from_label(k)]['genus'] for k in labels]
    raw=weighted_column(residues,['same']*len(labels));balanced=weighted_column(residues,groups)
    retained=[alignment[k][col] for k in labels if accession_from_label(k) not in excluded]
    without=weighted_column(retained,['same']*len(retained))
    values={'canonical_position':pos,'raw_conservation':raw['normalized_conservation'],'raw_coverage':raw['coverage'],'genus_balanced_conservation':balanced['normalized_conservation'],'genus_balanced_coverage':balanced['coverage'],'exclude3_conservation':without['normalized_conservation']}
    for key,value in values.items():
        if abs(float(row[key])-value)>1e-10:raise ValueError('Mismatch at '+str(pos)+' '+key)
    output.append(values)
(ROOT/'results/conservation_recheck.json').write_text(json.dumps({'positions':len(output),'status':'PASS','computed':output},indent=2)+'\n')
print('Recomputed and matched 242 canonical positions, three conservation curves and two coverages')
