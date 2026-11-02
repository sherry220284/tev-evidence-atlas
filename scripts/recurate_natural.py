#!/usr/bin/env python3
"""Re-extract mature domains from the frozen redistributable UniProt candidate TSV."""
import json,sys,tempfile,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from natural_homologs import read_uniprot_tsv,write_metadata_csv,write_representative_fasta
records=read_uniprot_tsv(str(ROOT/'data/source/uniprot_potyviridae_ipr001730_2026_03.tsv'),'2026_03')
assert len(records)==1505
assert sum(bool(r['is_sequence_representative']) for r in records)==35
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/'domains.fasta';write_representative_fasta(records,str(p))
    assert p.read_bytes()==(ROOT/'natural_nia_pro_sequences.fasta').read_bytes()
    write_metadata_csv(records,str(ROOT/'results/homolog_metadata_recurated.csv'))
report={'status':'PASS','candidate_count':len(records),'sequence_representatives':35,'fasta_byte_identical':True,'fasta_sha256':hashlib.sha256((ROOT/'natural_nia_pro_sequences.fasta').read_bytes()).hexdigest()}
(ROOT/'results/natural_source_recheck.json').write_text(json.dumps(report,indent=2)+'\n')
print('Frozen UniProt 1505 candidates -> 35 mature domains; FASTA byte-identical')
