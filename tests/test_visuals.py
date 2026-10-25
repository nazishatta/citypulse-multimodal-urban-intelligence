"""Verify visual encodings preserve values and communicate their scales."""
import numpy as np
import pandas as pd
from src.visuals import overview_figure,monthly_figure,ranked_figure,adjacency_figure,style_figure,timeline_html,COLORS

def test_overview_keeps_ids_and_fixed_rating_scale():
 a=pd.DataFrame({'business_id':['a','b'],'name':['First','Second'],'Selected reviews':[3,7],'Mean selected rating':[2.,4.]})
 f=style_figure(overview_figure(a,3.4,'b'))
 assert list(f.data[0].x)==[3,7]
 assert list(f.data[0].customdata[:,0])==['a','b']
 assert f.layout.yaxis.range==(.8,5.2)
 assert f.data[0].marker.color[0]!=f.data[0].marker.color[1]
 assert f.layout.shapes[0].y0==3.4

def counts():return pd.DataFrame({'Month':['2024-01','2024-02','2024-03'],'Reviews':[4,0,6],'Mean rating':[2.5,np.nan,4.],'Rated reviews':[4,0,5]})

def test_monthly_views_keep_missing_month_and_rating_gap():
 f=style_figure(monthly_figure(counts()));r=style_figure(monthly_figure(counts(),rating=True))
 assert list(f.data[0].y)==[4,0,6]
 assert f.layout.yaxis.rangemode=='tozero'
 assert r.layout.yaxis.range==(1,5)
 assert r.data[0].connectgaps is False
 assert np.isnan(r.data[0].y[1])

def test_long_ranked_labels_wrap_without_changing_selection_ids():
 a=pd.DataFrame({'Label':['an extremely long provisional topic label with several terms','short'],'Reviews':[8,20],'topic':[1,2]})
 f=style_figure(ranked_figure(a,'Label','Reviews','Topics','topic'))
 assert list(f.data[0].x)==[8,20]
 assert list(f.data[0].customdata[:,0])==[1,2]
 assert '<br>' in f.layout.yaxis.ticktext[0]
 assert f.layout.xaxis.range[0]==0

def test_matrix_keys_have_full_hover_names_and_zero_baseline():
 a=np.array([[0,3],[3,0]])
 f=style_figure(adjacency_figure(a,['a','b'],{'a':'First','b':'Second'}))
 assert f.data[0].zmin==0
 assert list(f.data[0].x)==['R01','R02']
 assert list(f.data[0].customdata[0,1])==['First','Second']
 np.testing.assert_array_equal(f.data[0].z,a)
 assert f.layout.yaxis.scaleanchor=='x'

def test_replay_is_optional_fixed_scale_and_checks_reduced_motion():
 from src.motion import MotionSettings,child_motion_html
 markup=child_motion_html(timeline_html(counts()),MotionSettings(),'timeline')
 assert 'prefers-reduced-motion: reduce' in markup
 assert "policy.mode==='Follow system'&&!media.matches" in markup
 assert 'Replay' in markup and 'Pause' in markup
 assert '"range":[0,6.8999999999999995]' in markup or '"range":[0,6.9]' in markup
 assert timeline_html(counts().iloc[0:0])==''
