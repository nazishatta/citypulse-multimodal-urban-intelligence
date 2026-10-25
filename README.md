**Motion revision v4:** Open `VISUAL_PREVIEW.html` for a synthetic animated chart preview. Read [docs/MOTION_SYSTEM_V4.md](docs/MOTION_SYSTEM_V4.md) for shared controls, timing, accessibility, browser checks and limits. Valid v2/v3 snapshots remain compatible.

# CityPulse — Multimodal Urban Experience Atlas

An interactive Streamlit explorer connecting restaurant geography, review language, image properties, shared-reviewer networks, and review activity over time.

**Current release:** runnable software, hardened preparation pipeline, tests and implementation audit. **Actual Yelp-data feasibility and public deployment remain unverified.** This repository contains neither the licensed dataset nor photos.

Start with **START_HERE.md**.

## What is implemented
- Seven state-aware tabs: Overview, Trends, Map, Reviews & Topics, Photos, Networks, Methods.
- Shared category/date/exact-term/topic filtering; restaurant focus is separate.
- Chart selection adapters for business focus, map focus, exact terms, fixed topics and Plotly network nodes, with ordinary form controls as alternatives.
- Reset callback clears widget keys and chart epoch; regression test checks later interactions.
- SQLite city preparation with global ID deduplication, finite-coordinate checks, date/rating validation, source SHA-256 and image decoding.
- Normalized RGB histograms, channel inspection and image montage from actual prepared assets.
- Reviewer-to-restaurant projection, edge thresholds, exclusion reporting, degree, communities, distance-aware betweenness and adjacency matrix.
- Opt-in PyVis physics and fixed circular layout, with hover names and thin edges.
- Haversine DBSCAN plus optional polygon spatial join and choropleth; Folium street-map option.
- Fixed NMF topic preparation, review sheet, and optional unverified BERTopic/UMAP script.
- Metadata exports omit reviewer IDs and text by default; private source inspection is explicit.

## Scientific limits
Review posting dates are not visits. Yelp is not a census. Current business ratings and filtered review means are different populations. Photos belong to businesses, not individual review events. Shared reviewers are not friendships. UMAP distances, inferred topics and algorithmic communities are exploratory. Labels require interpretation review.

## Scope boundaries
No claims of dataset suitability, model accuracy, fairness or submission readiness are inferred from software tests. No decorative motion is prioritized over readability. Final-project API and model serving remain planned; image saliency requires an evaluated model.

## Repository layout
- app.py: coordinated dashboard
- src/pipeline.py: actual-data preparation and structural audit
- src/analysis.py: pure filtering, temporal, text, spatial, image and graph calculations
- scripts/prepare_data.py: preparation CLI
- scripts/build_topics.py: offline topic generation
- tests/: synthetic adversarial fixtures and automated app checks
- docs/: independent findings, acceptance tests, methods and release evidence
- original_audit_kit/: preserved input reference; its original script is superseded by the new preparation pipeline

Dataset provenance and a reviewer-approved interpretation log belong in your finished submission. Document AI assistance under the course policy and understand/defend every analysis decision.
