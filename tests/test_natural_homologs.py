import unittest

import natural_homologs
import tev_history


P04517_CHAIN_FIELD = (
    'CHAIN 1..3054; /note="Genome polyprotein"; /id="PRO_0000420026"; '
    'CHAIN 1850..2037; /note="Viral genome-linked protein"; '
    '/evidence="ECO:0000250"; /id="PRO_0000040456"; '
    'CHAIN 2038..2279; /note="Nuclear inclusion protein A"; '
    '/evidence="ECO:0000250"; /id="PRO_0000040457"; '
    'CHAIN 2280..2791; /note="Nuclear inclusion protein B"; '
    '/id="PRO_0000040458"'
)


class ChainBoundaryTests(unittest.TestCase):
    def test_extracts_exact_nia_pro_chain(self):
        features = natural_homologs.parse_chain_features(P04517_CHAIN_FIELD)
        boundary = natural_homologs.find_nia_pro_boundary(features)
        self.assertIsNotNone(boundary)
        assert boundary is not None

        self.assertEqual(2038, boundary["start"])
        self.assertEqual(2279, boundary["end"])
        self.assertEqual("Nuclear inclusion protein A", boundary["description"])
        self.assertIn("ECO:0000250", boundary["evidence"])

    def test_p04517_record_recovers_canonical_mature_sequence(self):
        prefix = "A" * 2037
        suffix = "C" * (3054 - 2279)
        row = {
            "Entry": "P04517",
            "Entry Name": "POLG_TEV",
            "Reviewed": "reviewed",
            "Protein names": "Genome polyprotein",
            "Organism": "Tobacco etch virus (TEV)",
            "Organism (ID)": "12227",
            "Taxonomic lineage": "Viruses, Potyviridae, Potyvirus",
            "Virus hosts": "Nicotiana tabacum [TaxID: 4097]",
            "Sequence": prefix + tev_history.CANONICAL_TEV_SEQUENCE + suffix,
            "Length": "3054",
            "Chain": P04517_CHAIN_FIELD,
            "Protein existence": "Evidence at protein level",
            "Annotation": "5.0",
        }

        record = natural_homologs.curate_uniprot_record(row, "2026_03")

        self.assertEqual("FULL_POLYPROTEIN", record["source_record_type"])
        self.assertEqual("COMPLETE", record["domain_completeness"])
        self.assertEqual(tev_history.CANONICAL_TEV_SEQUENCE, record["mature_sequence"])
        self.assertEqual(242, record["mature_sequence_length"])
        self.assertEqual("UNKNOWN", record["low_temperature_activity_status"])
        self.assertTrue(record["include_in_qc_fasta"])

    def test_missing_chain_is_retained_but_not_in_qc_fasta(self):
        row = {
            "Entry": "A0ATEST",
            "Entry Name": "POLG_TEST",
            "Reviewed": "unreviewed",
            "Protein names": "Genome polyprotein",
            "Organism": "Example potyvirus (isolate X)",
            "Organism (ID)": "999999",
            "Taxonomic lineage": "Viruses, Potyviridae, Potyvirus",
            "Virus hosts": "Example host",
            "Sequence": "A" * 3000,
            "Length": "3000",
            "Chain": "",
            "Protein existence": "Predicted",
            "Annotation": "2.0",
        }

        record = natural_homologs.curate_uniprot_record(row, "2026_03")

        self.assertEqual("UNRESOLVED", record["domain_completeness"])
        self.assertEqual("PREDICTED_PROTEIN", record["source_record_type"])
        self.assertFalse(record["include_in_qc_fasta"])
        self.assertIn("boundary", record["exclusion_reason"].lower())


class DuplicateGroupingTests(unittest.TestCase):
    def test_identical_mature_sequences_form_one_event_group(self):
        sequence = tev_history.CANONICAL_TEV_SEQUENCE
        records = [
            {
                "accession": "A0A000",
                "record_status": "UNREVIEWED",
                "mature_sequence": sequence,
                "mature_sequence_sha256": tev_history.sha256_sequence(sequence),
                "domain_completeness": "COMPLETE",
                "annotation_score": 3.0,
                "include_in_qc_fasta": True,
            },
            {
                "accession": "P04517",
                "record_status": "REVIEWED",
                "mature_sequence": sequence,
                "mature_sequence_sha256": tev_history.sha256_sequence(sequence),
                "domain_completeness": "COMPLETE",
                "annotation_score": 5.0,
                "include_in_qc_fasta": True,
            },
        ]

        grouped = natural_homologs.assign_sequence_representatives(records)
        representatives = [r for r in grouped if r["is_sequence_representative"]]

        self.assertEqual(1, len(representatives))
        self.assertEqual("P04517", representatives[0]["accession"])
        self.assertEqual(
            grouped[0]["duplicate_group_sha256"],
            grouped[1]["duplicate_group_sha256"],
        )
        self.assertEqual(2, grouped[0]["duplicate_group_size"])
        self.assertEqual(2, grouped[1]["duplicate_group_size"])


if __name__ == "__main__":
    unittest.main()
