#!/usr/bin/env python3
"""Rebuild a local SQLite review copy using fixed, audited SQL statements."""
import csv,json,sqlite3
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def main():
    target=ROOT/'tev_history.sqlite'
    if target.exists():target.unlink()
    db=sqlite3.connect(str(target))
    db.executescript((ROOT/'data/schema.sql').read_text())
    queries=json.loads((ROOT/'data/provenance/sql_allowlist.json').read_text())
    counts={}
    for table,entry in sorted(queries.items()):
        with (ROOT/'data/tables'/(table+'.csv')).open() as f:
            reader=csv.reader(f)
            if next(reader)!=entry['columns']:raise ValueError('Unexpected CSV columns')
            db.executemany(entry['insert'],[[None if v=='\\N' else v for v in row] for row in reader])
        counts[table]=db.execute(entry['count']).fetchone()[0]
    db.commit()
    if db.execute('PRAGMA integrity_check').fetchone()[0]!='ok':raise ValueError('Integrity check failed')
    if db.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Foreign key check failed')
    if counts!=json.loads((ROOT/'data/provenance/table_counts.json').read_text()):raise ValueError('Count mismatch')
    db.close()
    (ROOT/'results').mkdir(exist_ok=True)
    (ROOT/'results/database_rebuild.json').write_text(json.dumps(dict(status='PASS',table_counts=counts),indent=2)+'\n')
    print('Rebuilt SQLite; integrity, foreign keys and all table counts PASS')
if __name__=='__main__':main()
