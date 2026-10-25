import pandas as pd
from src.stories import trend_story,review_story,cluster_story
def test_trend_story_uses_observed_peak():
    data=pd.DataFrame({'Month':['2024-01','2024-02'],'Reviews':[2,8]})
    assert '2024-02' in trend_story(data)['headline']
    assert '8 posted reviews' in trend_story(data)['evidence']
def test_review_story_does_not_claim_sentiment():
    d=pd.DataFrame({'Term':['service','food'],'Value':[10,3]})
    assert 'not sentiment' in review_story(d,20,'documents')['caution']
def test_empty_cluster_has_no_fabricated_groups():
    d=pd.DataFrame(columns=['Spatial cluster','Restaurants'])
    assert '0 geographic groups' in cluster_story(d,24,650,3)['headline']
from src.stories import term_by_restaurant

def test_term_restaurant_comparison_uses_per_business_denominators():
    r=pd.DataFrame({'business_id':['a','a','b'], 'text':['great service','bad food','great service']})
    b=pd.DataFrame({'business_id':['a','b'], 'name':['Alpha','Beta']})
    ans=term_by_restaurant(r,b,['great'])
    assert ans.set_index('Restaurant').loc['Alpha','Percent']==50
    assert ans.set_index('Restaurant').loc['Beta','Percent']==100
