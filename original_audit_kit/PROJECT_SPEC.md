# CityPulse — Multimodal Urban Experience Atlas

**Question:** How do recorded restaurant experiences differ by geographic area, review language, images, shared-reviewer connections and time?

**Study scope:** one well-supported city/state and restaurant category; stable date range; deterministic, frozen population. May expand at final only with explicit dataset-version and cohort change logs.

## Midterm dashboard (Weeks 1–10)
1. Overview & multivariate: ratings, business categories, review counts, attribute missingness.
2. Time-series: monthly reviews, ratings distributions, filters; note review date ≠ visit date.
3. Network Explorer: reviewer–restaurant bipartite graph; weighted restaurant graph, modularity communities, degree, betweenness, adjacency matrix, force/circular layouts.
4. Language Explorer: CountVectorizer frequency, transparent example reviews, BERTopic topic estimates and optional UMAP when adequately validated.
5. Photo Inspector: metadata-linked actual images, image montage, RGB/intensity histograms, annotations, category counts.
6. Map Explorer: restaurant point map, optional geographic boundary join/normalized choropleth and spatial clusters.
7. Methods & Evidence: data provenance, join/sample denominators, limitations, accessibility and reproducibility.

**Interactions:** city/category/date filter; restaurant focus across tabs; meaningful captions; table alternatives for visual displays; performance-minded caching; avoid accidental filter resets.

## Final extension (Weeks 11–14)
Documented API for updated external aggregate information (clearly separated from old Yelp snapshot); FastAPI or Flask serving; evaluated ML/NLP feature with train/validation/test isolation; deployment/ethics/report/presentation. Occlusion heatmaps only when an actual trained image model is available and validated.

**Scientific caveats:** Yelp is not a census of restaurants or customers; reviewer overlaps are not friendships; business photos cannot automatically be linked to individual review events; public ratings are subject to selection bias.
