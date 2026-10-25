"""Synthetic design-preview validation; no claims about actual Yelp observations."""
from src.demo_preview import ensure_preview
from src.data import load_snapshot

def test_preview_prepares_traceable_synthetic_snapshot(tmp_path):
    snapshot,photos=ensure_preview(tmp_path)
    businesses,reviews,images,audit=load_snapshot(str(snapshot))
    assert len(businesses)==24
    assert len(reviews)>350
    monthly=reviews.assign(month=reviews.date.str[:7]).groupby("month").size()
    assert monthly.size==48
    assert monthly.nunique()>4
    assert len(images)==24
    assert photos.is_dir()
    assert all(businesses.name.str.startswith('DEMO'))
    assert audit['scope']['city']=='Preview City'
    assert audit['metrics']['observed_months']>=24
    assert snapshot == ensure_preview(tmp_path)[0]
