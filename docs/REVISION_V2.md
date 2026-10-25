# CityPulse integrity and exploration revision

Development GO; submission readiness remains NO-GO until real-data and browser acceptance.

## Implemented corrections

- Database SHA-256 verified on every dashboard rerun, before consulting cached data; verified again across an uncached load. Tampered snapshots stop the app. Local hashes detect mismatch, not malicious replacement of both audit and data.
- Topic files require a parent snapshot hash, file checksums, unique nonempty review IDs belonging to the parent, integer assignments, valid labels and reconciled counts. Optional embedding coordinates and assignments must agree. Partial, stale and changed artifacts stop loading.
- Permanent network restaurant/pair state is independent of transient widget state. An explicit restaurant-to-network action changes focus/navigation without changing the global corpus.
- New preparation stores relative photo filenames, dimensions and SHA-256. CITYPULSE_ASSET_ROOT resolves photos and permits relocation. Absolute/escaping paths are rejected; missing or changed assets show a warning and are withheld.
- Topic review sheets contain disjoint representative, low-margin boundary and seeded random samples. Sparse topics have fewer roles. NMF scores are normalized component weights; BERTopic scores use centroid cosine similarity. These are exploratory ranking measures, not calibrated probabilities. Human interpretation remains pending.
- A benchmark CLI measures verified loading, graph construction/metrics, topic loading and Plotly serialization, plus traced Python peak allocations. It does not measure browser paint or full-process RSS.

## Upgrade instructions

Keep your old snapshot. Prepare a NEW snapshot with this revision so photo references are portable. Rebuild topics in that snapshot; legacy topic files without hashes are deliberately rejected. Do not edit checksums merely to suppress validation errors.

```bash
export CITYPULSE_DATA_DIR=/absolute/path/to/new/snapshot
export CITYPULSE_ASSET_ROOT=/absolute/path/to/authorized/photos
python scripts/build_topics.py --snapshot "$CITYPULSE_DATA_DIR" --method nmf
python -m streamlit run app.py
```

Default photo root is <snapshot>/assets/photos. If photos remain elsewhere, set the asset root as above. No image files or original review datasets are included.

```bash
python scripts/benchmark.py --snapshot "$CITYPULSE_DATA_DIR" --provenance real --out benchmark-real.json
```

Run a fresh process several times and record machine specs, cold/warm conditions and process RSS externally before claiming real performance. Full-city loads and reviewer projections still require measurement; hashing every rerun adds I/O intentionally.

## Remaining acceptance gates

1. Acquire authorized actual Yelp business, review, photo metadata and image files; retain applicable terms and decide public-display/export permissions.
2. Select a city using measured join coverage, review language, photograph availability and shared-reviewer connectivity. Review topic samples and document provisional labels.
3. Run real-data benchmarks and set justified time/memory limits. No real-data benchmark result is supplied here.
4. In a real browser test Plotly point/bar selection, map focus, keyboard alternatives, network selector/pair evidence, tab persistence, reset and exports. AppTest verifies state/render execution, not mouse events, keyboard usability or client JavaScript.
5. Validate deployed asset access, startup, all seven tabs and accessibility. PyVis dragging stays inside the embedded component; it does not send selection events to Streamlit. Folium is an optional basemap, not a coordinated selection source.
6. Optional BERTopic/model downloads and browser rendering remain unverified. No scientific or deployment readiness score is inferred from passing tests.

Animations remain opt-in PyVis physics; no claim of automatic entrance animations is added by this revision.
