# CityPulse v4.4 — Motion and Interaction Readability

This controlled release preserves the eight existing tabs, analytical records, filter semantics, cluster calculations, charts, and snapshot integrity.

## Changed
- Entrance motion uses slower, perceptible durations: Quick 1100 ms, Standard 1900 ms, Gentle 3000 ms.
- Bars and markers can reveal in a short stagger rather than all appearing simultaneously; the browser still renders final original values.
- Timeline replay allows at least 90 ms per month, avoiding effectively instantaneous frame changes.
- Default speed is Standard.
- Preview warning uses restrained amber rather than a red exception-like banner; its synthetic disclosure remains prominent.
- Existing motion off, reduced motion, pause, replay, and final-state controls remain available.

## What this does NOT certify
- A screenshot cannot demonstrate that playback is working in a specific browser. Test the real app in Chrome and in reduced motion.
- Maps still use true fixed restaurant coordinates; no fake geographic movement is introduced.
- Preview images are illustrations, not real Yelp photos.
- This release does not claim to fix full cross-chart linked selection or to add new datasets.

## Browser acceptance sequence
1. Open Trends; scroll to the monthly bar chart. Verify perceptible one-shot reveal.
2. Click Pause and Replay; Show final state must restore exact counts.
3. Select Gentle speed and compare timing with Quick.
4. Enable temporal replay; verify at least one month is discernible before proceeding.
5. Set Motion Off, reload, and confirm no animated reveal.
6. Set OS reduced motion and confirm nonessential motion stops.
7. Switch tabs and revisit: data and filters must not change because of playback.
8. Test chart selection/hover after motion stops and inspect accessible tables.
