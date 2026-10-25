# CityPulse v4.2 — Eighth tab: Clustering Lab

Adds a dedicated **Clustering Lab** tab after Networks and before Methods, preserving the existing seven views.

The Lab separates three questions:

1. **Spatial / geographic clustering:** DBSCAN with a user-adjustable meter radius and `min_samples`. Group `-1` means **unassigned/noise**, not an error. Uses actual in-scope restaurant coordinates and the original `business_id`s.
2. **Network community detection:** weighted reviewer–restaurant projection, then NetworkX greedy-modularity grouping. Links require at least the chosen number of distinct shared reviewers. Colors encode graph communities, not geography, friendship, or business partnerships. The node drawing is capped but group computation is performed on the eligible graph.
3. **Text groups:** frozen dominant NMF topics calculated on the audited snapshot, then restricted to selected review IDs. **NMF topics are not equivalent to spatial or graph clusters**, and are not ground-truth sentiment labels.

All charts include source-data tables and the existing shared animation metadata. The tab displays a narrative interpretation and exact counts. The preview retains the large **synthetic** warning; no synthetic findings should be submitted as Yelp research.

## Install

From the CityPulse repo root after v4.1 installation:

```bash
unzip -q ~/Downloads/CityPulse_v4_2_Clustering_Lab_Patch.zip -d ~/Downloads
bash ~/Downloads/CityPulse_v4_2_Clustering_Lab_Patch/INSTALL_V42.sh
python -m pytest -q tests
python -m streamlit run app.py
```

## Acceptance notes

- An interactive chart existing in Python **does not certify automatic browser playback**. The existing v4 shared motion system remains in use, but autoplay, pause, replay, browser rendering and reduced-motion operation need a real browser audit.
- The synthetic preview geography is visibly artificial and may give all-noise labels for certain DBSCAN settings; do not invent clusters to make the demo prettier.
- For real-data performance, benchmark NetworkX graph projection and betweenness before scaling to large Yelp cities.
- Genuine NMF topics must be built from the real data; no unverified topic groups are generated automatically.
