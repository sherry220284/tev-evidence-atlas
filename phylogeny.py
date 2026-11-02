"""Deterministic helpers for NIa-Pro phylogenetic subset selection."""

from __future__ import unicode_literals


GAP_CHARACTERS = frozenset("-.")


def read_fasta(path):
    records = []
    header = None
    sequence_parts = []
    with open(path, "r") as handle:
        for raw_line in handle:
            line = raw_line.strip()
            if not line:
                continue
            if line.startswith(">"):
                if header is not None:
                    records.append((header, "".join(sequence_parts)))
                header = line[1:]
                sequence_parts = []
            elif header is None:
                raise ValueError("FASTA sequence encountered before first header")
            else:
                sequence_parts.append(line)
    if header is not None:
        records.append((header, "".join(sequence_parts)))
    return records


def write_fasta(path, records, line_width=80):
    with open(path, "w") as handle:
        for header, sequence in records:
            handle.write(">{}\n".format(header))
            for offset in range(0, len(sequence), line_width):
                handle.write(sequence[offset : offset + line_width] + "\n")


def header_field(header, key):
    prefix = key + "="
    for field in header.split("|"):
        if field.startswith(prefix):
            return field[len(prefix) :]
    return None


def pairwise_identity(sequence_a, sequence_b):
    if len(sequence_a) != len(sequence_b):
        raise ValueError("aligned sequences must have equal length")
    compared = [
        (a, b)
        for a, b in zip(sequence_a.upper(), sequence_b.upper())
        if a not in GAP_CHARACTERS and b not in GAP_CHARACTERS
    ]
    if not compared:
        raise ValueError("aligned sequences have no comparable residues")
    matches = sum(a == b for a, b in compared)
    return matches / float(len(compared))


def identity_clusters(records, threshold=0.90):
    parent = list(range(len(records)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        left_root = find(left)
        right_root = find(right)
        if left_root == right_root:
            return
        parent[max(left_root, right_root)] = min(left_root, right_root)

    for left in range(len(records)):
        for right in range(left + 1, len(records)):
            if pairwise_identity(records[left][1], records[right][1]) >= threshold:
                union(left, right)

    grouped = {}
    for index in range(len(records)):
        grouped.setdefault(find(index), []).append(index)
    return sorted(grouped.values(), key=lambda cluster: cluster[0])


def select_medoid(records, cluster, mandatory_accession="P04517"):
    if not cluster:
        raise ValueError("cannot choose a representative from an empty cluster")
    for index in cluster:
        if header_field(records[index][0], "accession") == mandatory_accession:
            return index
    if len(cluster) == 1:
        return cluster[0]

    candidates = []
    for index in cluster:
        distances = [
            1.0 - pairwise_identity(records[index][1], records[other][1])
            for other in cluster
            if other != index
        ]
        mean_distance = sum(distances) / float(len(distances))
        accession = header_field(records[index][0], "accession") or records[index][0]
        candidates.append((mean_distance, accession, index))
    return min(candidates)[2]


def select_representatives(records, threshold=0.90, mandatory_accession="P04517"):
    selections = []
    for cluster_number, cluster in enumerate(
        identity_clusters(records, threshold=threshold), start=1
    ):
        selected = select_medoid(
            records, cluster, mandatory_accession=mandatory_accession
        )
        selections.append(
            {
                "cluster_number": cluster_number,
                "member_indices": cluster,
                "representative_index": selected,
            }
        )
    return selections
