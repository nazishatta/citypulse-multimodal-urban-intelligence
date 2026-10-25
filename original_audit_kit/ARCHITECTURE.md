# Engineering architecture

Local licensed raw JSONL + optional photo metadata/assets (not published)
→ Streaming audit / file checksums
→ Deterministic single-city restaurant cohort
→ Clean, licensed processed extract + denominators
→ Offline preprocessing (NetworkX projection, BERTopic, UMAP, spatial joins, thumbnails)
→ Streamlit sections: Overview, Trends, Network, Reviews, Photos, Maps, Methods
→ Final: API + FastAPI/Flask + evaluated ML/NLP + deployment governance

**Networks:** From `review.user_id` and `review.business_id`, create deduplicated bipartite edges. For restaurant projection, shared distinct reviewers define weights. Use NetworkX degree, greedy modularity, betweenness and PyVis. Avoid O(N²) full-data projections; impose supported thresholds and record exclusions.

**Text:** CountVectorizer labels total term frequency honestly. Freeze one topic model for cross-year topic comparisons; precompute BERTopic/UMAP offline with fixed seeds; present example texts where license permits.

**Images:** Load actual authorized image bytes; validate joined `photo_id` and `business_id`; montage and normalized channel histograms. Classification/occlusion belongs to final only if a real evaluated classifier exists.

**Maps:** Business lat/lon EPSG:4326; verify polygon CRS; correct local projection for spatial measures; denominator should match Yelp measures such as reviews/business, not imported epidemiological examples.

**Deployment:** Preaggregate data; avoid reading gigabyte JSON on each Streamlit rerun; cache stable resources/data; protect privacy; test all tabs; pin compatible dependencies and supported Python version.
