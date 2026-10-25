# Copy/paste prompt for independent comprehensive audit

Act as a principal multimodal data engineer, data visualization professor, graph researcher, NLP/image researcher, geospatial analyst, Streamlit architect and technical QA reviewer. Audit the **CityPulse — Yelp Multimodal Urban Experience Atlas** project plan and any real Yelp data provided. The app must use lecture methods Weeks 1–10 at midterm and extend to Weeks 11–14 for final.

1. Inspect ALL project files, exact source data, timestamps, schemas, legal user agreement and actual photo assets; do not assume unavailable files exist.
2. Run the supplied streaming auditor in full-scan mode and inspect its raw JSON results. Document if only a first-N sample was run; it is biased.
3. Compute review/business, image/business join coverage; business-ID uniqueness; valid geo coordinates and dates; city-state collisions; temporal support.
4. Verify useful distinct reviewer–restaurant pairs, repeat reviewers, weighted projection feasibility, community detection, centrality and adjacency visualization at practical scale.
5. Verify robust and interpretable text coverage, term-frequency semantics, topic validity, BERTopic/UMAP reproducibility.
6. Verify actual decoded authorized images, class balance, captions, business join and RGB-montage feasibility; reject unsupported model occlusion claims.
7. Verify maps, CRS, spatial joins, choropleth denominators and accessibility.
8. Trace each of Weeks 1–10 to an actual functioning interaction and Weeks 11–14 to an implementable final extension.
9. Check reproducibility, citation, licenses, secrets, cloud build, cached outputs, performance, alt text and responsible analysis.
10. Complete `templates/REVIEW_SCORECARD.md` with evidence-backed statuses PASS/CONDITIONAL/FAIL/NOT VERIFIED; provide blockers, remediation steps and a GO/CONDITIONAL GO/NO-GO decision.

Do NOT fabricate Yelp counts, images, joins, professor grading weights, test passes or deployment behavior. Separate observed evidence from design suggestions and state exact limitations.
