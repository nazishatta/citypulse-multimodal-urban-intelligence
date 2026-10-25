# CityPulse — Yelp Multimodal Dataset Audit Bundle

**Use case:** A coherent Streamlit project that implements Weeks 1–10 for the midterm and extends to Weeks 11–14 for the final. This is a **feasibility audit kit**, not a finished app, actual downloaded Yelp data, or a certification of dataset suitability.

## Steps
1. Obtain authorized Yelp Open Dataset files yourself and review the user agreement. Store raw archives OUTSIDE the GitHub repository.
2. Extract the five JSONL files to a local directory. Separately acquire Yelp photo metadata **and actual images** if available and permitted. The popular Kaggle dataset includes five JSON files, NOT the photo archive.
3. Run a rapid exploratory scan (first N lines is NOT representative):

```bash
python3 scripts/audit_yelp.py --data-dir /path/to/yelp --city Philadelphia --state PA --max-records 200000 --out audit_results
```

4. Run full, city-specific feasibility assessment (streams file records, slower, no artificial sample cap):

```bash
python3 scripts/audit_yelp.py --data-dir /path/to/yelp --city Philadelphia --state PA --out audit_results
```

5. If separately provided, add `--photo-json /path/to/photo.json --photos-dir /path/to/photos`.
6. Read `audit_results/AUDIT_REPORT.md`, populate `templates/REVIEW_SCORECARD.md`, and run `python3 -m unittest discover -s tests -v`.

**Flags:** `--city` selects exact case-insensitive city and `--state` filters state; defaults in script are no city/state filter. The auditor has standard-library-only dependencies. Full scans may take time; it does not fetch data and never modifies inputs.

## Contents
- `PROJECT_SPEC.md` — question, audience, app modules, midterm/final split.
- `COURSE_MATRIX.md` — explicit Weeks 1–14 coverage.
- `DATA_AND_LICENSE.md` — provenance, joins, photos, scope, bias, licensing.
- `AUDIT_CHECKLIST.md` — detailed audit points and suggested evidence.
- `ACCEPTANCE_GATES.md` — GO/NO-GO decision rules.
- `ARCHITECTURE.md` — pipeline, graph, NLP, image, spatial, Streamlit, ML plan.
- `AUDITOR_PROMPT.md` — ready-to-paste independent audit assignment.
- `scripts/audit_yelp.py` — streaming actual-data profiler.
- `tests/test_audit_yelp.py` — synthetic smoke test.
- `templates/REVIEW_SCORECARD.md` — fillable review matrix.
- `.gitignore` — raw-data/credentials exclusions.

## Hard constraints
Never present illustrative/sample results as real Yelp evidence. Do not upload Yelp raw reviews, reviewer records, or photographs to public GitHub without confirming permitted uses. A genuine image modality requires accessible actual images, not metadata alone. Keep your existing Clinical AI Research Atlas repository separate.
