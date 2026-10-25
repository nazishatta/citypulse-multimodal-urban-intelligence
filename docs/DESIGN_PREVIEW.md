# CityPulse v4.1 — Dark Visual Preview

The app displays **SYNTHETIC PREVIEW MODE** when no official dataset is configured and `data/processed/audit.json` does not exist. Synthetic data are generated deterministically in ignored `data/synthetic_preview_*` directories using the same snapshot preparation/validation path as actual Yelp input. All restaurants, reviews, coordinates, and graphics in this state are fictional. **Do not cite preview metrics as Yelp findings.**

This is a design and interaction preview, not a research study. No third-party photographs are supplied. Generated images are abstract placeholders labeled synthetic.

## Switch to real Yelp data

```bash
CITYPULSE_DATA_DIR=/absolute/path/to/verified/processed CITYPULSE_ASSET_ROOT=/absolute/path/to/permitted/photo/assets python -m streamlit run app.py
```

An explicitly configured but missing `CITYPULSE_DATA_DIR` continues to show a setup error instead of silently falling back to demo data. Set `CITYPULSE_DISABLE_DEMO=1` to show the original no-data state.

## Preview operation

```bash
python -m streamlit run app.py
python -m pytest -q tests
```

Use the Motion mode and speed sidebar controls. The existing shared motion controller remains unchanged, so additional enhancements should be audited for actual visual effects and reduced-motion behavior.

## Acceptance

- Application background and Plotly canvas match the dark theme.
- All seven tabs are visible with real-shaped **synthetic** example data.
- Synthetic banner remains visible, including after changing tabs and filters.
- Yelp data are never inferred from or replaced by synthetic records when `CITYPULSE_DATA_DIR` is set.
- Snapshot checksums remain enforced.
- Actual Yelp acquisition, photo permissions, and browser/mobile verification are still required.
