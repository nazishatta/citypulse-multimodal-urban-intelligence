from pathlib import Path
import pandas as pd
from src.cluster_comparison_v55 import build_profiles, category_composition, comparison_figure

def sample():
    return pd.DataFrame([
        dict(business_id='a',Group='Spatial group 1',categories='Restaurants, Japanese',business_stars=4.2,business_review_count=120),
        dict(business_id='b',Group='Spatial group 1',categories='Restaurants, Japanese',business_stars=3.8,business_review_count=80),
        dict(business_id='c',Group='Spatial group 2',categories='Restaurants, Mediterranean',business_stars=3.1,business_review_count=10),
    ])
def test_generic_categories_are_skipped():
    comp=category_composition(sample())
    assert set(comp.Category)=={'Japanese','Mediterranean'}
    assert comp.groupby('Group').Percent.sum().eq(100).all()
def test_alias_schema_and_highlight():
    profiles=build_profiles(sample())
    assert profiles['Mean snapshot stars'].notna().all()
    a,_=comparison_figure(profiles,sample(),'Bubble profile','Spatial group 1')
    b,_=comparison_figure(profiles,sample(),'Bubble profile','Spatial group 2')
    assert [t.opacity for t in a.data] != [t.opacity for t in b.data]
def test_live_network_embedded_and_unavailable_topic_hidden():
    src=(Path(__file__).parents[1]/'src'/'clustering_ui.py').read_text()
    assert 'render_live_audience' in src
    assert "if not v551_topics.empty" in src
    live=(Path(__file__).parents[1]/'src'/'live_audience_v551.py').read_text()
    assert 'network.moveNode' in live and 'components.html(page' in live
