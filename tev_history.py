"""Pure sequence/ID helpers retained from the historical curator for natural QC."""
import hashlib
CANONICAL_ACCESSION='P04517'
CANONICAL_TEV_SEQUENCE=(
    'GESLFKGPRDYNPISSTICHLTNESDGHTTSLYGIGFGPFIITNKHLFRRNNGTLLVQSLHGVF'
    'KVKNTTTLQQHLIDGRDMIIIRMPKDFPPFPQKLKFREPQREERICLVTTNFQTKSMSSMVSDTSC'
    'TFPSSDGIFWKHWIQTKDGQCGSPLVSTRDGFIVGIHSASNFTNTNNYFTSVPKNFMELLTNQEAQ'
    'QWVSGWRLNADSVLWGGHKVFMSKPEEPFQPVKEATQLMNELVYSQ'
)
def normalize_sequence(sequence):
    if sequence is None:raise ValueError('sequence is required')
    return ''.join(sequence.split()).upper()
def sha256_sequence(sequence):
    return hashlib.sha256(normalize_sequence(sequence).encode('ascii')).hexdigest()
def stable_id(prefix,*parts):
    payload='\x1f'.join('' if part is None else str(part).strip() for part in parts)
    return '%s_%s'%(prefix,hashlib.sha256(payload.encode('utf-8')).hexdigest()[:16])
