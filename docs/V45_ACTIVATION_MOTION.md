# CityPulse v4.5 — Tab activation motion

## Scope

This focused update repairs a tab-activation gap in the shared native-chart motion controller.

- First opening of each Streamlit tab: eligible visible native charts reveal automatically.
- Returning to another tab: its charts are eligible for a fresh introductory reveal.
- Rerendering the same tab without switching: does not deliberately restart every entrance.
- Off/reduced-motion: preserves static final-state behavior.
- Manual Play / Pause / Replay / Show final state remain available.
- Source values, axes, ID keys, calculations and datasets are not modified.

**Boundary:** This patch does not convert the synthetic placeholders into real restaurant photos, add actual Yelp data, or change algorithmic DBSCAN results. It also does not animate Folium basemap tiles or promise synchronization across separate map and chart components. Those require additional UI and integration work.

## Browser acceptance checklist

1. Open Trends: verify visible line and bar chart entrances are readable and finish at exact published values.
2. Open Reviews & Topics; return to Trends: expect an entrance on tab reactivation.
3. Change a sidebar filter without changing tabs: figures should update without a continuous replay loop.
4. Set Motion Off: switch tabs and verify static final states.
5. Enable operating-system Reduced Motion: no nonessential entrance animations.
6. Verify Play, Pause, Replay and Show final state on a chart.
7. Change focus and confirm no review IDs, ratings, bar heights or axis scales change because of animation.
8. Check Chrome and Safari, laptop and narrow viewport; verify interactive marks remain usable after playback.

## Next substantive work

Real-data acquisition and photo rights; meaningful group profiling and linked evidence in Clustering Lab; review term alternatives with representative records; real browser testing and full lecture-aligned visualization acceptance.
