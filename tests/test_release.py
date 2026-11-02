import csv,hashlib,json,sqlite3,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
class ReleaseIntegrity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.db=sqlite3.connect('file:'+str(ROOT/'tev_history.sqlite')+'?mode=ro',uri=True)
        cls.db.row_factory=sqlite3.Row
    @classmethod
    def tearDownClass(cls):cls.db.close()
    def test_database_constraints(self):
        self.assertEqual(self.db.execute('PRAGMA integrity_check').fetchone()[0],'ok')
        self.assertEqual(self.db.execute('PRAGMA foreign_key_check').fetchall(),[])
    def test_all_input_hashes(self):
        for path,expected in json.loads((ROOT/'data/provenance/SHA256SUMS.json').read_text()).items():
            with self.subTest(path=path):self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),expected)
    def test_csv_roundtrip_preserves_null_and_strings(self):
        queries=json.loads((ROOT/'data/provenance/sql_allowlist.json').read_text())
        for table,entry in queries.items():
            rows=self.db.execute(entry['count']).fetchone()[0]
            with (ROOT/'data/tables'/(table+'.csv')).open() as f:
                source=list(csv.DictReader(f))
            restored=list(self.db.execute(entry['select']))
            self.assertEqual(len(restored),len(source))
            for got,want in zip(restored,source):
                for field,value in want.items():
                    actual=got[field]
                    if value=='\\N':self.assertIsNone(actual,(table,field))
                    elif isinstance(actual,int):self.assertEqual(actual,int(value),(table,field))
                    elif isinstance(actual,float):self.assertEqual(actual,float(value),(table,field))
                    else:self.assertEqual(actual,value,(table,field))
        r=self.db.execute("SELECT assay_temperature_c,notes FROM assay_protocols WHERE protocol_id='nam_kin'").fetchone()
        self.assertIsNone(r[0]);self.assertIn('not reported',r[1])
    def test_measurement_traceability(self):
        rows=self.db.execute('SELECT * FROM measurements').fetchall()
        self.assertEqual(len(rows),168)
        for r in rows:
            for field in ['source_id','source_figure_table','protocol_id','extraction_method','value_qualifier']:
                self.assertTrue(r[field],(r['measurement_id'],field))
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM training_ready').fetchone()[0],0)
    def test_curation_correction_retains_prior_value(self):
        changes=json.loads((ROOT/'data/provenance/curation_corrections.json').read_text())
        self.assertEqual(len(changes),7)
        self.assertTrue(all(c['before']!=c['after'] and c['source'] for c in changes))
        rows=self.db.execute("SELECT reducing_agent FROM measurements WHERE protocol_id='nam_kin'").fetchall()
        self.assertTrue(all('not reported' in r[0] for r in rows))
    def test_natural_scope_is_not_candidate_scope(self):
        def nseq(p):return sum(line.startswith('>') for line in (ROOT/p).read_text().splitlines())
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM natural_homologs').fetchone()[0],1505)
        self.assertEqual(nseq('natural_nia_pro_sequences.fasta'),35)
        self.assertEqual(nseq('nia_pro_alignment.fasta'),35)
        self.assertEqual(nseq('build/phylogeny/nia_pro_representative_alignment.fasta'),23)
        rows=self.db.execute('SELECT low_temperature_activity_status FROM natural_homologs').fetchall()
        self.assertEqual(set(r[0] for r in rows),{'UNKNOWN'})
    def test_patent_and_fitting_qualifiers(self):
        r=self.db.execute("SELECT notes FROM assay_protocols WHERE protocol_id='pat_slope4'").fetchone()[0]
        self.assertIn('not independently measured',r)
        r=self.db.execute("SELECT notes FROM assay_protocols WHERE protocol_id='dav_kin_eq2'").fetchone()[0]
        self.assertIn('not independent',r)
        product=self.db.execute("SELECT source_id,patent_mapping_status,sequence_availability FROM commercial_products WHERE product_id='neb_p8118'").fetchone()
        self.assertEqual(product[0],'src_neb_p8118_spec')
        self.assertEqual(product[1],'UNRESOLVED')
        self.assertIn('Not disclosed',product[2])
    def test_five_figure_outputs(self):
        manifest=json.loads((ROOT/'results/figure_manifest.json').read_text())
        self.assertEqual(len(manifest),5)
        for r in manifest:
            for ext in ['png','svg','pdf']:self.assertTrue((ROOT/'results/figures'/(r['id']+'.'+ext)).is_file())
if __name__=='__main__':unittest.main()
