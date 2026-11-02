# TEV dual-atlas data dictionary

SQLite is authoritative after rebuilding from `data/schema.sql` and `data/tables/*.csv`. In this repository CSV `\\N` represents SQL NULL; an empty cell is an empty string, never zero. All 22 tables retain their primary-key fields. Parquet exports from the earlier workspace are not part of this repository.

Historical measurements remain source scoped. Raw text, units, bounds, unknown uncertainty, constructs, protocols and original locators are retained. Unit conversion does not remove a qualifier. A COMPLETE mature sequence may be truncated; consult sequence evidence and construct boundaries. Mutation mapping VERIFIED means positional mapping, not phenotypic validation.

Natural divergence never enters variants/mutations. 1,505 candidates include excluded records; only 35 exact-boundary unique domains enter MSA. Catalysis and low-temperature UNKNOWN mean no experimentally verified evidence curated for these candidates, not experimental inactivity.

Structures are experimental coordinate entities and are not automatically assigned to historical variants. All training eligibility flags are zero. Commercial products has one separately curated P8118 vendor-specification record. VERIFIED there denotes document/claim identity, not independent catalytic validation or patent sequence identity.

## Entity and field conventions

| Entity group | Meaning and joins |
|---|---|
| `sources`, `references`, `evidence_links` | File/document identity, bibliographic references and record-to-source locators; a source row is not necessarily a paper |
| `variants`, `constructs`, `mutations`, `lineage_edges` | Source-scoped engineered variant, assayed construct, original/mapped substitutions and documented parentage; natural divergence is excluded |
| `measurements`, `substrates`, `assay_protocols` | One reported value/qualifier under one protocol and substrate; fit alternatives retain common-data provenance |
| `commercial_products` | Explicit vendor claims with source/locator and unresolved patent/sequence mapping; separate from paper measurement rows |
| `audit_issues` | Severity, disputed field, original issue, proposed resolution and review state; unresolved issues remain visible |
| `natural_homologs`, `taxonomy` | Full candidate inventory and taxonomy; `qc_status`/domain fields identify the 35 analyzed mature domains |
| `alignments`, `msa_positions`, `phylogenetic_trees`, `evolutionary_features` | Alignment identity, sequence/MSA/canonical mapping, real inferred trees, and recomputable site features |
| `structures`, `residue_maps` | Experimental PDB entity and positional mapping; source residue may differ from canonical residue |
| `source_aliases`, `schema_metadata` | Explicit source-ID consolidation and schema/release provenance |

`*_id` fields join their same-named primary keys; `source_id` joins `sources`. Sequence positions, alignment columns and canonical positions are 1-based. Canonical mature TEV spans 1–242. `source_position` preserves original numbering; missing canonical mapping stays NULL. Units remain in the accompanying `*_unit` field. `value_qualifier` distinguishes exact values, bounds, ND and source-specific reported quantities; NULL is missing, never zero or inactive. `quality_grade` is VERIFIED/PARTIAL/INFERRED/UNRESOLVED and refers to the stated evidence class. `notes` retain qualifications, backgrounds, source conflicts and interpretation limits. `sequence_count` and `effective_sequence_count` distinguish raw observations from weighting. SHA-256 identifies exact file bytes.

The per-field `Required` column below reports the frozen SQLite NOT NULL flag; a primary-key field may show `no` under SQLite's historical table syntax but is still a required identifier in curation. Foreign-key constraints and exact CREATE statements are in `data/schema.sql` and checked during every rebuild.

## alignments

| Field | Type | Required |
|---|---|---|
| alignment_id | TEXT | no |
| alignment_role | TEXT | yes |
| fasta_path | TEXT | yes |
| sequence_count | INTEGER | yes |
| column_count | INTEGER | no |
| method | TEXT | yes |
| method_version | TEXT | no |
| parameters | TEXT | no |
| input_sha256 | TEXT | yes |
| output_sha256 | TEXT | no |
| qc_status | TEXT | yes |
| source_id | TEXT | no |
| notes | TEXT | no |

## assay_protocols

