#!/usr/bin/env python3
"""Render the five frozen v0.1 discussion figures and their exact data tables."""
import csv
import hashlib
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from Bio import Phylo
import evolution_analysis as evo

OUT = ROOT / 'results'
FIG = OUT / 'figures'
DATA = OUT / 'figure_data'
BLUE, ORANGE, GREEN, GREY = '#0072B2', '#D55E00', '#009E73', '#69757D'
SOURCES = ['src_cabrita2007', 'src_yi2013', 'src_sanchez2020', 'src_nam2020',
           'src_p1specificity2024', 'src_messing2024', 'src_davis2025', 'src_patent2026']
LABELS = ['Cabrita 2007', 'Yi 2013', 'Sanchez 2020', 'Nam 2020',
          'Golda 2024', 'Messing 2025', 'Davis 2025', 'NEB patent 2026']
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 11,
    'axes.titlesize': 14, 'axes.labelsize': 12, 'pdf.fonttype': 42, 'svg.fonttype': 'none',
    'axes.spines.top': False, 'axes.spines.right': False, 'savefig.facecolor': 'white'})
MANIFEST = []


def digest(relative):
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def rows(relative):
    with (ROOT / relative).open() as handle:
        return list(csv.DictReader(handle))


def table(name, records):
    records = list(records)
    if not records:
        raise ValueError('Empty figure data: ' + name)
    path = DATA / (name + '.csv')
    with path.open('w', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    return str(path.relative_to(OUT))


def title(ax, text):
    ax.set_title(text, loc='left', fontweight='bold', pad=14)


def save(fig, ident, data_files, source_ids, inputs, limitation):
    fig.set_size_inches(4000 / 300, 2250 / 300)
    fig.tight_layout(rect=(0, .05, 1, .96), pad=1.6)
    for extension in ['svg', 'png', 'pdf']:
        fig.savefig(str(FIG / (ident + '.' + extension)), dpi=300)
    MANIFEST.append(dict(id=ident, data_files=data_files, source_ids=source_ids,
        input_sha256={p: digest(p) for p in inputs}, limitation=limitation,
        formats=['SVG', 'PNG 4000x2250 (300 dpi)', 'PDF']))
    plt.close(fig)


def historical_sites(db):
    mutations = [dict(r) for r in db.execute('SELECT * FROM mutations ORDER BY canonical_position,source_id,mutation_id')]
    coord = [r for r in rows('build/structure_ca_coordinates.csv') if r['pdb_id'] == '1LVB' and r['chain_id'] == 'A']
    xyz = np.array([[float(r[k]) for k in ['x', 'y', 'z']] for r in coord])
    centered = xyz - xyz.mean(axis=0)
    _, _, basis = np.linalg.svd(centered, full_matrices=False)
    xy = centered.dot(basis[:2].T)
    positions = [int(r['canonical_position']) for r in coord]
    sites = {r['canonical_position'] for r in mutations}
    verified = {r['canonical_position'] for r in mutations if r['mapping_status'] == 'VERIFIED'}
    fig, (a, b) = plt.subplots(1, 2, figsize=(13.333, 7.5), gridspec_kw={'width_ratios': [1, 1.4]})
    for i in range(1, len(coord)):
        if positions[i] - positions[i-1] == 1 and np.linalg.norm(xyz[i] - xyz[i-1]) < 5:
            a.plot(xy[i-1:i+1, 0], xy[i-1:i+1, 1], color='#AAB5BB', lw=1.2, zorder=1)
    for i, position in enumerate(positions):
        if position in sites:
            a.scatter(*xy[i], s=32, facecolor=ORANGE if position in verified else 'white', edgecolor=ORANGE, zorder=3)
        if position in [46, 81, 151]:
            a.scatter(*xy[i], s=60, marker='s', color=BLUE, zorder=4)
    offsets = {46: (-68, 4), 49: (13, -18), 56: (-52, -13), 76: (10, 12),
               81: (12, 5), 135: (-46, 12), 151: (-65, -24), 153: (8, -1), 219: (10, 4)}
    for p, offset in offsets.items():
        if p in positions:
            i = positions.index(p)
            label = '151 Ala*' if p == 151 else str(p)
            a.annotate(label, xy[i], xytext=offset, textcoords='offset points', fontsize=10,
                       arrowprops={'arrowstyle': '-', 'color': GREY, 'lw': .5})
    a.set_aspect('equal'); a.axis('off')
    title(a, 'A  Historical sites on experimental 1LVB chain A')
    for j, source in enumerate(SOURCES):
        grouped = {}
        for m in mutations:
            if m['source_id'] == source:
                grouped.setdefault(m['canonical_position'], []).append(m)
        for p, group in grouped.items():
            good = any(m['mapping_status'] == 'VERIFIED' for m in group)
            b.scatter(p, j, marker='o' if good else 'o', s=65,
                      facecolor=ORANGE if good else 'white', edgecolor=ORANGE, linewidth=1.3)
    for p in [46, 81, 151]:
        b.axvline(p, color=BLUE, linestyle=':', lw=1)
    b.scatter([], [], facecolor=ORANGE, edgecolor=ORANGE, label='Sequence-verified mapping')
    b.scatter([], [], facecolor='white', edgecolor=ORANGE, label='Source notation; full sequence unresolved')
    b.set_yticks(range(8)); b.set_yticklabels(LABELS); b.invert_yaxis()
    b.set_xlim(0, 243); b.set_xticks([1, 46, 81, 151, 219, 242]); b.set_xlabel('Canonical mature TEV position')
    b.legend(loc='lower center', bbox_to_anchor=(.45, -.26), frameon=False, fontsize=10)
    title(b, 'B  Reported mutation positions by source')
    fig.text(.035, .025, '*1LVB is an inactive C151A crystal construct. Dotted lines: catalytic positions. No mechanistic effect is inferred.', fontsize=10)
    data = [table('F1_mutations', mutations), table('F1_experimental_coordinates', coord)]
    save(fig, 'F1_history_structure', data, SOURCES + ['src_pdb_1LVB'],
         ['tev_history.sqlite', 'build/structure_ca_coordinates.csv', 'data/tables/sources.csv'],
         'Positions include negative results and background mutations; marks do not mean beneficial changes. PCA projection is not a distance map. Missing coordinate segments are not connected.')


def coverage(db):
    measurements = [dict(r) for r in db.execute('SELECT * FROM measurements ORDER BY source_id,measurement_id')]
    fig, (a, b) = plt.subplots(1, 2, figsize=(13.333, 7.5), gridspec_kw={'width_ratios': [1, 1.4]})
    count = [sum(r['source_id'] == s for r in measurements) for s in SOURCES]
    a.barh(range(8), count, color=[BLUE]*7+[ORANGE]); a.set_yticks(range(8)); a.set_yticklabels(LABELS); a.invert_yaxis()
    for i, n in enumerate(count): a.text(n+.6, i, str(n), va='center')
    a.set_xlim(0, max(count)+7); a.set_xlabel('Measurement rows; not independent experiments')
    title(a, 'A  Curated endpoints within the frozen scope')
    field_groups = [('Temperature', ['assay_temperature_c']), ('Reaction time', ['reaction_time_value']),
        ('Enzyme concentration', ['enzyme_concentration_value']), ('Substrate concentration', ['substrate_concentration_value']),
        ('Buffer text', ['reaction_buffer']), ('pH', ['ph_value']), ('Replicate count', ['replicate_count']),
        ('Uncertainty value', ['uncertainty_value'])]
    conditions = []
    for label, fields in field_groups:
        n = sum(all(r[f] is not None and r[f] != '' for f in fields) for r in measurements)
        conditions.append(dict(field=label, available=n, denominator=len(measurements), percent=100*n/len(measurements)))
    b.barh(range(len(conditions)), [x['percent'] for x in conditions], color=GREEN)
    b.set_yticks(range(len(conditions))); b.set_yticklabels([x['field'] for x in conditions]); b.invert_yaxis()
    for i, x in enumerate(conditions): b.text(x['percent']+1, i, '%d/168' % x['available'], va='center', fontsize=10)
    b.set_xlim(0, 125); b.set_xticks([0, 25, 50, 75, 100]); b.set_xlabel('Non-NULL structured fields (%)')
    title(b, 'B  Metadata availability across the 168 rows')
    fig.text(.035, .025, 'Availability is not correctness or experimental relevance. Some fields do not apply to all assay types; text conflicts remain audited.', fontsize=10)
    data = [table('F2_measurements', measurements), table('F2_source_counts', [dict(source_id=s, label=l, count=n) for s,l,n in zip(SOURCES,LABELS,count)]), table('F2_metadata_availability', conditions)]
    save(fig, 'F2_measurement_coverage', data, SOURCES, ['tev_history.sqlite'],
         'Coverage is restricted to already curated sources, not the percentage of all published TEV experiments. Multiple endpoints and two fits of a dataset are not independent replication.')


def phylogeny():
    tree_path = 'build/phylogeny/nia_pro_representative_phylogeny.nwk'
    tree = Phylo.read(str(ROOT / tree_path), 'newick')
    metadata = {r['accession']: r for r in rows('homolog_metadata.csv')}
    tips = tree.get_terminals(); depth = tree.depths(); y = {t: float(i) for i,t in enumerate(tips)}
    for node in tree.get_nonterminals(order='postorder'):
        y[node] = (y[node.clades[0]] + y[node.clades[-1]]) / 2
    fig, a = plt.subplots(figsize=(13.333, 7.5))
    support = []; tiprows = []; maxdepth = max(depth[t] for t in tips)
    flagged = {'A0AUJ5', 'A4KZ49', 'Q65730'}
    for node in tree.find_clades():
        if node.clades:
            a.plot([depth[node], depth[node]], [min(y[c] for c in node.clades), max(y[c] for c in node.clades)], color=GREY, lw=.9)
            for child in node.clades:
                a.plot([depth[node], depth[child]], [y[child], y[child]], color=GREY, lw=1)
            if node.name and '/' in node.name:
                alrt, ufb = [float(x) for x in node.name.split('/')]
                strong = alrt >= 80 and ufb >= 95
                a.scatter(depth[node], y[node], s=18, facecolor=BLUE if strong else 'white', edgecolor=BLUE, zorder=3)
                support.append(dict(descendant_accessions=';'.join(evo.accession_from_label(t.name) for t in node.get_terminals()), sh_alrt=alrt, ultrafast_bootstrap=ufb, strong_both=strong))
        else:
            acc = evo.accession_from_label(node.name); m = metadata[acc]
            label = acc + ' | ' + m['virus_name'].split(' (')[0] + (' [reviewed long branch]' if acc in flagged else '')
            a.text(depth[node] + maxdepth*.012, y[node], label, va='center', fontsize=9, color=ORANGE if acc in flagged else '#1C303A')
            tiprows.append(dict(accession=acc, virus_name=m['virus_name'], genus=m['genus'], long_branch_flag=acc in flagged, tree_label=node.name))
    a.set_xlim(0, maxdepth*2.9); a.set_ylim(len(tips)-.5, -.7); a.set_yticks([])
    a.set_xlabel('Substitutions per site; arbitrary display root (unrooted inference)')
    title(a, '23-domain representative gene tree | IQ-TREE 2.4.0 | LG+I+G4')
    a.scatter([], [], s=30, facecolor=BLUE, edgecolor=BLUE, label='SH-aLRT >=80 AND UFB >=95')
    a.scatter([], [], s=30, facecolor='white', edgecolor=BLUE, label='At least one support threshold not met')
    a.legend(loc='lower right', frameon=False, fontsize=10)
    fig.text(.035, .025, '35-domain analysis set: 27 Potyvirus. Three long branches retained after review. No experimental cold-activity labels.', fontsize=10)
    data = [table('F3_tip_metadata', tiprows), table('F3_node_support', support)]
    save(fig, 'F3_natural_phylogeny', data, ['src_uniprot'], [tree_path, 'build/phylogeny/nia_pro_representative_alignment.fasta', 'build/publication_natural/natural_review_summary.json'],
         'Gene tree from a short domain, not a rooted species history. Representative MSA has 23 sequences and 272 columns. Recombination untested; cold activity unknown.')


def conservation():
    records = rows('build/publication_natural/conservation_sensitivity.csv')
    x = np.array([int(r['canonical_position']) for r in records])
    fig, (a,b) = plt.subplots(2,1,figsize=(13.333,7.5),sharex=True,gridspec_kw={'height_ratios':[3,1]})
    for field,color,label in [('raw_conservation',BLUE,'35 domains'), ('exclude3_conservation',ORANGE,'Exclude 3 long branches (32 domains)'), ('genus_balanced_conservation',GREEN,'Equal total weight per genus')]:
        a.plot(x,[float(r[field]) for r in records],color=color,label=label,lw=1.2,alpha=.9)
    for p in [46,81,151]:
        a.axvline(p,color=GREY,lw=.9,linestyle=':');a.text(p+.8,.06,str(p),fontsize=10)
    a.set_ylim(0,1.04); a.set_ylabel('1 - H / log2(20)'); a.legend(frameon=False,loc='lower left',fontsize=10)
    title(a,'A  Conservation at 242 canonical positions; descriptive sensitivity')
    b.plot(x,[float(r['raw_coverage']) for r in records],color=BLUE,label='Observed amino-acid coverage')
    b.plot(x,[float(r['genus_balanced_coverage']) for r in records],color=GREEN,label='Weighted coverage')
    b.set_ylim(0,1.05);b.set_xlim(1,242);b.set_ylabel('Coverage');b.set_xlabel('Canonical mature TEV position')
    b.legend(frameon=False,loc='lower left',fontsize=9);title(b,'B  Alignment occupancy (gaps excluded from amino-acid entropy)')
    fig.text(.035,.025,'Sensitivity curves are not confidence intervals. High conservation does not establish mutational intolerance or cold adaptation.',fontsize=10)
    data=[table('F4_conservation_and_coverage',records)]
    save(fig,'F4_natural_conservation',data,['src_uniprot'],['nia_pro_alignment.fasta','build/publication_natural/conservation_sensitivity.csv'],
         'Potyvirus-heavy sampling (27/35), unbalanced genera and alignment gaps limit inference. No new mutational design is implied.')


def patent(db):
    records = [dict(r) for r in db.execute("SELECT * FROM measurements WHERE source_id='src_patent2026' ORDER BY measurement_id")]
    lookup = {r['measurement_id']:r for r in records}
    fig,(a,b)=plt.subplots(1,2,figsize=(13.333,7.5))
    x=np.arange(3)
    for temp,offset,color in [(0,-.10,BLUE),(4,.10,ORANGE)]:
        values=[lookup[v+'_cleavage_'+str(temp)]['raw_value_numeric'] for v in ['pat_control','pat_l76p','pat_r49f_l76p']]
        a.scatter(x+offset,values,color=color,s=75,label=str(temp)+' C')
        for pos,value in zip(x+offset,values):a.text(pos,value+3,str(int(value)),ha='center',fontsize=12)
    a.set_xticks(x);a.set_xticklabels(['Control','+L76P','+R49F/L76P']);a.set_xlim(-.45,2.45);a.set_ylim(0,110)
    a.set_ylabel('Cleavage after 18 h (%)');a.legend(frameon=False,loc='upper left');title(a,'A  Protein-substrate endpoint cleavage')
    variants=['pat_r49v','pat_l76p','pat_r49v_l76p','pat_r49f_l76p']
    values=[lookup[v+'_slope_ratio']['raw_value_numeric'] for v in variants]
    b.scatter(range(4),values,color=GREEN,s=75);b.axhline(1,color=GREY,linestyle='--',lw=1)
    for i,value in enumerate(values):b.text(i,value+.12,str(value),ha='center',fontsize=12)
    b.set_xticks(range(4));b.set_xticklabels(['+R49V','+L76P','+R49V/\nL76P','+R49F/\nL76P'])
    b.set_ylim(0,3.2);b.set_xlim(-.5,3.5);b.set_ylabel('Endpoint-fit slope ratio (fold)');title(b,'B  Four separate matched control fits at 4 C')
    fig.text(.04,.07,'Background in every construct: L56V/S135G/S219V; mature domain ends at residue 237.',fontsize=11)
    fig.text(.04,.025,'US20260234592A1, Examples 12-13, Fig. 12 / Tables 2-5. No replicate errors reported. No identity assigned to NEB P8118.',fontsize=10)
    data=[table('F5_patent_measurements',records)]
    save(fig,'F5_patent_low_temperature',data,['src_patent2026'],['tev_history.sqlite','data/tables/sources.csv'],
         'Patent-only evidence. Panel A final concentrations derived from recipe: enzyme 0.4 uM, substrate 37 uM. Panel B is not independently measured absolute kcat/Km; controls differ between paired fits.')


def main():
    FIG.mkdir(parents=True,exist_ok=True);DATA.mkdir(parents=True,exist_ok=True)
    db=sqlite3.connect('file:'+str(ROOT/'tev_history.sqlite')+'?mode=ro',uri=True);db.row_factory=sqlite3.Row
    try:
        historical_sites(db);coverage(db);phylogeny();conservation();patent(db)
    finally:db.close()
    (OUT/'figure_manifest.json').write_text(json.dumps(MANIFEST,ensure_ascii=False,indent=2)+'\n')
    from PIL import Image, ImageDraw
    sheet=Image.new('RGB',(1600,3*470),0xffffff);draw=ImageDraw.Draw(sheet)
    for i,item in enumerate(MANIFEST):
        image=Image.open(str(FIG/(item['id']+'.png')));image.thumbnail((790,440))
        x=(i%2)*800;y=(i//2)*470;sheet.paste(image,(x,y));draw.text((x+15,y+440),item['id'],fill='black')
    sheet.save(str(OUT/'figure_contact_sheet.png'))
    print('Rendered 5 figures with SVG, 4000x2250 PNG, PDF, exact data CSV and source/input manifest.')


if __name__=='__main__':main()
