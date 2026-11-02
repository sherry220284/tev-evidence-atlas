"""Alignment and phylogeny analysis primitives for the Natural NIa-Pro Atlas."""

from __future__ import unicode_literals

import collections
import math
import re


STANDARD_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")


class NewickNode(object):
    def __init__(self, name="", length=0.0, children=None):
        self.name = name
        self.length = float(length or 0.0)
        self.children = list(children or [])

    @property
    def is_leaf(self):
        return not self.children


def parse_newick(text):
    """Parse the unquoted Newick emitted by IQ-TREE."""
    source = text.strip()
    position = [0]

    def skip_whitespace():
        while position[0] < len(source) and source[position[0]].isspace():
            position[0] += 1

    def read_token():
        skip_whitespace()
        start = position[0]
        while position[0] < len(source) and source[position[0]] not in ",():;":
            position[0] += 1
        return source[start : position[0]].strip()

    def read_length():
        skip_whitespace()
        if position[0] >= len(source) or source[position[0]] != ":":
            return 0.0
        position[0] += 1
        token = read_token()
        if not token:
            raise ValueError("missing branch length in Newick")
        return float(token)

    def parse_subtree():
        skip_whitespace()
        if position[0] >= len(source):
            raise ValueError("unexpected end of Newick")
        if source[position[0]] == "(":
            position[0] += 1
            children = [parse_subtree()]
            while True:
                skip_whitespace()
                if position[0] >= len(source):
                    raise ValueError("unterminated internal node in Newick")
                marker = source[position[0]]
                if marker == ",":
                    position[0] += 1
                    children.append(parse_subtree())
                elif marker == ")":
                    position[0] += 1
                    break
                else:
                    raise ValueError("unexpected token in Newick: %s" % marker)
            name = read_token()
            return NewickNode(name=name, length=read_length(), children=children)
        name = read_token()
        if not name:
            raise ValueError("missing leaf name in Newick")
        return NewickNode(name=name, length=read_length())

    root = parse_subtree()
    skip_whitespace()
    if position[0] < len(source) and source[position[0]] == ";":
        position[0] += 1
    skip_whitespace()
    if position[0] != len(source):
        raise ValueError("trailing content after Newick tree")
    return root


def walk_nodes(root):
    yield root
    for child in root.children:
        for node in walk_nodes(child):
            yield node


def terminal_branch_lengths(root):
    return {node.name: node.length for node in walk_nodes(root) if node.is_leaf}


def internal_supports(root):
    supports = []
    for node in walk_nodes(root):
        if node.is_leaf or not node.name:
            continue
        match = re.match(r"^([0-9.]+)/([0-9.]+)$", node.name)
        if match:
            supports.append((float(match.group(1)), float(match.group(2))))
    return supports


def accession_from_label(label):
    match = re.search(r"(?:^|\|)accession(?:=|_)([^|]+)", label)
    return match.group(1) if match else ""


def reference_column_map(records, reference_accession="P04517"):
    reference_sequence = None
    lengths = set()
    for header, sequence in records:
        lengths.add(len(sequence))
        if accession_from_label(header) == reference_accession:
            reference_sequence = sequence
    if len(lengths) != 1:
        raise ValueError("alignment records do not have a common length")
    if reference_sequence is None:
        raise ValueError("reference accession is absent from alignment")

    result = {}
    reference_position = 0
    for column, residue in enumerate(reference_sequence, start=1):
        if residue not in "-.":
            reference_position += 1
            result[column] = reference_position
        else:
            result[column] = None
    return result


def summarize_alignment_column(residues, sequence_count):
    observed = [residue.upper() for residue in residues if residue.upper() in STANDARD_AMINO_ACIDS]
    counts = collections.Counter(observed)
    observed_count = len(observed)
    if observed_count:
        majority_aa, majority_count = sorted(
            counts.items(), key=lambda item: (-item[1], item[0])
        )[0]
        entropy = -sum(
            (count / float(observed_count))
            * math.log(count / float(observed_count), 2)
            for count in counts.values()
        )
        majority_fraction = majority_count / float(observed_count)
    else:
        majority_aa = ""
        entropy = 0.0
        majority_fraction = 0.0
    return {
        "observed_residue_count": observed_count,
        "coverage_fraction": observed_count / float(sequence_count) if sequence_count else 0.0,
        "distinct_aa_count": len(counts),
        "majority_aa": majority_aa,
        "majority_fraction": majority_fraction,
        "shannon_entropy_bits": entropy,
        "normalized_conservation": 1.0 - (entropy / math.log(20.0, 2)),
        "amino_acid_counts": dict(sorted(counts.items())),
    }


def median(values):
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("median requires at least one value")
    midpoint = len(ordered) // 2
    if len(ordered) % 2:
        return ordered[midpoint]
    return (ordered[midpoint - 1] + ordered[midpoint]) / 2.0


def quantile(values, probability):
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("quantile requires at least one value")
    if not 0.0 <= probability <= 1.0:
        raise ValueError("probability must be between zero and one")
    location = (len(ordered) - 1) * probability
    lower = int(location)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = location - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def upper_tukey_fences(values):
    first_quartile = quantile(values, 0.25)
    third_quartile = quantile(values, 0.75)
    interquartile_range = third_quartile - first_quartile
    return (
        third_quartile + 1.5 * interquartile_range,
        third_quartile + 3.0 * interquartile_range,
    )


def robust_high_zscores(values):
    """Return one-sided robust z scores based on median absolute deviation."""
    center = median(values)
    deviation = median([abs(float(value) - center) for value in values])
    if deviation == 0.0:
        return [0.0 for _ in values]
    return [0.67448975 * (float(value) - center) / deviation for value in values]
