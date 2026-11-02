"""Collection and curation helpers for natural Potyviridae NIa-Pro homologs."""

from __future__ import unicode_literals

import csv
import re

import tev_history


STANDARD_AMINO_ACIDS = frozenset("ACDEFGHIKLMNPQRSTVWY")
NIAPRO_DESCRIPTION_PATTERNS = (
    "nuclear inclusion protein a",
    "nia-pro",
    "nia protease",
    "nia proteinase",
    "49 kda proteinase",
    "49 kda-pro",
)

METADATA_FIELDS = (
    "homolog_id",
    "accession",
    "accession_version",
    "source_database",
    "source_release",
    "record_status",
    "taxonomy_id",
    "virus_name",
    "virus_strain",
    "host_text",
    "geographic_origin",
    "taxonomic_lineage",
    "source_record_type",
    "is_predicted",
    "source_sequence_sha256",
    "source_sequence_length",
    "domain_start",
    "domain_end",
    "mature_sequence_sha256",
    "mature_sequence_length",
    "domain_boundary_method",
    "domain_completeness",
    "annotation_evidence",
    "duplicate_group_sha256",
    "duplicate_group_size",
    "representative_homolog_id",
    "is_sequence_representative",
    "known_substrate_recognition",
    "experimental_catalysis_status",
    "low_temperature_activity_status",
    "quality_grade",
    "include_in_qc_fasta",
    "exclusion_reason",
    "protein_existence",
    "annotation_score",
    "refseq_cross_reference",
    "embl_cross_reference",
)


def _text(value):
    return "" if value is None else str(value).strip()


def parse_chain_features(chain_field):
    """Parse UniProt's flattened CHAIN field into structured exact features."""
    text = _text(chain_field)
    if not text:
        return []
    pattern = re.compile(
        r"(?:^|;\s*)CHAIN\s+([<>?]?\d+)\.\.([<>?]?\d+);"
        r"(.*?)(?=(?:;\s*CHAIN\s+)|$)",
        re.IGNORECASE,
    )
    features = []
    for match in pattern.finditer(text):
        raw_start, raw_end, body = match.groups()
        note = re.search(r'/note="([^"]+)"', body, re.IGNORECASE)
        feature_id = re.search(r'/id="([^"]+)"', body, re.IGNORECASE)
        evidences = re.findall(r'/evidence="([^"]+)"', body, re.IGNORECASE)
        exact = raw_start.isdigit() and raw_end.isdigit()
        features.append(
            {
                "start": int(raw_start.lstrip("<>?")),
                "end": int(raw_end.lstrip("<>?")),
                "exact": exact,
                "description": note.group(1) if note else "",
                "feature_id": feature_id.group(1) if feature_id else "",
                "evidence": evidences,
            }
        )
    return features


def find_nia_pro_boundary(features):
    """Return the single best exact NIa-Pro chain annotation, if present."""
    matches = []
    for feature in features:
        description = feature.get("description", "").lower()
        if any(pattern in description for pattern in NIAPRO_DESCRIPTION_PATTERNS):
            if "protein b" not in description and "nib" not in description:
                matches.append(feature)
    exact = [feature for feature in matches if feature.get("exact")]
    if len(exact) == 1:
        return exact[0]
    if len(matches) == 1:
        return matches[0]
    return None


def _extract_strain(organism_name):
    values = []
    for label in ("strain", "isolate"):
        pattern = re.compile(r"\(%s\s+([^\)]+)\)" % label, re.IGNORECASE)
        values.extend(match.group(1).strip() for match in pattern.finditer(organism_name))
    return "; ".join(values)


def _source_record_type(sequence_length, mature_length, is_predicted, has_boundary):
    if has_boundary and mature_length and sequence_length == mature_length:
        return "MATURE_PROTEASE"
    if has_boundary and sequence_length >= 1000:
        return "FULL_POLYPROTEIN"
    if has_boundary and mature_length and sequence_length > mature_length:
        return "POLYPROTEIN_FRAGMENT"
    if is_predicted:
        return "PREDICTED_PROTEIN"
    return "OTHER"


