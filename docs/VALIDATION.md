Current validation: see TEST_RESULTS.txt, BROWSER_RESULTS.txt and MOTION_SYSTEM_V4.md. The earlier validation record follows for history.

# Validation evidence

The supplied original kit: one unittest passed. The original upgraded release passed 33 tests. The v2 integrity revision passed 51 tests. This visualization revision: **57 pytest tests passed in 22.11 seconds (exit 0)** in the development environment. See TEST_RESULTS.txt.

Verified against synthetic fixtures: global deduplication; joint date/text eligibility; 36-month support; real image decoding and corrupt-image exclusion; unsafe photo paths; NaN/boolean/out-of-range coordinates; first-N status; protected snapshots; category OR and cross-filter AND; exact tokens; missing-date inclusion/exclusion; monthly gaps and denominators; distinct-user projection weights; high-activity exclusions; pair evidence; RGB normalization; haversine clusters; empty states; no-data guidance; reset followed by another interaction; all seven views via Streamlit AppTest; NMF offline artifacts and topic filtering; PyVis and circular rendering via AppTest; GeoJSON spatial join and choropleth.

Not verified: actual Yelp records or download availability; population representativeness; source rights; topic semantics; actual city polygons; byte-for-byte browser downloads; native chart selection events in a real browser; PyVis visual/drag quality in a real browser; mobile, keyboard focus, screen-reader/contrast audit; real-data timings and memory; clean OS installation; optional BERTopic/model download; public deployment; final model API or model performance.

AppTest executes Streamlit's application logic and checks for exceptions; it does not certify browser JavaScript, canvas, maps or assistive technology. Synthetic fixtures are generated only in temporary test directories; they are not shipped as a Yelp dataset or used as research findings.

Environment versions are recorded in ENVIRONMENT.json. Main direct dependencies are pinned to the versions exercised. This is not a full transitive lockfile or cross-platform reproducibility guarantee.

Revision v2 adds negative snapshot/topic integrity checks, photo relocation/checksum checks, diversified deterministic examples, cross-tab focus/pair persistence, cache-tampering rejection and graceful missing assets. See REVISION_V2.md. Benchmark harness smoke-tested only with synthetic inputs.

Visualization revision: six figure renderings reviewed with synthetic inputs; shared encodings and optional replay/offline map checked by regression tests. Full-app browser verification remains pending. See VISUAL_REVISION_V3.md.
