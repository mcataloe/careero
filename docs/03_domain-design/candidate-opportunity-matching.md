# Candidate-Opportunity Matching and Extraction Strategy

Status: Active  
Doc Type: Domain Design  
Layer: Layers 2, 7, 10, 14  
Source of Truth: Yes  
Last Reviewed: 2026-09-28  
Related Docs:
- docs/01_strategy/00_product-strategy.md
- docs/03_domain-design/opportunity-model.md
- docs/04_ai-and-compass/ai-usage-cost-controls.md
- docs/02_layers/14_layer-14-model-catalog-and-prompt-management.md

## Purpose

This document defines the architecture for comparing candidate evidence with opportunity requirements in a performant, accurate, explainable, and cost-bounded way.

Careero should not treat a resume and a job description as two opaque documents and ask a large language model to judge them end-to-end for every comparison. Instead, both sides should be normalized into shared structured concepts once, then matched through a staged cascade that escalates only when cheaper methods cannot resolve the relationship.

The same matching engine must support both directions:

- candidate -> opportunities: find roles supported by the candidate's demonstrated evidence;
- opportunity -> candidates: find candidates whose evidence supports the opportunity's requirements.

## Core Principle

Use the cheapest sufficiently reliable method first.

The matching cascade is:

1. hard constraints;
2. lexical and title retrieval;
3. canonical capability matching;
4. relationship/graph inference;
5. semantic matching;
6. LLM adjudication for unresolved ambiguity.

The system should prefer deterministic and precomputed evidence over repeated generative inference.

## Normalized Inputs

### Candidate side

Candidate source material may include:

- resumes and resume versions;
- profile data;
- employment history;
- projects;
- accomplishments;
- education;
- certifications;
- portfolio artifacts;
- user-entered evidence;
- later, verified or externally corroborated evidence.

Candidate source material should normalize into:

- titles and role families;
- employers and organizations;
- dates and durations;
- technologies;
- skills and capabilities;
- domains;
- responsibilities;
- accomplishments;
- leadership and scope signals;
- credentials;
- preferences and constraints;
- evidence/provenance links.

### Opportunity side

Opportunity source material may include:

- title;
- job description;
- required qualifications;
- preferred or nice-to-have qualifications;
- responsibilities;
- technologies;
- domain;
- experience/seniority expectations;
- compensation;
- location and work arrangement;
- employment type;
- eligibility constraints;
- source/provenance.

Opportunity text should normalize into requirement records that preserve whether each item is required, preferred, descriptive, or ambiguous.

## Shared Capability Model

Candidate evidence and opportunity requirements should resolve toward shared canonical concepts rather than relying on raw string equality.

Examples:

- "Postgres", "PostgreSQL", and "RDS PostgreSQL" may resolve to canonical PostgreSQL concepts while retaining source wording.
- ".NET 8", ".NET Core", and "ASP.NET Core" may map to related but distinct canonical concepts.
- "SQS FIFO" may relate to message queues and asynchronous messaging without being falsely treated as Kafka experience.

A normalized capability should preserve:

- canonical identifier;
- canonical display name;
- type/category;
- aliases;
- parent/child or related concepts where appropriate;
- provenance for how the concept was inferred;
- confidence;
- version of the taxonomy/resolver used.

## Matching Cascade

### Stage 0 - Hard Constraints

Apply cheap deterministic filters before relevance scoring when the data exists.

Examples:

- geographic eligibility;
- remote/hybrid/onsite constraints;
- compensation thresholds;
- employment type;
- work authorization or clearance when explicitly required;
- user-declared exclusions.

Hard constraints must remain distinct from capability fit.

### Stage 1 - Lexical and Title Retrieval

Use inexpensive retrieval to reduce the candidate set.

Techniques may include:

- exact/normalized title matching;
- title-family lookup;
- keyword matching;
- database full-text search;
- BM25-style lexical retrieval.

Title matching is a retrieval hint, not a qualification decision. A title mismatch must not automatically discard an opportunity when the duties and capability requirements remain plausibly aligned.

### Stage 2 - Canonical Capability Matching

Resolve aliases and normalized concepts, then use direct joins where possible.

Examples:

- AWS -> AWS;
- PostgreSQL -> PostgreSQL;
- RESTful API -> REST API concept;
- Certified credential -> corresponding credential concept.

This stage should handle the largest share of ordinary matching at database cost.

### Stage 3 - Relationship / Graph Inference

Use stored relationships between concepts and evidence to infer support without invoking a generative model.

Examples:

- SQS FIFO -> is a -> message queue;
- message queue -> supports -> asynchronous messaging;
- idempotency -> reliability pattern for -> distributed systems.

Relationship inference must not overstate equivalence. Adjacent technology experience may support a partial or inferred match without becoming an exact match.

For the rapid prototype, graph-shaped data should remain relational in PostgreSQL unless traversal complexity demonstrates a concrete need for a dedicated graph database.

### Stage 4 - Semantic Matching

Use embeddings or another semantic retrieval model only for unresolved natural-language relationships.

Semantic matching should operate on small evidence/requirement units rather than entire resumes and job descriptions whenever practical.

Examples:

- requirement: "reduce coupling between critical services";
- evidence: "introduced a queue-backed worker that separated request handling from downstream processing."

Semantic similarity produces candidate evidence for adjudication; it does not by itself prove qualification.

### Stage 5 - LLM Adjudication

Use an LLM only when deterministic, canonical, graph, and semantic stages cannot resolve a material ambiguity.

