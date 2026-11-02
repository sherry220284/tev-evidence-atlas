CREATE TABLE alignments (
    alignment_id TEXT PRIMARY KEY,
    alignment_role TEXT NOT NULL CHECK (
        alignment_role IN ('FULL_QC', 'REPRESENTATIVE', 'EXPLORATORY')
    ),
    fasta_path TEXT NOT NULL,
    sequence_count INTEGER NOT NULL,
    column_count INTEGER,
    method TEXT NOT NULL,
    method_version TEXT,
    parameters TEXT,
    input_sha256 TEXT NOT NULL,
    output_sha256 TEXT,
    qc_status TEXT NOT NULL CHECK (
        qc_status IN ('PLANNED', 'COMPLETED', 'FAILED', 'WITHHELD')
    ),
    source_id TEXT REFERENCES sources(source_id),
    notes TEXT
);

CREATE TABLE assay_protocols (
    protocol_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    protocol_name TEXT NOT NULL,
    assay_type TEXT NOT NULL,
    assay_temperature_c REAL,
    reaction_time_value REAL,
    reaction_time_unit TEXT,
    enzyme_concentration_value REAL,
    enzyme_concentration_unit TEXT,
    substrate_concentration_value REAL,
    substrate_concentration_unit TEXT,
    reaction_buffer TEXT,
    ph_value REAL,
    ph_measurement_temperature_c REAL,
    reducing_agent TEXT,
    detection_method TEXT,
    notes TEXT
);

CREATE TABLE audit_issues (
    issue_id TEXT PRIMARY KEY,
    severity TEXT NOT NULL CHECK (severity IN ('INFO', 'WARNING', 'ERROR', 'CRITICAL')),
    source_id TEXT REFERENCES sources(source_id),
    subject_table TEXT,
    subject_id TEXT,
    field_name TEXT NOT NULL,
    issue_type TEXT NOT NULL,
    issue_description TEXT NOT NULL,
    proposed_resolution TEXT NOT NULL,
    review_status TEXT NOT NULL CHECK (
        review_status IN ('OPEN', 'IN_REVIEW', 'RESOLVED', 'ACCEPTED_UNRESOLVED')
    ),
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at TEXT
, issue_class TEXT, classification_rationale TEXT, blocked_use TEXT, release_blocking INTEGER NOT NULL DEFAULT 0);

CREATE TABLE commercial_products (
    product_id TEXT PRIMARY KEY,
    vendor_name TEXT NOT NULL,
    product_name TEXT NOT NULL,
    catalog_number TEXT,
    positioning_claim TEXT,
    claimed_performance TEXT,
    temperature_conditions TEXT,
    ph_conditions TEXT,
    buffer_conditions TEXT,
    unit_definition TEXT,
    standard_substrate TEXT,
    cleavage_rate_claim TEXT,
    cleavage_time_claim TEXT,
    storage_stability TEXT,
    packaging TEXT,
    sequence_availability TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    source_locator TEXT NOT NULL,
    related_patent_text TEXT,
    patent_mapping_status TEXT NOT NULL DEFAULT 'NOT_ASSERTED',
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    notes TEXT,
    UNIQUE(vendor_name, product_name, catalog_number)
);

CREATE TABLE constructs (
    construct_id TEXT PRIMARY KEY,
    construct_name TEXT NOT NULL,
    variant_id TEXT NOT NULL REFERENCES variants(variant_id),
    construct_version INTEGER NOT NULL DEFAULT 1,
    expression_host TEXT,
    n_terminal_tag TEXT,
    c_terminal_tag TEXT,
    additional_sequence TEXT,
    mature_start INTEGER,
    mature_end INTEGER,
    full_sequence TEXT,
    sequence_sha256 TEXT,
    sequence_status TEXT NOT NULL CHECK (
        sequence_status IN ('COMPLETE', 'INCOMPLETE', 'CONFLICTING')
    ),
    provenance_source_id TEXT REFERENCES sources(source_id),
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    notes TEXT,
    UNIQUE(construct_name, construct_version)
);

