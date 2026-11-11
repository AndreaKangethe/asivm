# ASIVM real-data ML migration: Milestone 1

## Scope

Milestone 1 defines the combined asset-risk contract. It does not ingest public feeds, build training rows, train models, or promote a real model. NVD, CISA KEV, and FIRST EPSS remain vulnerability-intelligence inputs; they do not supply asset risk labels.

## v3 feature contract

`FEATURE_VERSION_V3 = "v3"` is immutable. The vector order is:

1. `kev_count`
2. `epss_max`
3. `asset_age_days`
4. `observation_change_count`
5. `cvss_max`
6. `vulnerability_count`
7. `critical_vulnerability_count`
8. `open_port_count`
9. `new_port_count`
10. `service_count`
11. `new_service_count`
12. `ip_change_count`
13. `hostname_change_count`
14. `vulnerability_change_count`
15. `asset_criticality_score`
16. `business_impact_score`
17. `internet_exposed`
18. `externally_reachable_port_count`
19. `externally_reachable_service_count`
20. `identity_confidence`

The first fourteen values preserve the intended v2 vulnerability and behavior signals. The final six require asset-owner or observation evidence. `asset_criticality_score` and `business_impact_score` must retain their source and meaning; no universal thresholds are defined in this milestone. Missing values are represented consistently by the feature builder and must be recorded in row provenance.

v1 remains the existing four-feature contract. Existing v2 artifacts are not rewritten or migrated by this change.

## Analyst risk-label policy

The supervised target is an expert-reviewed assessment of the asset at a specific observation timestamp:

- `LOW = 0`
- `MEDIUM = 1`
- `HIGH = 2`

A label must reference an `AssetObservation`, include the asset and observation identifiers, reviewer identity, assessment timestamp, label version, and a written justification. `label_source` is `expert_review` for the initial policy. Labels are not generated from CVSS, KEV, EPSS, anomaly status, or model scores. Those values may inform a reviewer but cannot be ground truth.

The project still needs an approved reviewer rubric defining what evidence qualifies for LOW, MEDIUM, and HIGH. Until that rubric exists, no real labels should be imported or inferred.

## Historical training row

Each persisted row contains:

- dataset version and deterministic row hash;
- asset ID and observation ID/timestamp;
- immutable feature version and named feature values;
- asset-vulnerability relationship evidence as-of the observation;
- vulnerability-intelligence provenance, including source, source-effective timestamp, retrieval timestamp, and record/feed version;
- the referenced expert risk label.

Rows must be reproducible from information available at the prediction timestamp. Mutable current relationships are insufficient for historical reconstruction.

## Temporal and leakage rules

For prediction time `T`, features may use only observations and intelligence effective or retrieved at or before `T`. Labels are assessed at or after `T` and are never features. Future KEV membership, later EPSS scores, revised CVSS values, future asset-vulnerability links, remediation status, and future outcomes must be excluded from the feature row. Train, validation, and test partitions are chronological; repeated observations from the same asset or asset group must not cross partitions where that would leak near-duplicate state.

## Future exploitation outcomes

`ExploitationOutcome` is separate from `RiskLabel`. It records independently verified outcomes, including outcome type, occurrence time, verification time, verifier, source, and evidence. Outcomes are used for later label-quality and prospective evaluation work; they do not overwrite analyst labels.

## Evaluation and promotion

Real v3 models start in shadow mode. A candidate must record dataset version/hash, feature contract, label version, cutoff dates, provenance summary, algorithm parameters, and metrics. Evaluation must include class prevalence, coverage, missingness, confusion matrix, per-class precision/recall, macro and weighted F1, PR-AUC where applicable, calibration, and comparison with simple baselines. Asset-grouped chronological holdout performance is required before promotion. Promotion must be explicit, reversible, and must leave synthetic fallback artifacts and historical v1/v2 interpretation available.

## Milestone 2 checklist

- Implement versioned NVD, KEV, and EPSS snapshots with source timestamps, feed versions, hashes, deduplication, and non-destructive merges.
- Version asset-vulnerability relationships and ensure historical `as_of` reconstruction.
- Add the approved reviewer rubric and ingest only supplied expert labels.
- Build rows using the same v3 feature builder used by inference.
- Add temporal/grouped dataset splitting and leakage tests.
- Train real candidates in shadow mode and persist dataset provenance and evaluation metrics.
- Add explicit candidate validation and promotion/rollback controls.

## Information still required from ASIVM owners

Provide the asset-criticality and business-impact source/schema, the observation fields that establish internet exposure and reachable services, the reviewer identity model, the approved LOW/MEDIUM/HIGH rubric, label history if available, and any independently verified exploitation/outcome source. No asset records, outcomes, or expert labels are fabricated by this milestone.
