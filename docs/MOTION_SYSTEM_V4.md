# CityPulse v4 — Shared motion system

## What visitors get

All seven tabs share one motion policy. The sidebar exposes **Motion mode** (Follow system / Reduce motion / Off), **Motion speed** (Quick / Standard / Gentle), and **Play / Pause / Replay / Show final state**. Native charts and the image collection also have local playback controls. Methods uses the shared page-introduction reveal rather than animating scientific claims or text values.

- **Play** starts a finished reveal or resumes a paused reveal.
- **Pause** freezes native reveal animations at their current progress. A partial-reveal label remains visible; chart hover is withheld until completion or Show final state. Exact data tables remain available throughout. Network pause freezes the current node layout.
- **Replay** restarts visible native reveals and the active controlled embed. It does not refit topics, recompute data or change filters.
- **Show final state** cancels native visual effects immediately, restores exact hover inspection, restores every timeline count, and returns PyVis to its stable seeded layout. The global action also stops automatic playback until Play/Replay.
- **Reduce motion** removes spatial/growth reveals and uses only a 120 ms opacity fade for native content; timeline playback and physics are stopped. **Off** removes all app-authored movement. An OS/browser reduced-motion preference takes priority over every setting and prevents playback, including manual Play.

Global controls govern the active page; native Replay targets visible units, while Pause/Show final state stop all registered native animations and controlled embeds. Local native controls affect their own chart or image collection. Speed is shared in the sidebar rather than repeated on every chart.

## Timing and behavior

| Token | Value |
|---|---|
| Quick entrance | 400 ms |
| Standard entrance | 650 ms |
| Gentle entrance | 1,000 ms |
| Data-update fade | 160 ms |
| Reduced-motion fade | 120 ms |
| Entrance easing | cubic-bezier(0.22, 1, 0.36, 1) |
| Mark stagger | Up to 60 ms, included in the entrance duration |

First encounters reveal content when it enters the viewport. Later changed figure content uses the shorter update fade; ordinary hover, pan and zoom do not trigger an entrance. Pausing blocks autoplay until Play, while Show final state stops autoplay across tab navigation. No looping decorative animations are added.

## Motion by modality

| Tab | Motion |
|---|---|
| Overview | Brief introduction and restaurant-point reveal; fixed final values and reference line |
| Trends | Bars grow from their baseline; rating line reveals left to right. Optional frame timeline uses the same speed/policy and parent controls |
| Map | Opacity reveal of the rendered map layer; restaurant coordinates and camera are not fabricated or shifted |
| Reviews & Topics | Ranked bars grow from zero; document-map points reveal without refitting or changing positions |
| Photos | Collection opacity reveal; no panning, recoloring or movement of image pixels |
| Networks | Stable Plotly network reveal, matrix fade, or explicitly enabled continuous PyVis physics |
| Methods | Brief section-heading reveal; readable text and audit values remain static |

PyVis continuous physics requires unfreezing it in the network controls and a force-directed layout. The same speed setting controls its simulation timestep (Quick 0.75 / Standard 0.5 / Gentle 0.25); it is not an interpolation duration. Circular layouts remain fixed. Show final state restores the seeded coordinates supplied by Python. Node positions are layout aids, not measurements of geography.

## Architecture and integrity

`src/motion.py` defines tokens and generated-iframe controls. `src/frontend/motion.js` is one progressive conductor, mounted through the pinned Streamlit v2 component API in `src/motion_ui.py`. It uses the browser Web Animations API on native Plotly marks rather than replacing Streamlit charts or installing a second selection bridge. Existing native Plotly callbacks, table exports and integrity validation remain.

The conductor never changes native figure data, coordinates, IDs or scales. It alters presentation styles only and restores pointer interaction on completion/final-state actions. A content hash in figure metadata identifies updates. Optional timeline frames deliberately reveal temporal subsets; their original full counts remain available and Show final state restores them. Generated embeds accept control messages only from their parent. Dataset text is not inserted into controller HTML.

One controller owns the page. Cleanup disconnects observers, cancels animations, restores pointer styles and removes injected local controls. Missing animation support falls back to the original static charts. This progressive DOM enhancement is tested against the pinned Streamlit/Plotly versions; dependency upgrades need the browser regression run.

PyVis's unused Bootstrap CDN dependencies are removed from generated HTML; its network engine remains inline. Embed titles are supplied through `st.iframe`. External map tiles are still optional and require network access; the browser QA uses the offline canvas.

## Verify locally

Python/application checks:

```bash
python -m pytest -q tests
```

Browser checks need a separate development installation, not a runtime app dependency:

```bash
npm install --no-save playwright
npx playwright install chromium
node tests/browser/motion_browser.cjs
```

Activate the Python venv first, or set `PYTHON` to its Python executable. A preinstalled browser may be selected through `CHROMIUM_EXECUTABLE`; `PLAYWRIGHT_MODULE` may point to an existing Playwright installation. The harness creates explicitly synthetic temporary inputs, launches a local Streamlit process, runs the journey, and terminates the process. It writes only temporary QA screenshots unless CITYPULSE_QA_ARTIFACTS specifies a directory.

Open `VISUAL_PREVIEW.html` to review the same native motion conductor without installing Yelp data. It is self-contained and labeled synthetic, with mode/speed/playback controls and exact tables. It is not a complete alternative to the seven-tab Streamlit application.

## Evidence and remaining limits

See TEST_RESULTS.txt and BROWSER_RESULTS.txt. The local browser journey verifies animation pause/resume/final state, unchanged native values and IDs, native selection callbacks, seven-tab rendering, live system reduced motion, timeline restoration, physics controls, and narrow-preview controls. These are synthetic-data checks, not a real Yelp feasibility or scientific-validity assessment.

Real-city performance, full photo asset availability/rights, public deployment, screen-reader use, all keyboard journeys, and a broad device/browser matrix remain unverified. Browser QA uses an offline map and cannot certify online tile services. Rapid tab changes can cancel old media requests; photo decoding and unavailable-file handling remain separately tested. Movement does not establish analytical quality: your final narrative still needs real evidence and your own interpretation.