CREATE TABLE evidence_links (
    evidence_link_id TEXT PRIMARY KEY,
    subject_table TEXT NOT NULL,
    subject_id TEXT NOT NULL,
    predicate TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    evidence_locator TEXT NOT NULL,
    quoted_text TEXT,
    extraction_method TEXT NOT NULL,
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    )
);

CREATE TABLE evolutionary_features (
    feature_id TEXT PRIMARY KEY,
    alignment_id TEXT NOT NULL REFERENCES alignments(alignment_id),
    alignment_column INTEGER,
    canonical_position INTEGER,
    feature_type TEXT NOT NULL,
    residue TEXT,
    numeric_value REAL,
    text_value TEXT,
    sequence_count INTEGER,
    effective_sequence_count REAL,
    calculation_method TEXT NOT NULL,
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    notes TEXT,
    CHECK (canonical_position IS NULL OR canonical_position BETWEEN 1 AND 242)
);

CREATE TABLE lineage_edges (
    edge_id TEXT PRIMARY KEY,
    parent_variant_id TEXT NOT NULL REFERENCES variants(variant_id),
    child_variant_id TEXT NOT NULL REFERENCES variants(variant_id),
    relationship_type TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    evidence_locator TEXT,
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    UNIQUE(parent_variant_id, child_variant_id, relationship_type, source_id)
);

