# CityPulse v5.5 — Cluster comparison intelligence

Adds a view switcher to **Clustering Lab → Geographic** (Exact size bars, Bubble profile, Treemap, Category mix). The existing ranked-size chart remains available below the new comparison. All views are derived from the currently selected DBSCAN groups; no clusters or numerical values are fabricated.

The **Bubble profile** maps selected restaurants per group to area, mean recorded business stars to x, mean Yelp snapshot review count to y, and cluster identity to hue. Categories come from the listed business category field. **Category mix** assigns each restaurant to its *first listed category*, so stacks sum to 100% (they are not total category memberships). The group profiles disclose denominator and sample restaurant names. Unassigned DBSCAN noise is retained in profiles but excluded from comparisons among fitted groups.

Ratings are platform reports rather than a validated measure of business quality. Review counts do not measure foot traffic, market demand, or profitability. Cluster membership is geographic, not causal. Demonstration mode is synthetic, not Yelp evidence. Both mode and limitations must be visible in the app.

## Acceptance

Run `.venv/bin/python -m pytest -q tests` on the installed project, then visit Clustering Lab, choose Geographic, and switch through all four comparison types. Filter the study population and confirm plotted numbers update. Review label/hover contrast and responsiveness in Chrome. Not certified in browser by this package alone.
