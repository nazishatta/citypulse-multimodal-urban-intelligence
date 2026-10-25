Historical engineering audit below. Current visual revision and validation: VISUAL_REVISION_V3.md and TEST_RESULTS.txt.

# Independent audit of supplied CityPulse kit

## Observed input
CityPulse_Yelp_Complete_Audit_Bundle(1).zip, 28,912 bytes. Standard ZIP integrity check passed. It contained markdown plans, a standard-library JSONL auditor, one test and compiled caches. **No app.py, Yelp records, photo assets, maps or topic model were supplied.** The original smoke test passed (one test).

## Findings and disposition
| Severity | Finding in supplied kit | Disposition in this release |
|---|---|---|
| Critical scope | Filename implies complete project; contents are a feasibility kit | Added runnable seven-view app; explicitly no real-data/deployment validation |
| High | Duplicate IDs counted but duplicate reviews still enter totals | Global ID deduplication before analysis, first-record policy documented |
| High | Nonempty JPG existence does not prove image decodability | Pillow verify + actual decode; corrupt/missing/path-traversal cases tested |
| High | Proposed 24-month gate not measured; dates/text counted independently | Monthly counts and joint dated/nonempty text eligibility measured |
| High | No deterministic downstream extract | New isolated SQLite snapshots and protected output paths |
| Medium | Input checksums mentioned but not implemented (hashlib unused) | Source and snapshot SHA-256 written |
| Medium | Duplicate business rows inflate coordinate totals | Coordinate metrics calculated after deduplication |
| Medium | Memory tracks global work/review IDs in Python sets | Disk-backed SQLite unique-ID tracking; only selected businesses kept in memory |
| Medium | Structural targets do not produce a machine-readable disposition | Conservative engineering status plus rights/semantic review pending |
| Medium | Unknown city feasibility | Explicit city/state, coverage counters; no invented successful city choice |
| Low | Compiled caches shipped | Excluded from new archive |

## New work
Centralized shared filtering; reset regression tests; lazy tab rendering; real-data network projection and lookup; exact tokenizer; no misleading population rates; images decoded; offline topic artifacts; optional map boundaries. See VALIDATION.md and ACCEPTANCE_TESTS.csv.

## Remaining blockers to empirical release
1. Obtain actual authorized data and photo assets.
2. Run full uncapped preparation for candidate city/cities and inspect support.
3. Validate semantic topic labels and sampling/missingness.
4. Verify boundary sources, geographic plausibility and unmatched joins.
5. Run actual browser, responsive and accessibility checks on real data.
6. Confirm public display/redistribution terms and deployment asset paths.

This release upgrades the software. It does not establish that Yelp access is available, that a selected city meets targets, or that the project will earn a particular grade.
