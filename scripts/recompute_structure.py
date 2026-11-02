#!/usr/bin/env python3
"""Recompute experimental PDB C-alpha coordinates and audit positional mappings."""
import csv,json,sqlite3,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from Bio.PDB.MMCIF2Dict import MMCIF2Dict
from Bio.SeqUtils import seq1
from tev_history import CANONICAL_TEV_SEQUENCE
rows=[];maps={}
for pdb in ('1LVB','1LVM'):
    d=MMCIF2Dict(str(ROOT/'data/source/structures'/(pdb+'.cif')))
    sequence=''.join(d['_entity_poly.pdbx_seq_one_letter_code_can'][0].split())
    offset=sequence.index('GESLF')
    if sequence[offset:offset+20]!=CANONICAL_TEV_SEQUENCE[:20]:raise ValueError('Canonical anchor mismatch')
    for chain,label,author in zip(d['_pdbx_poly_seq_scheme.pdb_strand_id'],d['_pdbx_poly_seq_scheme.seq_id'],d['_pdbx_poly_seq_scheme.auth_seq_num']):
        pos=int(label)-offset
        if chain in ('A','B') and 1<=pos<=len(sequence)-offset:
            maps['map_'+pdb+'_'+chain+'_'+label]=(pos,sequence[int(label)-1],CANONICAL_TEV_SEQUENCE[pos-1])
    keys=['label_atom_id','label_asym_id','label_seq_id','auth_asym_id','label_comp_id','Cartn_x','Cartn_y','Cartn_z']
    for atom,asym,label,chain,residue,x,y,z in zip(*(d['_atom_site.'+k] for k in keys)):
        if atom=='CA' and chain in ('A','B') and label.isdigit() and 1<=int(label)-offset<=len(sequence)-offset:
            rows.append(dict(pdb_id=pdb,chain_id=chain,canonical_position=int(label)-offset,residue=seq1(residue),x=float(x),y=float(y),z=float(z)))
expected=list(csv.DictReader((ROOT/'build/structure_ca_coordinates.csv').open()))
if len(rows)!=len(expected):raise ValueError('Coordinate row count mismatch')
for got,want in zip(rows,expected):
    for key,value in got.items():
        if isinstance(value,(int,float)):
            if abs(value-float(want[key]))>1e-10:raise ValueError('Coordinate mismatch')
        elif value!=want[key]:raise ValueError('Coordinate identifier mismatch')
db=sqlite3.connect('file:'+str(ROOT/'tev_history.sqlite')+'?mode=ro',uri=True)
for ident,(pos,source,canonical) in maps.items():
    got=db.execute('SELECT canonical_position,source_residue,canonical_residue FROM residue_maps WHERE residue_map_id=?',(ident,)).fetchone()
    if got!=(pos,source,canonical):raise ValueError('Residue map mismatch '+ident)
db.close()
report=dict(status='PASS',coordinate_rows=len(rows),residue_maps=len(maps),evidence='EXPERIMENTAL; positional correspondence does not imply amino-acid identity or mechanism')
(ROOT/'results/structure_recheck.json').write_text(json.dumps(report,indent=2)+'\n')
print('Recomputed %d C-alpha rows and verified %d PDB-to-canonical mappings'%(len(rows),len(maps)))