The adjudicator should receive the smallest useful context:

- one requirement or tightly related requirement set;
- candidate evidence that survived retrieval;
- provenance;
- applicable matching rules.

It should not receive an entire resume and entire job description unless the task genuinely requires document-level reasoning.

## Match Types

Careero should distinguish the nature of support rather than reducing every comparison to a single opaque percentage.

Recommended match types:

- EXACT;
- EQUIVALENT;
- INFERRED;
- SEMANTIC;
- PARTIAL;
- UNSUPPORTED;
- UNKNOWN.

Each match should be able to carry:

- confidence;
- evidence references;
- provenance;
- matching stage/method;
- explanation suitable for user review;
- parser/model/ruleset version.

A weighted aggregate score may exist for ranking, but it must not replace evidence-level explanations.

## Evidence Invariant

Every positive candidate qualification claim should be traceable to source evidence.

Conceptually:

Opportunity Requirement
-> Matched Capability
-> Candidate Evidence
-> Project / Position / Credential / Artifact
-> Original Source

The system must distinguish direct evidence from inferred adjacency. It must not transform related experience into experience the candidate did not claim.

## Extraction Pipeline

Candidate and opportunity parsing should also use an escalation cascade.

1. Native document/text extraction.
2. Deterministic extraction for easy structured fields.
3. Lightweight entity or schema extraction.
4. Canonicalization/taxonomy linking.
5. Larger structured-extraction or language model only for ambiguous fields.
6. Human review when confidence or trust thresholds require it.

Examples of fields that should generally avoid an LLM when structured parsing is sufficient:

- email;
- phone;
- URLs;
- explicit dates;
- explicit compensation ranges;
- explicit location;
- recognizable headings.

Model-based extraction is most useful for:

- required versus preferred qualification classification;
- responsibility extraction;
- accomplishment/evidence segmentation;
- scope and seniority signals;
- capability extraction from prose;
- relationship candidates between evidence and capability concepts;
- ambiguous section interpretation.

## Performance and Cost Strategy

Normalize source material once and reuse it.

Candidate profiles should be reparsed only when source evidence changes or the extraction/taxonomy version requires migration.

Opportunity profiles should be parsed at ingestion and reused for subsequent candidate comparisons.

Precompute when practical:

- normalized titles;
- canonical capability IDs;
- evidence-to-capability links;
- requirement-to-capability links;
- embeddings for unresolved evidence/requirement units;
- source hashes;
- parser/taxonomy/model versions.

Cache reusable results by stable source hash plus parser/model/ruleset version.

The desired shape is:

large corpus
-> hard/lexical retrieval
-> canonical matching
-> graph inference
-> small semantic candidate set
-> very small LLM adjudication set.

## Storage Posture

For the current Careero rapid prototype:

- PostgreSQL remains the canonical persistence layer.
- Graph relationships should initially use relational tables/edges.
- pgvector or an equivalent PostgreSQL-compatible vector extension may support semantic retrieval when implementation reaches that stage.
- A dedicated graph database is not justified until measured query/traversal requirements exceed the relational model.
- A dedicated vector database is not justified until scale or operational evidence shows PostgreSQL vector search is insufficient.

Possible conceptual records include:

- Capability;
- CapabilityAlias;
- CapabilityRelationship;
- CandidateEvidence;
- CandidateEvidenceCapability;
- OpportunityRequirement;
- OpportunityRequirementCapability;
- MatchEvidence;
- MatchResult.

These are conceptual boundaries, not an approved migration or implementation schema.

## Model Strategy

The matching architecture must remain model-agnostic.

Open-source models may be used for:

- named-entity extraction;
- structured JSON extraction;
- skill/capability linking;
- embeddings;
- ambiguous relation classification.

Model selection should be benchmark-driven against Careero's schema and data, not chosen by popularity alone.

Careero should prefer adapting or fine-tuning a capable pretrained model over training a language model from scratch unless later evidence shows that pretrained representations are fundamentally unsuitable.

Any fine-tuned model should remain replaceable behind the Layer 14 model/provider boundary.

## Evaluation Requirements

Before replacing one stage with a model-based approach, measure it against a labeled Careero evaluation set.

At minimum, evaluate:

- field-level precision;
- field-level recall;
- required-vs-preferred classification;
- canonical capability linking accuracy;
- false qualification rate;
- false rejection rate;
- evidence/provenance correctness;
- latency;
- throughput;
- compute/API cost per parsed document;
- cost per accepted match;
- behavior on ambiguous and adversarial wording.

For candidate qualification, false positive qualification claims are a higher trust risk than leaving an ambiguous requirement unresolved.

## Non-Goals

This strategy does not:

- approve Neo4j, Neptune, or another dedicated graph database;
- approve a dedicated vector database;
- select a production model;
- define a destructive schema migration;
- authorize employer-side marketplace behavior;
- remove human review or TruthGuard boundaries;
- treat semantic similarity as proof of qualification.

## Implementation Gate

This document defines the architecture and evaluation posture only.

Before implementation of a new matching subsystem:

- inspect current Layer 2 parsing and COMPASS behavior;
- define the minimum shared capability/requirement contract;
- create a representative labeled evaluation set;
- benchmark deterministic extraction and at least one lightweight model path;
- confirm schema and migration impact;
- use the lightest LEAP workflow appropriate to the resulting blast radius.

Gate decision: architecture direction approved for documentation; implementation remains gated on measured parser/matcher evaluation and current-repo reconciliation.
