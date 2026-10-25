**Motion revision v4:** Open `VISUAL_PREVIEW.html` for a synthetic animated chart preview. Read [docs/MOTION_SYSTEM_V4.md](docs/MOTION_SYSTEM_V4.md) for shared controls, timing, accessibility, browser checks and limits. Valid v2/v3 snapshots remain compatible.

# Release status

Implemented software + tested preparation pipeline. No empirical Yelp-data approval and no public deployment.

Input audit kit preserved under original_audit_kit; its old audit script is reference only. Current workflow: START_HERE.md → scripts/prepare_data.py → optional scripts/build_topics.py → app.py.

The original release passed 33 tests; see docs/TEST_RESULTS.txt for this revision’s complete result. No real dataset/photos included. Original tutorial examples have been translated into actual-data operations, not substituted with karate-club/digits demo results.

Scientific findings, dataset suitability, accessibility and grade are not certified. Weeks 11–14 remain the final-project roadmap.
