# Methods and design decisions

**Population.** Exact case-insensitive city and state plus Restaurants category. Business/review/photo IDs use first valid object per ID. Duplicate IDs do not contribute twice. Missing IDs excluded. Invalid dates, ratings and coordinates remain missing; relevant analyses state their eligibility rule. Ratings outside 1–5 are null. Dates before 2004 or after preparation day are excluded from temporal eligibility.

**Selection.** OR within category/topic lists; AND across category, date, exact term and topic. Categories define a business cohort; global metrics identify businesses with selected review evidence. Topic filtering restricts to assigned documents. Restaurant focus affects evidence panels, not global totals. Native chart callbacks update the same sidebar state. PyVis is explicitly not connected by click; equivalent selectors exist.

**Time.** Calendar month counts include gaps as zero; mean rating gaps remain missing. Rated-review count accompanies means. No booking, visit, revenue or causal inference is implied.

**Text.** English CountVectorizer unigram/bigram analyzer for term charts and term filtering. Document count and occurrence count differ. NMF baseline fits TF-IDF once, fixed seed and uniform capped sample; labels are automatic top terms. BERTopic/UMAP optional, requires separate environment/model download and semantic evaluation. No claim of validated sentiment from unsupervised topics.

**Network.** Deduplicated user–business memberships. Restaurant projection weight = shared distinct reviewers. Users above configurable business count excluded from projection to bound clique expansion; exclusion count shown. The pair evidence view includes all shared users, explicitly contrasting its denominator with the projected graph. Degree means connected businesses; strength sums shared-reviewer weights. Betweenness uses inverse weight as distance. More than 200 nodes uses 100 sampled sources and discloses approximation. Communities are calculated on selected thresholded graph; display cap affects drawing only. No social friendship or geographic interpretation of graph distance.

**Geography.** Input coordinates EPSG:4326, finite/range validation only; local plausibility still needs review. Haversine DBSCAN uses meters converted to radians, min_samples=3. Geographic clusters are distinct from graph communities. Optional polygons must declare CRS and unique region IDs; within join excludes boundary points and reports misses. Overlapping joins withhold the choropleth. Reviews/business uses matched selected-business denominator, not population per 100k. White-bg coordinate maps do not need live tiles; Folium option does.

**Images.** Metadata joins on business_id only. Safe file stems, decoded files and per-image hashes. RGB analysis preview limited to 1024px; original dimensions disclosed. Histograms normalize each channel to sum to one. No trained classifier, saliency or image-date trend is fabricated.

**Accessibility and UI.** Native controls and labels, ordinary selectors beside chart actions, data-table alternatives, thin edges, hover names. Physics is opt-in and circular layout fixed. Readability, browser reduced-motion preference, contrast and screen-reader behavior still require manual browser checks. Tables rendered through Streamlit are not assumed certified for every assistive technology.

**Performance.** Full JSON scans happen offline. App caches city snapshot reads and projected graphs; tab-aware execution skips hidden analyses. Real-data load times and memory are not yet measured. Topic preparation is offline. Global reviewed corpus remains local and private unless terms permit deployment.


## Revision v2 integrity and evidence sampling
See REVISION_V2.md for enforced lineage, permanent focus state, portable photo references and disjoint topic example sampling. Checksums provide consistency, not authenticated provenance. Real-data performance and semantic validation remain pending.
