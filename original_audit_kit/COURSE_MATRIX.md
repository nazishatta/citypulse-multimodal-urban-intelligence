# Explicit lecture-to-feature coverage

| Lecture | Topic | Concrete deliverable | Evidence |
|---|---|---|---|
| 1 | Foundations & Setup | Dataset schema, diagnostics, reproducible local setup | audit JSON, README |
| 2 | Grammar of Graphics & Design | Appropriate marks/encodings, labels, contrast, annotations | manual accessibility checklist |
| 3 | Tabular & Multivariate Data | Ratings vs review counts, categorical distributions, multivariate plot | labeled charts, denominators |
| 4 | Time-Series Data | Monthly reviews/time filtering, no future leakage | date coverage audit |
| 5 | Streamlit Interactive Apps | Multiple tabs, filters, caching, state | UI smoke tests |
| 6 | Graph & Network | NetworkX degree/community/betweenness, PyVis, adjacency | repeated reviewers and projection audit |
| 7 | Text Data | CountVectorizer + BERTopic/UMAP with interpretation | nonempty reviews, topic evidence |
| 8 | Image Data | Montage, RGB histograms, photo inspection | actual authorized images and joins |
| 9 | Map Visualization I | Coordinates, CRS, point map | valid lat/lon and map tests |
| 10 | Map Visualization II | Choropleth/density, normalization, spatial join | polygon source and denominators |
| 11 | Consuming APIs & Endpoints | Documented endpoint, refresh/error handling | final only |
| 12 | FastAPI / Flask | Serve aggregates/predictions via backend | final only |
| 13 | ML/NLP Visualization | Evaluated prediction/explanations and uncertainty | final only |
| 14 | Deployment, Ethics & Workshop | Reproducible hosted app and transparent limitations | final only |

Do not claim the midterm needs Weeks 11–14; these are planned future extensions.
