# CityPulse v5.5.1 — Clustering repair

- Normalizes recorded business attributes using supported explicit column aliases without inventing values.
- Omits generic umbrella categories such as “Restaurants” when selecting informative primary categories. A generic-only business is assigned “Other restaurant.”
- Hides Bubble profile when recorded star and review-count measures cannot be resolved; hides Category mix when no meaningful category distinctions exist.
- Focus selection highlights the chosen group and displays its underlying business records; no new group is fabricated.
- Hides text topic grouping when no verified topic assignments exist; original Reviews & Topics functionality remains available.
- Shared audience visualization uses actual observed graph edges in interactive PyVis physics with Freeze and reduced-motion support, rather than a static coordinate plot. The subtle nudge runs only when allowed and the document is visible.
- All results in synthetic preview are illustrative and must not be treated as Yelp findings. Review-count activity is not evidence of customer demand.
- Acceptance: run full Mac pytest suite and visually verify hover, group changes, and movement in Chrome. A unit test cannot certify browser motion.
