import unittest

import evolution_analysis


class NewickTests(unittest.TestCase):
    def test_newick_parser_preserves_support_and_terminal_branches(self):
        root = evolution_analysis.parse_newick("(A:0.1,(B:0.2,C:0.3)90/95:0.4);")
        branches = evolution_analysis.terminal_branch_lengths(root)
        self.assertEqual({"A": 0.1, "B": 0.2, "C": 0.3}, branches)
        self.assertEqual([(90.0, 95.0)], evolution_analysis.internal_supports(root))

    def test_iqtree_tip_name_maps_back_to_accession(self):
        name = "hom_x|accession_P04517|taxid_12227|status_REVIEWED"
        self.assertEqual("P04517", evolution_analysis.accession_from_label(name))
    def test_tukey_fences_use_interpolated_quartiles(self):
        inner, outer = evolution_analysis.upper_tukey_fences([0, 1, 2, 3, 100])
        self.assertEqual(6.0, inner)
        self.assertEqual(9.0, outer)


class AlignmentMappingTests(unittest.TestCase):
    def test_reference_gap_column_has_no_canonical_position(self):
        records = [("accession=P04517", "A-C"), ("accession=OTHER", "ABC")]
        column_map = evolution_analysis.reference_column_map(records, "P04517")
        self.assertEqual({1: 1, 2: None, 3: 2}, column_map)

    def test_site_feature_coverage_ignores_gaps(self):
        feature = evolution_analysis.summarize_alignment_column(
            ["A", "A", "-", "C"], sequence_count=4
        )
        self.assertEqual(3, feature["observed_residue_count"])
        self.assertAlmostEqual(0.75, feature["coverage_fraction"])
        self.assertAlmostEqual(2.0 / 3.0, feature["majority_fraction"])


if __name__ == "__main__":
    unittest.main()