| Field | Type | Required |
|---|---|---|
| protocol_id | TEXT | no |
| source_id | TEXT | yes |
| protocol_name | TEXT | yes |
| assay_type | TEXT | yes |
| assay_temperature_c | REAL | no |
| reaction_time_value | REAL | no |
| reaction_time_unit | TEXT | no |
| enzyme_concentration_value | REAL | no |
| enzyme_concentration_unit | TEXT | no |
| substrate_concentration_value | REAL | no |
| substrate_concentration_unit | TEXT | no |
| reaction_buffer | TEXT | no |
| ph_value | REAL | no |
| ph_measurement_temperature_c | REAL | no |
| reducing_agent | TEXT | no |
| detection_method | TEXT | no |
| notes | TEXT | no |

## audit_issues

| Field | Type | Required |
|---|---|---|
| issue_id | TEXT | no |
| severity | TEXT | yes |
| source_id | TEXT | no |
| subject_table | TEXT | no |
| subject_id | TEXT | no |
| field_name | TEXT | yes |
| issue_type | TEXT | yes |
| issue_description | TEXT | yes |
| proposed_resolution | TEXT | yes |
| review_status | TEXT | yes |
| created_at | TEXT | yes |
| resolved_at | TEXT | no |
| issue_class | TEXT | no |
| classification_rationale | TEXT | no |
| blocked_use | TEXT | no |
| release_blocking | INTEGER | yes |

## commercial_products

| Field | Type | Required |
|---|---|---|
| product_id | TEXT | no |
| vendor_name | TEXT | yes |
| product_name | TEXT | yes |
| catalog_number | TEXT | no |
| positioning_claim | TEXT | no |
| claimed_performance | TEXT | no |
| temperature_conditions | TEXT | no |
| ph_conditions | TEXT | no |
| buffer_conditions | TEXT | no |
| unit_definition | TEXT | no |
| standard_substrate | TEXT | no |
| cleavage_rate_claim | TEXT | no |
| cleavage_time_claim | TEXT | no |
| storage_stability | TEXT | no |
| packaging | TEXT | no |
| sequence_availability | TEXT | yes |
| source_id | TEXT | yes |
| source_locator | TEXT | yes |
| related_patent_text | TEXT | no |
| patent_mapping_status | TEXT | yes |
| quality_grade | TEXT | yes |
| notes | TEXT | no |

## constructs

| Field | Type | Required |
|---|---|---|
| construct_id | TEXT | no |
| construct_name | TEXT | yes |
| variant_id | TEXT | yes |
| construct_version | INTEGER | yes |
| expression_host | TEXT | no |
| n_terminal_tag | TEXT | no |
| c_terminal_tag | TEXT | no |
| additional_sequence | TEXT | no |
| mature_start | INTEGER | no |
| mature_end | INTEGER | no |
| full_sequence | TEXT | no |
| sequence_sha256 | TEXT | no |
| sequence_status | TEXT | yes |
| provenance_source_id | TEXT | no |
| quality_grade | TEXT | yes |
| notes | TEXT | no |

## evidence_links

| Field | Type | Required |
|---|---|---|
| evidence_link_id | TEXT | no |
| subject_table | TEXT | yes |
| subject_id | TEXT | yes |
| predicate | TEXT | yes |
| source_id | TEXT | yes |
| evidence_locator | TEXT | yes |
| quoted_text | TEXT | no |
| extraction_method | TEXT | yes |
| quality_grade | TEXT | yes |

## evolutionary_features

| Field | Type | Required |
|---|---|---|
| feature_id | TEXT | no |
| alignment_id | TEXT | yes |
| alignment_column | INTEGER | no |
| canonical_position | INTEGER | no |
| feature_type | TEXT | yes |
| residue | TEXT | no |
| numeric_value | REAL | no |
| text_value | TEXT | no |
| sequence_count | INTEGER | no |
| effective_sequence_count | REAL | no |
| calculation_method | TEXT | yes |
| quality_grade | TEXT | yes |
| notes | TEXT | no |

## lineage_edges

| Field | Type | Required |
|---|---|---|
| edge_id | TEXT | no |
| parent_variant_id | TEXT | yes |
| child_variant_id | TEXT | yes |
| relationship_type | TEXT | yes |
| source_id | TEXT | yes |
| evidence_locator | TEXT | no |
| quality_grade | TEXT | yes |

## measurements