def curate_uniprot_record(row, source_release):
    """Convert one UniProt TSV row into an auditable NIa-Pro candidate record."""
    accession = _text(row.get("Entry"))
    source_sequence = tev_history.normalize_sequence(row.get("Sequence", ""))
    source_length = len(source_sequence)
    declared_length = _text(row.get("Length"))
    if declared_length and int(declared_length) != source_length:
        raise ValueError(
            "declared sequence length does not match sequence for %s" % accession
        )

    protein_existence = _text(row.get("Protein existence"))
    is_predicted = "predicted" in protein_existence.lower()
    features = parse_chain_features(row.get("Chain", ""))
    boundary = find_nia_pro_boundary(features)
    mature_sequence = ""
    mature_start = None
    mature_end = None
    completeness = "UNRESOLVED"
    boundary_method = ""
    evidence = ""
    exclusion_reason = "NIa-Pro boundary unavailable from UniProt CHAIN annotation"

    if boundary is not None:
        mature_start = boundary["start"]
        mature_end = boundary["end"]
        evidence = "; ".join(boundary.get("evidence", []))
        if not boundary.get("exact"):
            completeness = "AMBIGUOUS"
            boundary_method = "UNIPROT_CHAIN_NONEXACT"
            exclusion_reason = "NIa-Pro boundary is non-exact"
        elif not (1 <= mature_start <= mature_end <= source_length):
            completeness = "UNRESOLVED"
            boundary_method = "UNIPROT_CHAIN_INVALID"
            exclusion_reason = "NIa-Pro boundary lies outside the source sequence"
        else:
            mature_sequence = source_sequence[mature_start - 1:mature_end]
            boundary_method = "UNIPROT_CHAIN_EXACT"
            mature_chars = set(mature_sequence)
            if not 180 <= len(mature_sequence) <= 300:
                completeness = "PARTIAL"
                exclusion_reason = "NIa-Pro chain length is outside 180-300 aa QC range"
            elif not mature_chars.issubset(STANDARD_AMINO_ACIDS):
                completeness = "AMBIGUOUS"
                exclusion_reason = "NIa-Pro chain contains ambiguous amino-acid symbols"
            else:
                completeness = "COMPLETE"
                exclusion_reason = ""

    status = "REVIEWED" if _text(row.get("Reviewed")).lower() == "reviewed" else "UNREVIEWED"
    annotation_score_text = _text(row.get("Annotation"))
    annotation_score = float(annotation_score_text) if annotation_score_text else None
    include = completeness == "COMPLETE" and bool(mature_sequence)
    quality = "PARTIAL" if include else "UNRESOLVED"
    mature_hash = tev_history.sha256_sequence(mature_sequence) if mature_sequence else ""
    organism_name = _text(row.get("Organism"))

    return {
        "homolog_id": tev_history.stable_id(
            "hom", "UniProtKB", accession, source_release
        ),
        "accession": accession,
        "accession_version": "",
        "source_database": "UniProtKB",
        "source_release": source_release,
        "record_status": status,
        "taxonomy_id": int(_text(row.get("Organism (ID)"))) if _text(row.get("Organism (ID)")) else None,
        "virus_name": organism_name,
        "virus_strain": _extract_strain(organism_name),
        "host_text": _text(row.get("Virus hosts")),
        "geographic_origin": "",
        "taxonomic_lineage": _text(row.get("Taxonomic lineage")),
        "source_record_type": _source_record_type(
            source_length, len(mature_sequence), is_predicted, boundary is not None
        ),
        "is_predicted": is_predicted,
        "source_sequence": source_sequence,
        "source_sequence_sha256": tev_history.sha256_sequence(source_sequence),
        "source_sequence_length": source_length,
        "domain_start": mature_start,
        "domain_end": mature_end,
        "mature_sequence": mature_sequence,
        "mature_sequence_sha256": mature_hash,
        "mature_sequence_length": len(mature_sequence) if mature_sequence else None,
        "domain_boundary_method": boundary_method,
        "domain_completeness": completeness,
        "annotation_evidence": evidence,
        "duplicate_group_sha256": mature_hash,
        "duplicate_group_size": 0,
        "representative_homolog_id": "",
        "is_sequence_representative": False,
        "known_substrate_recognition": "",
        "experimental_catalysis_status": "UNKNOWN",
        "low_temperature_activity_status": "UNKNOWN",
        "quality_grade": quality,
        "include_in_qc_fasta": include,
        "exclusion_reason": exclusion_reason,
        "protein_existence": protein_existence,
        "annotation_score": annotation_score,
        "refseq_cross_reference": _text(row.get("RefSeq")),
        "embl_cross_reference": _text(row.get("EMBL")),
    }


def _representative_priority(record):
    return (
        1 if record.get("accession") == tev_history.CANONICAL_ACCESSION else 0,
        1 if record.get("record_status") == "REVIEWED" else 0,
        1 if record.get("domain_completeness") == "COMPLETE" else 0,
        float(record.get("annotation_score") or 0.0),
    )


def assign_sequence_representatives(records):
    """Mark one representative per exact mature-sequence hash without data loss."""
    groups = {}
    for record in records:
        record["is_sequence_representative"] = False
        record["representative_homolog_id"] = ""
        sequence_hash = record.get("mature_sequence_sha256")
        if record.get("include_in_qc_fasta") and sequence_hash:
            groups.setdefault(sequence_hash, []).append(record)

    for sequence_hash, group in groups.items():
        representative = sorted(
            group,
            key=lambda record: (
                -_representative_priority(record)[0],
                -_representative_priority(record)[1],
                -_representative_priority(record)[2],
                -_representative_priority(record)[3],
                record.get("accession", ""),
            ),
        )[0]
        representative["is_sequence_representative"] = True
        representative_id = representative.get("homolog_id") or representative["accession"]
        for record in group:
            record["duplicate_group_sha256"] = sequence_hash
            record["duplicate_group_size"] = len(group)
            record["representative_homolog_id"] = representative_id
    return records


def read_uniprot_tsv(path, source_release):
    """Read and curate a downloaded UniProt TSV candidate pool."""
    with open(path, "r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle, delimiter="\t")
        records = [curate_uniprot_record(row, source_release) for row in reader]
    return assign_sequence_representatives(records)


def write_metadata_csv(records, path):
    """Write candidate-level metadata, retaining included and excluded records."""
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=METADATA_FIELDS, extrasaction="ignore")
        writer.writeheader()
        for record in sorted(records, key=lambda item: item.get("accession", "")):
            writer.writerow({field: record.get(field, "") for field in METADATA_FIELDS})


def write_representative_fasta(records, path):
    """Write one exact-sequence representative per mature NIa-Pro duplicate group."""
    representatives = [
        record for record in records if record.get("is_sequence_representative")
    ]
    with open(path, "w", encoding="ascii", newline="\n") as handle:
        for record in sorted(representatives, key=lambda item: item["homolog_id"]):
            header = (
                ">{homolog_id}|accession={accession}|taxid={taxonomy_id}|"
                "status={record_status}|duplicates={duplicate_group_size}"
            ).format(**record)
            handle.write(header + "\n")
            sequence = record["mature_sequence"]
            for offset in range(0, len(sequence), 80):
                handle.write(sequence[offset:offset + 80] + "\n")
