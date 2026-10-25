**Motion revision v4:** Open `VISUAL_PREVIEW.html` for a synthetic animated chart preview. Read [docs/MOTION_SYSTEM_V4.md](docs/MOTION_SYSTEM_V4.md) for shared controls, timing, accessibility, browser checks and limits. Valid v2/v3 snapshots remain compatible.

# CityPulse — start here

This bundle upgrades the supplied audit kit into an executable multimodal project. It contains **no real Yelp dataset or photographs**. Tests use synthetic fixtures clearly labeled SYNTHETIC; their counts are not empirical findings.

## 1. Install (Python 3.12 recommended)
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```
On Windows activate with `.venv\Scripts\activate`.

## 2. Acquire permitted data
Use the official Yelp Open Dataset route and retain the applicable agreement. Obtain business/review JSONL plus separate photo metadata and actual image assets. User, tip and check-in files are not needed for the main analyses. Review public-display/redistribution terms before putting original reviews or photos in a public app. Do not assume metadata-only copies include images.

Official entry: https://business.yelp.com/data/resources/open-dataset/
Download entry: https://www.yelp.com/dataset/download
Acquisition was not performed by this release. If unavailable or unsuitable, stop and reassess the source rather than scrape or invent missing assets.

## 3. Prepare a new real-data snapshot
```bash
python scripts/prepare_data.py --data-dir /absolute/path/to/yelp --city Philadelphia --state PA --photo-json /absolute/path/to/photos.json --photos-dir /absolute/path/to/photos --out data/processed
```
City and state are explicit examples; select the actual city after inspecting coverage. Output path must not exist, protecting previous snapshots. Photo assets remain external; relative filenames are recorded. Set CITYPULSE_ASSET_ROOT to the image directory (or place authorized assets in snapshot/assets/photos). Moving the directory only requires updating that setting.

For a quick diagnostic prefix scan add `--max-records 200000` and use a different output directory. First-N results are biased and never a final feasibility pass. Every input file is hashed even during a limited parsing scan; hashing large files takes time.

Read data/processed/AUDIT_REPORT.md. Deduplicated record counts, monthly support, repeat reviewers, image decoding and provisional targets are measured. Permissions, topic meaning and public deployment are still separate checks.

## 4. Generate fixed text topics
```bash
python scripts/build_topics.py --snapshot data/processed --method nmf
```
NMF is the verified lightweight baseline. Topic fitting uses a seeded uniform sample of up to 5,000 eligible reviews (at least 10 words), sampled from sorted unique review IDs. The same fixed assignments support all filters. Other reviews remain in non-topic analyses; assigned population is disclosed. Output labels are automatic and require review.

Optional BERTopic + UMAP:
```bash
python -m pip install -r requirements-nlp.txt
python scripts/build_topics.py --snapshot /path/to/copied/snapshot --method bertopic
```
This downloads a sentence-transformer model on first use and may need substantial RAM. This optional path was not executed in this release. Topic outputs are protected from overwrite. Never report numerical model success or meaningful topic labels before evaluating the real-data results. TOPIC_REVIEW_PRIVATE.csv contains licensed review text; keep it private unless permitted.

## 5. Run
```bash
python -m streamlit run app.py
```
To use a different snapshot:
```bash
export CITYPULSE_DATA_DIR=/absolute/path/to/snapshot
python -m streamlit run app.py
```
Without prepared inputs the app displays truthful setup guidance, not fake Yelp charts.

## 6. Test
```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q tests
```
Read docs/VALIDATION.md for exactly what was tested. AppTest is automated Streamlit testing, not a real-browser accessibility certification.

## 7. Add geographic boundaries
Put an authorized GeoJSON at data/regions.geojson, with a declared CRS and unique region_id. The map tab spatially joins selected restaurant coordinates and shows business count or reviews per matched business. Missing boundaries are disclosed. Unknown CRS, duplicate IDs and overlaps block ambiguous aggregation. Points on polygon boundaries are unmatched under the documented within predicate. No epidemiological population rate is used.

## 8. Before public deployment
Keep all raw/processed Yelp data out of public git unless expressly permitted. Review content rights; prepare a permitted deployment extract and image location. Pin Python 3.12 and use the included dependency versions. Deploy only after all checks in docs/ACCEPTANCE_TESTS.csv have actual evidence. No public deployment is created by this ZIP.
