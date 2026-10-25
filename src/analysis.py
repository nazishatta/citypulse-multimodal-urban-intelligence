"""Pure cohort, text, graph and image calculations."""
from __future__ import annotations
from collections import defaultdict
from itertools import combinations
import math
import numpy as np
import pandas as pd
import networkx as nx
from sklearn.feature_extraction.text import CountVectorizer,TfidfVectorizer
from sklearn.decomposition import NMF
from sklearn.cluster import DBSCAN

def select_reviews(reviews: pd.DataFrame,businesses: pd.DataFrame,categories: list[str],
                   start: str | None,end: str | None,term: str='',apply_dates: bool=False) -> tuple[pd.DataFrame,pd.DataFrame]:
    b=businesses
    if categories:
        b=b[b.categories.fillna('').map(lambda x: bool(set(s.strip() for s in x.split(',')) & set(categories)))]
    r=reviews[reviews.business_id.isin(b.business_id)].copy()
    if apply_dates:
        dates=r.date.fillna('')
        r=r[(dates!='') & (dates>=str(start)) & (dates<=str(end))]
    if term.strip():
        analyzer=CountVectorizer(stop_words='english',ngram_range=(1,2)).build_analyzer()
        tokens=analyzer(term.strip())
        # The input must be one exact token or bigram, not a free-form query.
        target=term.strip().lower()
        if target not in tokens: r=r.iloc[0:0]
        else:r=r[r.text.fillna('').map(lambda t: target in set(analyzer(t)))]
    # Keep geography/category cohort distinct from businesses with selected review evidence.
    return b.copy(),r

def monthly_reviews(r: pd.DataFrame) -> pd.DataFrame:
    d=pd.to_datetime(r.date,errors='coerce').dropna()
    if d.empty:return pd.DataFrame(columns=['Month','Reviews','Mean rating','Rated reviews'])
    x=r.assign(Month=pd.to_datetime(r.date,errors='coerce').dt.to_period('M').astype(str))
    x=x[x.Month!='NaT']
    g=x.groupby('Month').agg(Reviews=('review_id','size'),**{'Mean rating':('stars','mean'),'Rated reviews':('stars','count')})
    idx=pd.period_range(d.min(),d.max(),freq='M').astype(str)
    g=g.reindex(idx);g.index.name='Month'
    g[['Reviews','Rated reviews']]=g[['Reviews','Rated reviews']].fillna(0).astype(int)
    return g.reset_index()

def term_table(texts: list[str],limit: int=25,measure: str='documents') -> pd.DataFrame:
    try:
        v=CountVectorizer(stop_words='english',ngram_range=(1,2),max_features=10000)
        x=v.fit_transform(texts)
    except ValueError:return pd.DataFrame(columns=['Term','Value'])
    values=np.asarray((x>0).sum(axis=0) if measure=='documents' else x.sum(axis=0)).ravel()
    return pd.DataFrame({'Term':v.get_feature_names_out(),'Value':values}).sort_values(['Value','Term'],ascending=[False,True]).head(limit)

def fit_topics(reviews: pd.DataFrame,k: int=5,max_documents: int=5000) -> tuple[pd.DataFrame,pd.DataFrame]:
    r=reviews[reviews.text.fillna('').str.split().str.len()>=10].sort_values('review_id').copy()
    if len(r)>max_documents:r=r.sample(max_documents,random_state=42).sort_values('review_id')
    if len(r)<max(10,k*2):return pd.DataFrame(columns=['review_id','topic']),pd.DataFrame(columns=['topic','Label'])
    try:
        v=TfidfVectorizer(stop_words='english',max_features=6000,min_df=2,max_df=.95)
        x=v.fit_transform(r.text)
        k=min(k,x.shape[0]-1,x.shape[1])
        if k<2:raise ValueError('insufficient vocabulary')
        model=NMF(n_components=k,init='nndsvda',random_state=42,max_iter=400)
        weights=model.fit_transform(x)
    except ValueError:return pd.DataFrame(columns=['review_id','topic']),pd.DataFrame(columns=['topic','Label'])
    names=v.get_feature_names_out()
    labels=pd.DataFrame([{'topic':i,'Label':'T'+str(i+1)+' · '+' / '.join(names[c.argsort()[-4:][::-1]])} for i,c in enumerate(model.components_)])
    assigned=weights.argmax(axis=1);assigned[weights.sum(axis=1)==0]=-1
    normalized=weights/np.maximum(weights.sum(axis=1,keepdims=True),1e-12)
    ordered=np.sort(normalized,axis=1)
    if -1 in assigned:labels=pd.concat([labels,pd.DataFrame([{'topic':-1,'Label':'Unassigned · no topic weight'}])],ignore_index=True)
    return pd.DataFrame({'review_id':r.review_id.values,'topic':assigned,'representative_score':normalized.max(axis=1),'boundary_margin':ordered[:,-1]-ordered[:,-2]}),labels

