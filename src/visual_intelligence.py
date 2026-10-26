"""Data-driven visual storytelling. All quantities originate in the filtered analytical population."""
from __future__ import annotations
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

COLORS=['#5CD8C0','#F2B777','#9B8CEF','#76B9F1','#FF8CAB']

def temporal_story_frames(months: pd.DataFrame, steps: int = 14) -> go.Figure:
    """Animated cumulative monthly series: fixed axes prevent misleading rescaling."""
    if months.empty: return go.Figure()
    d=months.copy().reset_index(drop=True)
    x=pd.to_datetime(d['Month']).dt.strftime('%Y-%m').tolist()
    y=pd.to_numeric(d['Reviews']).fillna(0).astype(float).tolist()
    n=len(x); ix=sorted(set([0,*[round(i*(n-1)/max(steps-1,1)) for i in range(steps)],n-1]))
    def data_at(k):
        return [go.Scatter(x=x[:k+1],y=y[:k+1],mode='lines+markers',line={'color':COLORS[0],'width':3,'shape':'spline'},marker={'size':6},fill='tozeroy',fillcolor='rgba(92,216,192,.11)',name='Posted reviews',hovertemplate='%{x}<br>%{y:.0f} reviews<extra></extra>')]
    frames=[go.Frame(name=str(k),data=data_at(k)) for k in ix]
    fig=go.Figure(data=data_at(0),frames=frames)
    fig.update_layout(title='How monthly review activity unfolds',height=430,paper_bgcolor='#191F27',plot_bgcolor='#191F27',font={'color':'#ECF3F7'},margin={'t':75,'r':25,'l':50,'b':90},
      xaxis={'title':'Posting month','categoryorder':'array','categoryarray':x,'range':[-.5,n-.5],'showgrid':False,'tickangle':-45,'nticks':9},
      yaxis={'title':'Reviews posted','range':[0,max(1,max(y))*1.18],'gridcolor':'#34414D'},
      updatemenus=[{'type':'buttons','direction':'right','showactive':False,'x':0,'y':-0.23,'buttons':[
        {'label':'▶ Play / replay','method':'animate','args':[None,{'fromcurrent':False,'frame':{'duration':420,'redraw':True},'transition':{'duration':150},'mode':'immediate'}]},
        {'label':'Ⅱ Pause','method':'animate','args':[[None],{'mode':'immediate','frame':{'duration':0,'redraw':False}}]},
        {'label':'◼ Final','method':'animate','args':[[str(ix[-1])],{'mode':'immediate','frame':{'duration':0,'redraw':True}}]}
      ]}])
    return fig

def theme_landscape(rows:pd.DataFrame, top:int=14)->go.Figure:
    """Hierarchical term-frequency treemap; terms are linguistic counts, not topics/sentiment."""
    if rows.empty:return go.Figure()
    d=rows.nlargest(top,'Value').copy()
    d['Scope']='Selected review vocabulary'
    fig=px.treemap(d,path=['Scope','Term'],values='Value',color='Value',color_continuous_scale=['#294453','#2D8088','#5CD8C0'],title='Review language landscape · term frequency')
    fig.update_traces(textinfo='label+value',hovertemplate='%{label}<br>%{value} mentions<extra></extra>')
    fig.update_layout(height=490,paper_bgcolor='#191F27',font={'color':'#ECF3F7'},margin={'t':65,'l':15,'r':15,'b':15})
    return fig

def cluster_profile(grouped:pd.DataFrame)->pd.DataFrame:
    """Describe only observed geography and snapshot rating; no inferred demand."""
    if grouped.empty:return pd.DataFrame(columns=['Group','Restaurants','Mean snapshot rating','Example restaurants'])
    d=grouped[grouped['Spatial cluster']>=0].copy()
    if d.empty:return pd.DataFrame(columns=['Group','Restaurants','Mean snapshot rating','Example restaurants'])
    agg={'Restaurants':('business_id','nunique'),'Example restaurants':('name',lambda s:', '.join(s.astype(str).head(3)))}
    if 'stars' in d:agg['Mean snapshot rating']=('stars','mean')
    out=d.groupby('Spatial cluster').agg(**agg).reset_index().rename(columns={'Spatial cluster':'Group'})
    out['Group']='Spatial group '+(out['Group']+1).astype(str)
    if 'Mean snapshot rating' not in out:out['Mean snapshot rating']=float('nan')
    return out[['Group','Restaurants','Mean snapshot rating','Example restaurants']]


def review_rating_mix(reviews:pd.DataFrame,businesses:pd.DataFrame,max_businesses:int=8)->tuple[go.Figure,pd.DataFrame]:
    """100%-normalized reported-review star mixes for top supported restaurants."""
    cols=['Restaurant','Stars','Reviews','Percent','Total selected reviews']
    if reviews.empty or businesses.empty:return go.Figure(),pd.DataFrame(columns=cols)
    rated=reviews[reviews['stars'].isin([1,2,3,4,5])].copy()
    if rated.empty:return go.Figure(),pd.DataFrame(columns=cols)
    ids=rated.groupby('business_id').size().sort_values(ascending=False).head(max_businesses).index
    rated=rated[rated.business_id.isin(ids)]
    out=rated.groupby(['business_id','stars']).size().rename('Reviews').reset_index()
    totals=rated.groupby('business_id').size().rename('Total selected reviews').reset_index()
    out=out.merge(totals,on='business_id',validate='many_to_one')
    out['Percent']=100*out.Reviews/out['Total selected reviews']
    names=businesses.set_index('business_id')['name'].to_dict()
    out['Restaurant']=out.business_id.map(names).fillna(out.business_id)
    out['Stars']=out.stars.astype(int).astype(str)+'★'
    order=sorted(out['Stars'].unique())
    fig=px.bar(out,x='Percent',y='Restaurant',color='Stars',orientation='h',barmode='stack',
       color_discrete_map={'1★':'#DA7076','2★':'#DDA56B','3★':'#C8BE74','4★':'#67C3B8','5★':'#4D988F'},
       category_orders={'Stars':order},title='How are reported ratings distributed by restaurant?',
       hover_data={'Reviews':True,'Total selected reviews':True,'Percent':':.1f'})
    fig.update_layout(height=max(430,70+50*out.Restaurant.nunique()),paper_bgcolor='#191F27',plot_bgcolor='#191F27',
         font={'color':'#ECF3F7'},xaxis={'range':[0,100],'title':'Share of selected rated reviews (%)','gridcolor':'#34414D'},
         yaxis={'title':''},legend_title_text='Review rating')
    return fig,out[cols]
