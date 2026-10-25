import pandas as pd
import numpy as np
from src.analysis import select_reviews,restaurant_graph,shared_reviewers,monthly_reviews,term_table,spatial_clusters,image_histogram,graph_details

def data():
 b=pd.DataFrame([{'business_id':'a','categories':'Restaurants, Pizza'},{'business_id':'b','categories':'Restaurants, Cafe'},{'business_id':'c','categories':'Restaurants, Pizza'}])
 r=pd.DataFrame([{'review_id':'1','business_id':'a','user_id':'u','date':'2024-01-01','stars':5,'text':'great pizza pizza'},{'review_id':'2','business_id':'b','user_id':'u','date':'2024-03-01','stars':1,'text':'coffee shop'},{'review_id':'3','business_id':'a','user_id':'u','date':None,'stars':3,'text':'pizzeria'},{'review_id':'4','business_id':'c','user_id':'v','date':'2024-03-10','stars':None,'text':'pizza'}])
 return b,r

def test_categories_or_and_term_across_filters():
 b,r=data();_,s=select_reviews(r,b,['Pizza','Cafe'],None,None,'pizza')
 assert set(s.review_id)=={'1','4'}

def test_focus_does_not_mutate_population():
 b,r=data();_,s=select_reviews(r,b,[],None,None)
 focus=s[s.business_id=='a'];assert len(focus)==2 and len(s)==4 and len(r)==4

def test_missing_dates_kept_until_date_filter():
 b,r=data();assert len(select_reviews(r,b,[],None,None)[1])==4
 assert set(select_reviews(r,b,[],'2024-01-01','2024-03-31',apply_dates=True)[1].review_id)=={'1','2','4'}

def test_month_gaps_and_rating_denominator():
 _,r=data();m=monthly_reviews(r).set_index('Month')
 assert m.loc['2024-02','Reviews']==0 and pd.isna(m.loc['2024-02','Mean rating'])
 assert m.loc['2024-03','Rated reviews']==1 and m.loc['2024-03','Reviews']==2

def test_repeated_reviews_one_person_do_not_inflate_edge():
 _,r=data();g,info=restaurant_graph(r,1)
 assert g['a']['b']['weight']==1 and g.number_of_edges()==1 and info['unique_reviewer_business_edges']==3
 assert restaurant_graph(r,2)[0].number_of_edges()==0

def test_projection_high_activity_exclusion_is_reported():
 _,r=data();g,info=restaurant_graph(r,1,1)
 assert info['excluded_high_activity_reviewers']==1 and g.number_of_edges()==0

def test_pair_evidence_reconciles():
 _,r=data();p=shared_reviewers(r,'a','b')
 assert set(p.review_id)=={'1','2','3'} and p.user_id.nunique()==1

def test_document_vs_occurrence_counts():
 assert term_table(['pizza pizza','pizza'],measure='documents').set_index('Term').loc['pizza','Value']==2
 assert term_table(['pizza pizza','pizza'],measure='occurrences').set_index('Term').loc['pizza','Value']==3

def test_empty_vocabulary_and_graph():
 assert term_table(['the and']).empty
 _,r=data();g,_=restaurant_graph(r.iloc[:0],1);assert graph_details(g)[0].empty

def test_spatial_units_and_noise():
 b=pd.DataFrame({'latitude':[39,39.0001,39.0002,40],'longitude':[-75]*4})
 labels=spatial_clusters(b,100,3)['Spatial cluster'].tolist();assert labels[:3]==[0,0,0] and labels[-1]==-1

def test_rgb_histograms_normalized():
 h=image_histogram(np.zeros((10,20,3),dtype=np.uint8))
 assert np.allclose(h.groupby('Channel')['Pixel share'].sum(),1)
