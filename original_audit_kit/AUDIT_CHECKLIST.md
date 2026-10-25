# End-to-end feasibility checklist

**Acquire & license**
- [ ] Download location, archive version/date/hash recorded
- [ ] Agreement reviewed for academic research, public site, redistribution, review quotes, images
- [ ] Separate photo metadata AND actual image bytes obtained and usage approved

**Data integrity**
- [ ] JSON parse errors measured; ID uniqueness and missing keys
- [ ] Review→business join fraction; image→business join fraction
- [ ] City/state duplicates resolved; restaurant category filter reviewed
- [ ] Coordinates valid and dates parseable; temporal coverage sufficient
- [ ] Scope selection explained (avoid first-N file ordering bias)

**Network**
- [ ] Distinct `(user_id, business_id)` edges counted
- [ ] Reviewers with >=2 in-scope businesses verified
- [ ] Projected graph edge weight = number of distinct common reviewers
- [ ] Community colors, centrality, adjacency matrix, alternative layouts validated
- [ ] Graph restricted to feasible size with reproducible thresholds

**Text and images**
- [ ] Nonempty review count, lengths and sample quality
- [ ] Frequency metric clearly means term counts vs document counts
- [ ] BERTopic/UMAP result inspected, stable, reproducible, and not overinterpreted
- [ ] Actual images decode, have business match and display rights
- [ ] Image montage and histograms robust to various sizes/modes
- [ ] Occlusion ONLY for trained/evaluated classifier, not a borrowed digit model

**Maps**
- [ ] EPSG:4326 coordinate validation and correct CRS transformation
- [ ] Sourced boundary polygons and region IDs validated
- [ ] Choropleths use valid denominators, not generic `cases/population`
- [ ] Sparse-data uncertainty and table alternatives shown

**App/QA/academic**
- [ ] Frozen cohort, documented licenses, clean package install
- [ ] Streamlit tabs, filters, state and caches work
- [ ] No secrets, inappropriate large assets or sensitive raw data committed
- [ ] Accessible labels, color contrasts, alt descriptions, mobile tests
- [ ] Required midterm Weeks 1–10 covered; final Weeks 11–14 separately planned
- [ ] Deployed app smoke-tested and method limitations displayed