| Field | Type | Required |
|---|---|---|
| measurement_id | TEXT | no |
| variant_id | TEXT | yes |
| construct_id | TEXT | no |
| substrate_id | TEXT | no |
| source_id | TEXT | yes |
| source_figure_table | TEXT | yes |
| protocol_id | TEXT | no |
| assay_type | TEXT | yes |
| assay_temperature_c | REAL | no |
| reaction_time_value | REAL | no |
| reaction_time_unit | TEXT | no |
| enzyme_concentration_value | REAL | no |
| enzyme_concentration_unit | TEXT | no |
| substrate_concentration_value | REAL | no |
| substrate_concentration_unit | TEXT | no |
| reaction_buffer | TEXT | no |
| ph_value | REAL | no |
| ph_measurement_temperature_c | REAL | no |
| reducing_agent | TEXT | no |
| measurement_name | TEXT | yes |
| raw_value_text | TEXT | yes |
| raw_value_numeric | REAL | no |
| raw_unit | TEXT | no |
| value_qualifier | TEXT | no |
| normalized_value | REAL | no |
| normalized_unit | TEXT | no |
| replicate_count | INTEGER | no |
| uncertainty_value | REAL | no |
| uncertainty_type | TEXT | no |
| comparator_id | TEXT | no |
| evidence_quality | TEXT | yes |
| extraction_method | TEXT | yes |
| future_training_ready | INTEGER | yes |
| notes | TEXT | no |

## msa_positions

| Field | Type | Required |
|---|---|---|
| alignment_id | TEXT | yes |
| homolog_id | TEXT | yes |
| homolog_position | INTEGER | no |
| alignment_column | INTEGER | yes |
| residue | TEXT | yes |
| canonical_position | INTEGER | no |
| mapping_status | TEXT | yes |
| mapping_method | TEXT | yes |

## mutations

| Field | Type | Required |
|---|---|---|
| mutation_id | TEXT | no |
| variant_id | TEXT | yes |
| source_id | TEXT | yes |
| source_notation | TEXT | yes |
| source_numbering_scheme | TEXT | yes |
| source_position | INTEGER | no |
| canonical_position | INTEGER | no |
| reference_residue | TEXT | no |
| alternate_residue | TEXT | no |
| mutation_type | TEXT | yes |
| mapping_status | TEXT | yes |
| mapping_method | TEXT | no |
| notes | TEXT | no |

## natural_homologs

| Field | Type | Required |
|---|---|---|
| homolog_id | TEXT | no |
| accession | TEXT | yes |
| accession_version | TEXT | no |
| source_database | TEXT | yes |
| source_release | TEXT | yes |
| record_status | TEXT | yes |
| taxonomy_id | INTEGER | no |
| virus_name | TEXT | yes |
| virus_strain | TEXT | no |
| host_text | TEXT | no |
| geographic_origin | TEXT | no |
| taxonomic_lineage | TEXT | no |
| source_record_type | TEXT | yes |
| is_predicted | INTEGER | yes |
| source_sequence | TEXT | yes |
| source_sequence_sha256 | TEXT | yes |
| source_sequence_length | INTEGER | yes |
| domain_start | INTEGER | no |
| domain_end | INTEGER | no |
| mature_sequence | TEXT | no |
| mature_sequence_sha256 | TEXT | no |
| mature_sequence_length | INTEGER | no |
| domain_boundary_method | TEXT | no |
| domain_completeness | TEXT | yes |
| annotation_evidence | TEXT | no |
| duplicate_group_sha256 | TEXT | no |
| representative_homolog_id | TEXT | no |
| is_sequence_representative | INTEGER | yes |
| tev_pairwise_identity | REAL | no |
| known_substrate_recognition | TEXT | no |
| experimental_catalysis_status | TEXT | yes |
| low_temperature_activity_status | TEXT | yes |
| source_id | TEXT | yes |
| quality_grade | TEXT | yes |
| exclusion_reason | TEXT | no |
| notes | TEXT | no |

## phylogenetic_trees

| Field | Type | Required |
|---|---|---|
| tree_id | TEXT | no |
| alignment_id | TEXT | yes |
| tree_role | TEXT | yes |
| newick_path | TEXT | yes |
| figure_path | TEXT | no |
| inference_method | TEXT | yes |
| software_version | TEXT | no |
| substitution_model | TEXT | no |
| support_method | TEXT | no |
| support_replicates | INTEGER | no |
| rooting_method | TEXT | no |
| recombination_screen_status | TEXT | yes |
| long_branch_review_status | TEXT | yes |
| tree_sha256 | TEXT | no |
| analysis_status | TEXT | yes |
| source_id | TEXT | no |
| notes | TEXT | no |

