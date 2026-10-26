import pandas as pd
from src.guided_motion import topic_bubbles,synchronized_trends,cluster_entrance,player_html

def test_terms_are_observed():
 fig=topic_bubbles(pd.DataFrame({'Term':['pizza','service','queue'],'Value':[12,8,3]}))
 assert len(fig.frames)==3 and 'pizza' in list(fig.data[0].text)
 assert 'Replay' in player_html(fig)

def test_trends_frames_fixed_and_complete():
 d=pd.DataFrame({'Month':['2025-01','2025-02','2025-03'],'Reviews':[3,6,4],'Mean rating':[3.1,3.4,3.0]})
 fig=synchronized_trends(d); assert len(fig.frames)>=2
 assert fig.layout.yaxis.range[0]==0 and fig.layout.yaxis2.range[1]==5
 assert len(fig.frames[-1].data[0].x)==3

def test_cluster_phases_include_noise():
 d=pd.DataFrame({'latitude':[40,40.01,40.2],'longitude':[-75,-75.01,-74.7],'name':['a','b','c'],'Spatial cluster':[0,0,-1]})
 fig=cluster_entrance(d); assert len(fig.frames)==3
 assert 'Unassigned' in fig.frames[-1].layout.title.text
