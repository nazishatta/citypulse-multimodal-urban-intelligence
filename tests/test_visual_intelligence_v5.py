import pandas as pd
from src.visual_intelligence import temporal_story_frames,theme_landscape,cluster_profile,review_rating_mix

def test_temporal_frames_preserve_final_counts_and_fixed_axis():
    d=pd.DataFrame({'Month':['2022-01','2022-02','2022-03'],'Reviews':[3,9,4]})
    fig=temporal_story_frames(d)
    assert len(fig.frames)>=2
    assert list(fig.frames[-1].data[0].y)==[3.,9.,4.]
    assert fig.layout.yaxis.range[1]>9
    assert fig.layout.xaxis.range[1]==2.5

def test_review_treemap_uses_real_values():
    d=pd.DataFrame({'Term':['service','food'],'Value':[12,5]})
    fig=theme_landscape(d)
    assert sorted(fig.data[0].values) == [5,12,17]  # parent node contains child totals

def test_cluster_profiles_no_noise_as_group():
    d=pd.DataFrame({'Spatial cluster':[0,0,-1],'business_id':['a','b','c'],'name':['A','B','C'],'stars':[4,2,1]})
    p=cluster_profile(d)
    assert len(p)==1
    assert p.iloc[0]['Restaurants']==2
    assert p.iloc[0]['Mean snapshot rating']==3


def test_rating_mix_denominators_and_percents():
    r=pd.DataFrame({'business_id':['a','a','a','b'],'stars':[1,5,5,3]})
    b=pd.DataFrame({'business_id':['a','b'],'name':['Alpha','Beta']})
    fig,table=review_rating_mix(r,b)
    assert len(fig.data)==3
    assert round(table.loc[table.Restaurant=='Alpha','Percent'].sum())==100
    assert table.loc[table.Restaurant=='Alpha','Total selected reviews'].unique().tolist()==[3]
