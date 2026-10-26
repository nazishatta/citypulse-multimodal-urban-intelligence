# CityPulse v5.1.1 — Visual repair notes

- Hover labels: fix unreadable white-on-white tooltip by using charcoal background and light text in shared Plotly styling.
- Geographic clustering overview: show actual restaurant positions in an offline longitude/latitude scatter chart. Avoid relying on online map tiles for the eighth tab; this chart is not a street map.
- Guided DBSCAN group scene: use 1.6 second per stage and optionally loop, with a pause at the end to make three cluster groups visible across repeated viewings.
- Respect system reduced motion: the animation controller goes directly to the final state.
- Not changed: research grouping computation, geographic DBSCAN thresholds, reviewer graph, source-data provenance, and the Map tab's map-tile functionality.

## Browser checks
1. Hover network nodes in both Networks and Clustering Lab; tooltip should be readable.
2. Open Clustering Lab > Geographic; the first overview must show points even without Internet map tiles.
3. Scroll to Story mode; three computed clusters should reveal in sequence, pause, and repeat.
4. Press Pause and Show final state. With macOS Reduce Motion on, expect no autoplay.