CREATE TABLE measurements (
    measurement_id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL REFERENCES variants(variant_id),
    construct_id TEXT REFERENCES constructs(construct_id),
    substrate_id TEXT REFERENCES substrates(substrate_id),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    source_figure_table TEXT NOT NULL,
    protocol_id TEXT REFERENCES assay_protocols(protocol_id),
    assay_type TEXT NOT NULL,
    assay_temperature_c REAL,
    reaction_time_value REAL,
    reaction_time_unit TEXT,
    enzyme_concentration_value REAL,
    enzyme_concentration_unit TEXT,
    substrate_concentration_value REAL,
    substrate_concentration_unit TEXT,
    reaction_buffer TEXT,
    ph_value REAL,
    ph_measurement_temperature_c REAL,
    reducing_agent TEXT,
    measurement_name TEXT NOT NULL,
    raw_value_text TEXT NOT NULL,
    raw_value_numeric REAL,
    raw_unit TEXT,
    value_qualifier TEXT CHECK (
        value_qualifier IS NULL OR value_qualifier IN (
            'EXACT', 'ND', 'BELOW_DETECTION', 'OUT_OF_RANGE',
            'LOWER_BOUND', 'UPPER_BOUND', 'APPROXIMATE'
        )
    ),
    normalized_value REAL,
    normalized_unit TEXT,
    replicate_count INTEGER,
    uncertainty_value REAL,
    uncertainty_type TEXT,
    comparator_id TEXT REFERENCES variants(variant_id),
    evidence_quality TEXT NOT NULL CHECK (
        evidence_quality IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    extraction_method TEXT NOT NULL,
    future_training_ready INTEGER NOT NULL DEFAULT 0 CHECK (
        future_training_ready IN (0, 1)
    ),
    notes TEXT
);

CREATE TABLE msa_positions (
    alignment_id TEXT NOT NULL REFERENCES alignments(alignment_id),
    homolog_id TEXT NOT NULL REFERENCES natural_homologs(homolog_id),
    homolog_position INTEGER,
    alignment_column INTEGER NOT NULL,
    residue TEXT NOT NULL,
    canonical_position INTEGER,
    mapping_status TEXT NOT NULL CHECK (
        mapping_status IN ('VERIFIED', 'AMBIGUOUS', 'UNMAPPED', 'CONFLICT')
    ),
    mapping_method TEXT NOT NULL,
    PRIMARY KEY(alignment_id, homolog_id, alignment_column),
    CHECK (canonical_position IS NULL OR canonical_position BETWEEN 1 AND 242)
);

CREATE TABLE mutations (
    mutation_id TEXT PRIMARY KEY,
    variant_id TEXT NOT NULL REFERENCES variants(variant_id),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    source_notation TEXT NOT NULL,
    source_numbering_scheme TEXT NOT NULL,
    source_position INTEGER,
    canonical_position INTEGER,
    reference_residue TEXT,
    alternate_residue TEXT,
    mutation_type TEXT NOT NULL DEFAULT 'SUBSTITUTION',
    mapping_status TEXT NOT NULL CHECK (
        mapping_status IN ('VERIFIED', 'AMBIGUOUS', 'UNMAPPED', 'CONFLICT')
    ),
    mapping_method TEXT,
    notes TEXT,
    CHECK (canonical_position IS NULL OR canonical_position BETWEEN 1 AND 242)
);

CREATE TABLE natural_homologs (
    homolog_id TEXT PRIMARY KEY,
    accession TEXT NOT NULL,
    accession_version TEXT,
    source_database TEXT NOT NULL,
    source_release TEXT NOT NULL,
    record_status TEXT NOT NULL CHECK (
        record_status IN ('REVIEWED', 'UNREVIEWED', 'REFSEQ', 'OTHER')
    ),
    taxonomy_id INTEGER REFERENCES taxonomy(taxonomy_id),
    virus_name TEXT NOT NULL,
    virus_strain TEXT,
    host_text TEXT,
    geographic_origin TEXT,
    taxonomic_lineage TEXT,
    source_record_type TEXT NOT NULL CHECK (
        source_record_type IN (
            'MATURE_PROTEASE', 'FULL_POLYPROTEIN', 'POLYPROTEIN_FRAGMENT',
            'PREDICTED_PROTEIN', 'OTHER'
        )
    ),
    is_predicted INTEGER NOT NULL DEFAULT 0 CHECK (is_predicted IN (0, 1)),
    source_sequence TEXT NOT NULL,
    source_sequence_sha256 TEXT NOT NULL,
    source_sequence_length INTEGER NOT NULL,
    domain_start INTEGER,
    domain_end INTEGER,
    mature_sequence TEXT,
    mature_sequence_sha256 TEXT,
    mature_sequence_length INTEGER,
    domain_boundary_method TEXT,
    domain_completeness TEXT NOT NULL CHECK (
        domain_completeness IN ('COMPLETE', 'PARTIAL', 'AMBIGUOUS', 'UNRESOLVED')
    ),
    annotation_evidence TEXT,
    duplicate_group_sha256 TEXT,
    representative_homolog_id TEXT REFERENCES natural_homologs(homolog_id),
    is_sequence_representative INTEGER NOT NULL DEFAULT 0 CHECK (
        is_sequence_representative IN (0, 1)
    ),
    tev_pairwise_identity REAL,
    known_substrate_recognition TEXT,
    experimental_catalysis_status TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (
        experimental_catalysis_status IN ('CONFIRMED', 'INDIRECT', 'UNKNOWN', 'NOT_FOUND')
    ),
    low_temperature_activity_status TEXT NOT NULL DEFAULT 'UNKNOWN' CHECK (
        low_temperature_activity_status IN ('CONFIRMED', 'UNKNOWN', 'NOT_TESTED', 'CONFLICTING')
    ),
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    exclusion_reason TEXT,
    notes TEXT,
    UNIQUE(source_database, accession, accession_version)
);

CREATE TABLE phylogenetic_trees (
    tree_id TEXT PRIMARY KEY,
    alignment_id TEXT NOT NULL REFERENCES alignments(alignment_id),
    tree_role TEXT NOT NULL CHECK (tree_role IN ('FULL', 'REPRESENTATIVE')),
    newick_path TEXT NOT NULL,
    figure_path TEXT,
    inference_method TEXT NOT NULL,
    software_version TEXT,
    substitution_model TEXT,
    support_method TEXT,
    support_replicates INTEGER,
    rooting_method TEXT,
    recombination_screen_status TEXT NOT NULL,
    long_branch_review_status TEXT NOT NULL,
    tree_sha256 TEXT,
    analysis_status TEXT NOT NULL CHECK (
        analysis_status IN ('PLANNED', 'COMPLETED', 'FAILED', 'WITHHELD')
    ),
    source_id TEXT REFERENCES sources(source_id),
    notes TEXT
);

CREATE TABLE "references" (
    reference_id TEXT PRIMARY KEY,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    reference_type TEXT NOT NULL,
    title TEXT NOT NULL,
    authors TEXT,
    publication_year INTEGER,
    journal_or_authority TEXT,
    doi TEXT,
    pmid TEXT,
    pmcid TEXT,
    patent_number TEXT,
    patent_family_id TEXT,
    url TEXT,
    citation_status TEXT NOT NULL DEFAULT 'UNVERIFIED',
    UNIQUE(doi),
    UNIQUE(pmid),
    UNIQUE(patent_number)
);

CREATE TABLE residue_maps (
    residue_map_id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    source_numbering_scheme TEXT NOT NULL,
    source_position TEXT NOT NULL,
    source_residue TEXT,
    canonical_position INTEGER,
    canonical_residue TEXT,
    alignment_column INTEGER,
    mapping_status TEXT NOT NULL CHECK (
        mapping_status IN ('VERIFIED', 'AMBIGUOUS', 'UNMAPPED', 'CONFLICT')
    ),
    mapping_method TEXT NOT NULL,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    notes TEXT,
    CHECK (canonical_position IS NULL OR canonical_position BETWEEN 1 AND 242)
);

CREATE TABLE schema_metadata (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE source_aliases (alias_source_id TEXT PRIMARY KEY, canonical_source_id TEXT NOT NULL REFERENCES sources(source_id), reason TEXT NOT NULL);

CREATE TABLE sources (
    source_id TEXT PRIMARY KEY,
    source_type TEXT NOT NULL,
    title TEXT NOT NULL,
    uri TEXT,
    local_path TEXT,
    access_date TEXT NOT NULL,
    release_version TEXT,
    sha256 TEXT,
    is_raw INTEGER NOT NULL DEFAULT 1 CHECK (is_raw IN (0, 1)),
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    notes TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE structures (
    structure_id TEXT PRIMARY KEY,
    pdb_id TEXT,
    model_accession TEXT,
    evidence_class TEXT NOT NULL CHECK (
        evidence_class IN ('EXPERIMENTAL', 'PREDICTED', 'MD', 'HYPOTHESIS')
    ),
    variant_id TEXT REFERENCES variants(variant_id),
    construct_id TEXT REFERENCES constructs(construct_id),
    chain_id TEXT,
    experimental_method TEXT,
    resolution_angstrom REAL,
    mature_start INTEGER,
    mature_end INTEGER,
    source_id TEXT NOT NULL REFERENCES sources(source_id),
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    notes TEXT
);

CREATE TABLE substrates (
    substrate_id TEXT PRIMARY KEY,
    substrate_name TEXT NOT NULL,
    substrate_type TEXT NOT NULL,
    full_sequence TEXT,
    recognition_sequence TEXT,
    p1_residue TEXT,
    p1_prime_residue TEXT,
    cleavage_site_notation TEXT,
    source_id TEXT REFERENCES sources(source_id),
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    notes TEXT
);

CREATE TABLE taxonomy (
    taxonomy_id INTEGER PRIMARY KEY,
    scientific_name TEXT NOT NULL,
    common_name TEXT,
    rank TEXT,
    parent_taxonomy_id INTEGER REFERENCES taxonomy(taxonomy_id),
    lineage_text TEXT,
    taxonomy_source TEXT NOT NULL DEFAULT 'NCBI Taxonomy',
    source_release TEXT,
    source_id TEXT REFERENCES sources(source_id)
);

CREATE TABLE variants (
    variant_id TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL UNIQUE,
    variant_class TEXT NOT NULL CHECK (
        variant_class IN ('REFERENCE', 'ENGINEERED', 'HISTORICAL_UNKNOWN')
    ),
    alias_text TEXT,
    parent_variant_id TEXT REFERENCES variants(variant_id),
    mutation_definition_complete INTEGER NOT NULL DEFAULT 0 CHECK (
        mutation_definition_complete IN (0, 1)
    ),
    sequence_status TEXT NOT NULL CHECK (
        sequence_status IN ('COMPLETE', 'INCOMPLETE', 'CONFLICTING')
    ),
    mature_sequence TEXT,
    sequence_sha256 TEXT,
    sequence_length INTEGER,
    provenance_source_id TEXT REFERENCES sources(source_id),
    quality_grade TEXT NOT NULL CHECK (
        quality_grade IN ('VERIFIED', 'PARTIAL', 'INFERRED', 'UNRESOLVED')
    ),
    notes TEXT,
    CHECK (variant_class <> 'ENGINEERED' OR canonical_name <> '')
);

CREATE INDEX idx_evolutionary_features_position
    ON evolutionary_features(canonical_position);

CREATE INDEX idx_homologs_sequence_hash
    ON natural_homologs(mature_sequence_sha256);

CREATE INDEX idx_measurements_temperature
    ON measurements(assay_temperature_c);

CREATE INDEX idx_measurements_variant
    ON measurements(variant_id);

CREATE INDEX idx_msa_canonical_position
    ON msa_positions(canonical_position);

CREATE INDEX idx_mutations_canonical_position
    ON mutations(canonical_position);

CREATE VIEW literature_audit AS
 SELECT r.*, s.local_path, s.sha256, s.access_date,
        (SELECT count(*) FROM measurements m WHERE m.source_id=r.source_id) AS measurement_count,
        (SELECT count(*) FROM audit_issues a WHERE a.source_id=r.source_id
          AND a.review_status<>'RESOLVED') AS unresolved_issue_count
 FROM "references" r JOIN sources s USING(source_id);

CREATE VIEW measurement_trace AS
 SELECT m.*, v.canonical_name, v.sequence_status, c.construct_name,
        p.protocol_name, p.detection_method, p.notes AS protocol_notes,
        (SELECT group_concat(u.source_notation, '; ') FROM mutations u
          WHERE u.variant_id=m.variant_id) AS source_mutations,
        (SELECT group_concat(u.mapping_status, '; ') FROM mutations u
          WHERE u.variant_id=m.variant_id) AS mutation_mapping_status,
        (SELECT group_concat(DISTINCT rm.mapping_method) FROM residue_maps rm
          JOIN mutations u ON rm.entity_type='mutation' AND rm.entity_id=u.mutation_id
          WHERE u.variant_id=m.variant_id) AS mapping_basis,
        s.local_path, s.sha256, s.uri AS source_url,
        e.source_id AS evidence_source_id, es.local_path AS evidence_local_path,
        es.sha256 AS evidence_sha256, e.evidence_locator, e.quoted_text
 FROM measurements m JOIN variants v USING(variant_id)
 JOIN sources s ON m.source_id=s.source_id
 JOIN constructs c USING(construct_id)
 JOIN assay_protocols p USING(protocol_id)
 JOIN evidence_links e ON e.subject_table='measurements'
  AND e.subject_id=m.measurement_id AND e.predicate='PRIMARY_VALUE'
 JOIN sources es ON e.source_id=es.source_id;

CREATE VIEW training_ready AS SELECT * FROM measurement_trace WHERE future_training_ready=1;

CREATE VIEW unresolved_issues AS SELECT * FROM audit_issues WHERE review_status<>'RESOLVED';
