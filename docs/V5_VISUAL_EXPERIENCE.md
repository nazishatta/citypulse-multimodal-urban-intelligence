# CityPulse v5.0 — Visual Experience Release

This is a **targeted, visible upgrade** to the v4.5 application; existing eight tabs and all integrity safeguards remain.

## New visible experiences
- **Trends:** automatically playing, multi-second temporal reveal with Play/Replay, Pause, and Final controls. Axes stay fixed; native data tables remain available.
- **Reviews:** a language treemap and a 100% stacked reported-rating comparison, both based on current eligible records. Chart values have accessible data tables.
- **Clustering:** observed spatial-group profiles showing group size, snapshot mean rating, and sample restaurant names (not predicted opportunity).
- **Methods:** a connected research journey and realistic limitations of business inference.
- **Visual polish:** consistent eight-tab hero copy and clearer interpretation panel headings.

## Motion note
The new trend motion uses Plotly frames in a contained iframe and starts on tab rendering. The user's explicit Off and Reduce motion modes display an unanimated chart instead. Browser-level system prefers-reduced-motion detection for this particular new iframe is not yet implemented; use the application motion selector and test in Chrome before making accessibility claims.

## Evidence rules
- Preview mode continues to be clearly labeled synthetic.
- Real Yelp data, licensed business photographs, browser/keyboard QA and cloud deployment are NOT supplied or certified.
- Text-term treemap is not topic modeling or sentiment.
- Ratings are observed review labels, not model-inferred text sentiment.
- Snapshot ratings in cluster profiles are distinct from selected-review means.

## Verification
- Python compilation passed.
- 29 focused non-UI regression tests passed in the packaging environment.
- Full suite must be run on your Mac: `python -m pytest -q tests`.
- No browser visual or real-data acceptance is claimed.
