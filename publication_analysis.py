"""Small, dependency-free methods used in the TEV publication release.

Tree comparisons are unrooted RF distances on the intersection of taxa. Genus
balancing is a descriptive sensitivity analysis, not a phylogenetic model or a
substitute for experimental replication.
"""
from collections import Counter, defaultdict
import math
from typing import Any, Dict
from evolution_analysis import accession_from_label, walk_nodes

AMINO_ACIDS = frozenset('ACDEFGHIKLMNPQRSTVWY')


def tip_id(label):
    return accession_from_label(label) or label


def unrooted_splits(tree, keep=None):
    """Return nontrivial edge bipartitions after projection onto retained taxa."""
    taxa = {tip_id(node.name) for node in walk_nodes(tree) if node.is_leaf}
    retained = taxa if keep is None else taxa.intersection(keep)
    splits = set()

    def descendants(node):
        if node.is_leaf:
            return {tip_id(node.name)}.intersection(retained)
        left = set()
        for child in node.children:
            left.update(descendants(child))
        right = retained.difference(left)
        if min(len(left), len(right)) >= 2:
            a, b = tuple(sorted(left)), tuple(sorted(right))
            splits.add(min((a, b), key=lambda x: (len(x), x)))
        return left

    descendants(tree)
    return splits


def split_comparison(tree_a, tree_b) -> Dict[str, Any]:
    taxa_a = {tip_id(n.name) for n in walk_nodes(tree_a) if n.is_leaf}
    taxa_b = {tip_id(n.name) for n in walk_nodes(tree_b) if n.is_leaf}
    shared = taxa_a.intersection(taxa_b)
    if len(shared) < 4:
        raise ValueError('An informative unrooted comparison requires at least four shared taxa')
    a, b = unrooted_splits(tree_a, shared), unrooted_splits(tree_b, shared)
    distance = len(a.symmetric_difference(b))
    return dict(shared_taxa=len(shared), splits_a=len(a), splits_b=len(b),
                shared_splits=len(a.intersection(b)), robinson_foulds_distance=distance,
                normalized_rf=distance / (len(a) + len(b)) if a or b else 0.0)


def weighted_column(residues, groups) -> Dict[str, Any]:
    """Equal total weight per supplied group, with gaps excluded from AA counts."""
    if len(residues) != len(groups) or not groups:
        raise ValueError('Each residue needs exactly one nonempty group assignment')
    counts = Counter(groups)
    weights = [1.0 / counts[group] for group in groups]
    total = sum(weights)
    observed = defaultdict(float)
    for residue, weight in zip(residues, weights):
        if residue in AMINO_ACIDS:
            observed[residue] += weight
    observed_total = sum(observed.values())
    frequencies = {aa: weight / observed_total for aa, weight in sorted(observed.items())} if observed_total else {}
    entropy = -sum(p * math.log(p, 2) for p in frequencies.values())
    return dict(frequencies=frequencies, entropy_bits=entropy,
                normalized_conservation=1 - entropy / math.log(20, 2) if observed_total else None,
                coverage=observed_total / total,
                kish_effective_n=total ** 2 / sum(w * w for w in weights))
