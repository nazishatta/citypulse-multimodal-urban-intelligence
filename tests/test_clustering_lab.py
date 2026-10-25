import pandas as pd
from src.clustering_lab import geographic_summary,shared_audience_summary,text_group_summary


def test_spatial_ids_preserved_and_noise_explained():
    b=pd.DataFrame({'business_id':['a','b','c'],'latitude':[39.95,39.9501,40.4],'longitude':[-75.16,-75.1601,-76.]})
    grouped,counts=geographic_summary(b,200,2)
    assert set(grouped.business_id)=={'a','b','c'}
    assert -1 in set(grouped['Spatial cluster'])
    assert counts.Restaurants.sum()==3


def test_network_groups_only_use_real_shared_reviewers():
    r=pd.DataFrame({'user_id':['u1','u1','u2','u2','u3'],'business_id':['a','b','a','b','c']})
    g,ranks,info=shared_audience_summary(r,2,50)
    assert g['a']['b']['weight']==2
    assert 'c' in g and g.degree('c')==0
    assert len(ranks)==3


def test_text_assignments_respect_review_selection():
    reviews=pd.DataFrame({'review_id':['r1','r2']})
    assignments=pd.DataFrame({'review_id':['r1','r2','r3'],'topic':[0,1,0]})
    labels=pd.DataFrame({'topic':[0,1],'Label':['service','food']})
    out,n=text_group_summary(reviews,assignments,labels)
    assert n==2 and out.Reviews.sum()==2
