Historical v3 visual revision. Current motion behavior and browser evidence supersede the motion/browser-status statements below: see MOTION_SYSTEM_V4.md and BROWSER_RESULTS.txt.

# CityPulse v3 — Visualization-focused revision

The central deliverable is a clear, connected visualization experience. v2 integrity controls remain in place; this revision refines the existing views rather than adding more analytical modalities.

## Review the design before installing data

Open `VISUAL_PREVIEW.html` in a browser. It contains clearly labeled, generated synthetic records and the same Plotly figure builders used by the app. It is self-contained, with hover, zoom and data tables. It is a chart-style review, not the full seven-tab application: its selections do not change Streamlit filters. Synthetic values establish no research findings or real Yelp feasibility.

To rebuild it: `python scripts/build_visual_preview.py --out VISUAL_PREVIEW.html`.

## What changed

| View | Visual improvement | Design purpose |
|---|---|---|
| Shared shell | Navy title panel, consistent typography, neutral canvas, restrained teal, compact KPI cards and numbered section hierarchy | Make the analytical content easy to scan |
| Overview | Fixed rating axis, meaningful hover, selected-review mean reference and a diamond for the focused restaurant | Compare volume and ratings; distinguish focus without relying on color alone |
| Trends | Side-by-side activity/rating charts, selected calendar ticks, honest fixed rating range, observed-coverage note | Separate volume from rating context without a dual axis |
| Map | Context basemap/offline canvas switch, focused-place highlight and geographic clustering labels | Provide orientation while retaining a network-independent fallback |
| Language | Horizontal ranking, 10/15/25-term display control, counts outside bars and meaningful axis labels | Use common-scale length for precise comparisons |
| Topics | Horizontal bars and wrapped labels; fixed category colors on optional document maps | Avoid long angled labels and color changes during filtering |
| Photos | Aligned cropped montage thumbnails, full-aspect inspector, adjacent RGB distributions, percentage scale and channel inspection | Compare the collection, then inspect original image structure |
| Network | Focus outline, community legend, richer node hover and equal layout scale | Explain node encodings and preserve layout geometry |
| Matrix | Compact R01-style keys, full restaurant names on hover, name-key table and zero-based sequential scale | Prevent long restaurant names from overwhelming the matrix |
| Every chart | Shared Plotly styling, accessible table, CSV export and SVG toolbar export configuration | Support precise inspection and presentation-quality graphics |
| Methods | Detailed audit behind an expander; limitations remain available | Keep evidence interpretation visible without overwhelming chart reading |

The photo KPI now says **Prepared photo records**. It does not claim those files are currently accessible. Files are verified as the displayed photos are opened; the montage is explicitly a stable first-nine navigation sample, not a representative sample.

## Interaction and movement

Existing Plotly selection callbacks and ordinary widget alternatives remain. Optional temporal replay progressively reveals the same monthly counts on fixed axes. Playback starts only after the visitor enables it, and only when the system does not request reduced motion. Replay/Pause controls remain available. No looping decorative animation or claim of scroll-triggered transitions is added.

PyVis physics remains opt-in. PyVis clicks and optional Folium maps do not synchronize Streamlit selection; the restaurant selector remains the evidence control. Mobile layout, keyboard use and screen-reader behavior still require browser acceptance.

## Course alignment used for this revision

The supplied syllabus describes the midterm as an interactive Streamlit application with narrative, at least three modalities, accessibility and reproducibility (p. 4). Its first ten weeks cover tabular, time-series, Streamlit, networks, text, images and maps (p. 3).

The supplied *Grammar of Graphics & Design Principles* slides inform these decisions: perceptual channel ranking (p. 15), categorical versus quantitative color (p. 17), redundant shape/color encoding (p. 18), attention and motion (p. 21), expressiveness/effectiveness (p. 23) and zero baselines for bars (p. 26). This revision is not evidence that every lecture exercise has been completed. Supplied teaching materials are not redistributed in the bundle.

## Verification and limits

See TEST_RESULTS.txt for the complete regression result. Six chart types were rendered with synthetic fixtures and inspected for axes, wrapping, spacing and color; AppTest exercises all seven tabs, focus persistence, reset, optional replay and the offline map option. Tests also check figure values/IDs, rating gaps, matrix hover identity and replay controls.

Full-app browser screenshot/interaction verification could not be completed in this environment. A browser download was unavailable; rendered figure review is not an end-to-end app-browser test. Native Plotly selection, replay playback/pause, responsive layout, exports, tile access, keyboard/screen-reader behavior and deployed assets remain acceptance items. The self-contained HTML preview is generated and structurally checked; it is not claimed browser-certified.

No real Yelp records or photos are included. City feasibility, topic interpretation, image rights, full-city performance and deployment remain pending. Valid v2 snapshots and topic artifacts are compatible; legacy v1 artifacts still need the v2 migration. Scientific conclusions must come from your authorized real dataset and your own interpretation.

## Visual acceptance checklist for the final real-data pass

- Each chart answers a stated question and names the population and eligibility rules.
- Desktop and narrow-screen plots have readable labels, no clipped titles and no obstructed controls.
- Bars start at zero; rating ranges are stable; count and rate denominators are explicit.
- Selecting a point/term/topic leads to correct evidence, and clearing focus/filter state restores the correct counts.
- A keyboard user can perform the investigation with ordinary controls; chart tables retain exact values.
- Color is supplemented with labels, shapes or line patterns; contrast and assistive-technology use are tested.
- Network metrics, displayed subgraph and matrix scope reconcile.
- Photographs load on the deployment host; unavailable images never appear in an accessible-file count.
- Motion is brief, optional, pausable and verified with reduced-motion settings.
- Your final narrative states observations supported by the real data and distinguishes them from interpretation.
