"""Regression checks for the publication analysis, independent of optional plotting tools."""
import unittest
from pathlib import Path
import sys
from typing import Any, Dict

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from evolution_analysis import parse_newick
from publication_analysis import split_comparison, weighted_column


class PublicationAnalysisTests(unittest.TestCase):
    def test_unrooted_comparison_ignores_display_root(self):
        a = parse_newick('((A:1,B:1):1,(C:1,D:1):1);')
        b = parse_newick('(A:1,(B:1,(C:1,D:1):1):1);')
        result = split_comparison(a, b)
        self.assertEqual(result['robinson_foulds_distance'], 0)
        self.assertEqual(result['splits_a'], 1)

    def test_incompatible_quartets_have_maximal_normalized_distance(self):
        a = parse_newick('((A:1,B:1):1,(C:1,D:1):1);')
        b = parse_newick('((A:1,C:1):1,(B:1,D:1):1);')
        self.assertEqual(split_comparison(a, b)['normalized_rf'], 1)

    def test_shared_taxon_projection_suppresses_trivial_splits(self):
        a = parse_newick('((A:1,E:1):1,B:1,(C:1,D:1):1);')
        b = parse_newick('((A:1,B:1):1,(C:1,D:1):1);')
        self.assertEqual(split_comparison(a, b)['robinson_foulds_distance'], 0)
        self.assertEqual(split_comparison(a, b)['shared_taxa'], 4)

    def test_genus_balancing_does_not_count_large_genus_as_replicated_evidence(self):
        result: Dict[str, Any] = weighted_column(['A', 'A', 'G'], ['Potyvirus', 'Potyvirus', 'Bymovirus'])
        self.assertAlmostEqual(result['frequencies']['A'], 0.5)
        self.assertAlmostEqual(result['frequencies']['G'], 0.5)
        self.assertAlmostEqual(result['entropy_bits'], 1)
        self.assertAlmostEqual(result['kish_effective_n'], 8/3)

    def test_gaps_reduce_coverage_instead_of_becoming_an_amino_acid(self):
        result = weighted_column(['-', 'A'], ['Potyvirus', 'Bymovirus'])
        self.assertEqual(result['coverage'], 0.5)
        self.assertEqual(result['frequencies'], {'A': 1.0})


if __name__ == '__main__':
    unittest.main()