def restaurant_graph(reviews: pd.DataFrame,min_shared: int=2,max_reviewers_per_user: int=50) -> tuple[nx.Graph,dict]:
    memberships=defaultdict(set)
    for row in reviews[['user_id','business_id']].itertuples(index=False):
        if isinstance(row.user_id,str) and row.user_id:memberships[row.user_id].add(row.business_id)
    g=nx.Graph();g.add_nodes_from(sorted(reviews.business_id.unique()))
    weights=defaultdict(int);excluded=0
    for bids in memberships.values():
        if len(bids)>max_reviewers_per_user:excluded+=1;continue
        for pair in combinations(sorted(bids),2):weights[pair]+=1
    for (a,b),weight in sorted(weights.items()):
        if weight>=min_shared:g.add_edge(a,b,weight=weight,distance=1/weight)
    return g,{'excluded_high_activity_reviewers':excluded,'unique_reviewer_business_edges':sum(map(len,memberships.values())),'reviewers':len(memberships),'min_shared':min_shared,'max_businesses_per_reviewer':max_reviewers_per_user}

def graph_details(g: nx.Graph) -> tuple[pd.DataFrame,dict]:
    # Bound expensive betweenness; report approximation explicitly.
    approx=len(g)>200
    bridge=nx.betweenness_centrality(g,k=min(100,len(g)) if approx else None,weight='distance',seed=42) if len(g) else {}
    communities=list(nx.community.greedy_modularity_communities(g,weight='weight')) if g.number_of_edges() else [{n} for n in sorted(g)]
    membership={n:i for i,c in enumerate(communities) for n in c}
    rows=[{'business_id':n,'Connections':g.degree(n),'Shared-reviewer strength':g.degree(n,weight='weight'),'Betweenness':bridge.get(n,0),'Community':membership[n]} for n in g]
    return pd.DataFrame(rows,columns=['business_id','Connections','Shared-reviewer strength','Betweenness','Community']),{'membership':membership,'communities':len(communities),'betweenness':'approximate, 100 sampled sources' if approx else 'exact'}

def shared_reviewers(reviews: pd.DataFrame,a: str,b: str) -> pd.DataFrame:
    users_a=set(reviews.loc[reviews.business_id==a,'user_id'].dropna())
    users_b=set(reviews.loc[reviews.business_id==b,'user_id'].dropna())
    return reviews[reviews.user_id.isin(users_a & users_b) & reviews.business_id.isin([a,b])].copy()

def spatial_clusters(b: pd.DataFrame,epsilon_m: float=500,min_samples: int=3) -> pd.DataFrame:
    x=b.dropna(subset=['latitude','longitude']).copy()
    if x.empty:x['Spatial cluster']=pd.Series(dtype=int);return x
    # Haversine expects radians ordered latitude, longitude; radius in meters.
    labels=DBSCAN(eps=epsilon_m/6371008.8,min_samples=min_samples,metric='haversine').fit_predict(np.radians(x[['latitude','longitude']].to_numpy()))
    x['Spatial cluster']=labels
    return x

def image_histogram(arr: np.ndarray) -> pd.DataFrame:
    rows=[]
    for i,color in enumerate(['Red','Green','Blue']):
        freq,_=np.histogram(arr[:,:,i],bins=32,range=(0,256))
        rows.extend({'Intensity':j*8+4,'Channel':color,'Pixel share':float(n/freq.sum())} for j,n in enumerate(freq))
    return pd.DataFrame(rows)


def review_examples(assignments: pd.DataFrame,reviews: pd.DataFrame,per_role: int=3,seed: int=42) -> pd.DataFrame:
    """Disjoint representative, low-margin boundary and seeded random examples."""
    evidence=assignments.merge(reviews[['review_id','text']],on='review_id',validate='one_to_one')
    pieces=[]
    for _,group in evidence.groupby('topic',sort=True):
        remaining=group.sort_values('review_id').copy()
        for role in ['representative','boundary','random']:
            if remaining.empty:continue
            if role=='representative':sample=remaining.sort_values(['representative_score','review_id'],ascending=[False,True]).head(per_role)
            elif role=='boundary':sample=remaining.sort_values(['boundary_margin','review_id']).head(per_role)
            else:sample=remaining.sample(min(per_role,len(remaining)),random_state=seed).sort_values('review_id')
            pieces.append(sample.assign(sample_role=role))
            remaining=remaining[~remaining.review_id.isin(sample.review_id)]
    if not pieces:return pd.DataFrame()
    return pd.concat(pieces,ignore_index=True).assign(reviewer='',label_approved='',notes='')