## references

| Field | Type | Required |
|---|---|---|
| reference_id | TEXT | no |
| source_id | TEXT | yes |
| reference_type | TEXT | yes |
| title | TEXT | yes |
| authors | TEXT | no |
| publication_year | INTEGER | no |
| journal_or_authority | TEXT | no |
| doi | TEXT | no |
| pmid | TEXT | no |
| pmcid | TEXT | no |
| patent_number | TEXT | no |
| patent_family_id | TEXT | no |
| url | TEXT | no |
| citation_status | TEXT | yes |

## residue_maps

| Field | Type | Required |
|---|---|---|
| residue_map_id | TEXT | no |
| entity_type | TEXT | yes |
| entity_id | TEXT | yes |
| source_numbering_scheme | TEXT | yes |
| source_position | TEXT | yes |
| source_residue | TEXT | no |
| canonical_position | INTEGER | no |
| canonical_residue | TEXT | no |
| alignment_column | INTEGER | no |
| mapping_status | TEXT | yes |
| mapping_method | TEXT | yes |
| source_id | TEXT | yes |
| notes | TEXT | no |

## schema_metadata

| Field | Type | Required |
|---|---|---|
| key | TEXT | no |
| value | TEXT | yes |

## source_aliases

| Field | Type | Required |
|---|---|---|
| alias_source_id | TEXT | no |
| canonical_source_id | TEXT | yes |
| reason | TEXT | yes |

## sources

| Field | Type | Required |
|---|---|---|
| source_id | TEXT | no |
| source_type | TEXT | yes |
| title | TEXT | yes |
| uri | TEXT | no |
| local_path | TEXT | no |
| access_date | TEXT | yes |
| release_version | TEXT | no |
| sha256 | TEXT | no |
| is_raw | INTEGER | yes |
| quality_grade | TEXT | yes |
| notes | TEXT | no |
| created_at | TEXT | yes |

## structures

| Field | Type | Required |
|---|---|---|
| structure_id | TEXT | no |
| pdb_id | TEXT | no |
| model_accession | TEXT | no |
| evidence_class | TEXT | yes |
| variant_id | TEXT | no |
| construct_id | TEXT | no |
| chain_id | TEXT | no |
| experimental_method | TEXT | no |
| resolution_angstrom | REAL | no |
| mature_start | INTEGER | no |
| mature_end | INTEGER | no |
| source_id | TEXT | yes |
| quality_grade | TEXT | yes |
| notes | TEXT | no |

## substrates

| Field | Type | Required |
|---|---|---|
| substrate_id | TEXT | no |
| substrate_name | TEXT | yes |
| substrate_type | TEXT | yes |
| full_sequence | TEXT | no |
| recognition_sequence | TEXT | no |
| p1_residue | TEXT | no |
| p1_prime_residue | TEXT | no |
| cleavage_site_notation | TEXT | no |
| source_id | TEXT | no |
| quality_grade | TEXT | yes |
| notes | TEXT | no |

## taxonomy

| Field | Type | Required |
|---|---|---|
| taxonomy_id | INTEGER | no |
| scientific_name | TEXT | yes |
| common_name | TEXT | no |
| rank | TEXT | no |
| parent_taxonomy_id | INTEGER | no |
| lineage_text | TEXT | no |
| taxonomy_source | TEXT | yes |
| source_release | TEXT | no |
| source_id | TEXT | no |

## variants

| Field | Type | Required |
|---|---|---|
| variant_id | TEXT | no |
| canonical_name | TEXT | yes |
| variant_class | TEXT | yes |
| alias_text | TEXT | no |
| parent_variant_id | TEXT | no |
| mutation_definition_complete | INTEGER | yes |
| sequence_status | TEXT | yes |
| mature_sequence | TEXT | no |
| sequence_sha256 | TEXT | no |
| sequence_length | INTEGER | no |
| provenance_source_id | TEXT | no |
| quality_grade | TEXT | yes |
| notes | TEXT | no |
