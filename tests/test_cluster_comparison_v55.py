import pandas as pd
from src.cluster_comparison_v55 import build_profiles,category_composition,comparison_figure,group_takeaway


def fixture():
    return pd.DataFrame([
        {'business_id':'a','name':'Cafe A','Spatial cluster':0,'stars':4.0,'review_count':20,'categories':'Coffee, Breakfast'},
        {'business_id':'b','name':'Cafe B','Spatial cluster':0,'stars':2.0,'review_count':40,'categories':'Coffee, Bakery'},
        {'business_id':'c','name':'Cafe C','Spatial cluster':1,'stars':5.0,'review_count':12,'categories':'Bakery'},
        {'business_id':'d','name':'Isolated','Spatial cluster':-1,'stars':3.0,'review_count':5,'categories':'Diner'},
    ])


def test_group_profiles_and_noise():
    p=build_profiles(fixture())
    one=p.set_index('Group').loc['Spatial group 1']
    assert one['Restaurants']==2
    assert one['Mean snapshot stars']==3.0
    assert one['Mean snapshot review count']==30.0
    assert int(p.set_index('Group').loc['Unassigned (−1)','Restaurants'])==1


def test_alternatives_derive_from_same_observations():
    d=fixture();p=build_profiles(d)
    for kind in ['Exact size bars','Bubble profile','Treemap','Category mix']:
        fig,evidence=comparison_figure(p,d,kind,'Spatial group 1')
        assert len(fig.data)>0 and not evidence.empty
    composition=category_composition(d)
    assert abs(composition.loc[composition.Group=='Spatial group 1','Percent'].sum()-100)<0.01


def test_tell_truth_not_demand_claim():
    t,why,use=group_takeaway(build_profiles(fixture()),'Spatial group 1')
    assert '2 selected restaurants' in t
    assert 'investigation' in why
    assert 'independent' in use
