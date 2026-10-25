"""Shared visual language; figure builders never change the analytical population."""
from __future__ import annotations
import html
import json
import textwrap
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

INK='#172B40'
MUTED='#536579'
TEAL='#007C83'
AMBER='#A65F10'
COLORS=['#007C83','#A65F10','#6554A4','#276A9B','#A63669','#367A35','#536878','#884A24']
SEQUENTIAL=['#F0F5F5','#C9E4E2','#88C4C0','#439F9D','#007C83','#004E57']

CSS='''<style>
.stApp {background:#F4F6F8;color:#172B40}
.block-container {max-width:1450px;padding-top:2.2rem;padding-bottom:3rem}
h1,h2,h3 {color:#172B40;letter-spacing:-.025em}
h2 {font-size:1.6rem!important} h3 {font-size:1.25rem!important}
[data-testid="stSidebar"] {background:#FFFFFF;border-right:1px solid #DCE3EA}
[data-testid="stMetric"] {background:#FFFFFF;border:1px solid #DCE3EA;border-top:3px solid #007C83;border-radius:10px;padding:15px 18px;min-height:112px}
[data-testid="stMetricLabel"] {color:#536579;font-weight:600}
[data-testid="stMetricValue"] {color:#172B40;font-variant-numeric:tabular-nums}
[data-testid="stPlotlyChart"] {background:#FFFFFF;border:1px solid #DCE3EA;border-radius:10px;padding:6px}
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, [data-testid="stCaptionContainer"] span {color:#536579!important}
[data-testid="stTabs"] [role="tablist"] {gap:1rem;border-bottom:1px solid #CFD9E2;margin-top:1.2rem}
[data-testid="stTabs"] [role="tab"] {padding:12px 2px;font-weight:600}
[data-testid="stTabs"] [aria-selected="true"] {color:#006A71}
[data-testid="stExpander"] {background:#FFFFFF;border-radius:8px}
.citypulse-hero {background:#132C40;color:#FFFFFF;border-radius:14px;padding:30px 34px;margin-bottom:24px;border-left:5px solid #70C7C5}
.citypulse-hero .eyebrow {color:#ACD9DC;font-size:.76rem;letter-spacing:.16em;font-weight:700;margin-bottom:10px}
.citypulse-hero h1 {color:#FFFFFF;font-size:3.2rem;line-height:1.1;margin:0 0 12px;font-weight:750}
.citypulse-hero p {color:#E2EDF3;max-width:800px;font-size:1.05rem;margin:0;line-height:1.55}
.citypulse-note {background:#E8F2F2;border-left:3px solid #007C83;padding:13px 16px;border-radius:0 6px 6px 0;margin:12px 0 20px;color:#173E48}
.citypulse-kicker {font-size:.75rem;letter-spacing:.12em;color:#536579;font-weight:700;margin-top:1.5rem}
.citypulse-filter {display:inline-block;background:#FFFFFF;border:1px solid #CAD6DF;border-radius:5px;padding:4px 9px;margin:3px 5px 3px 0;font-size:.8rem;color:#334C60}
button:focus-visible,a:focus-visible,input:focus-visible,[role="tab"]:focus-visible {outline:3px solid #007C83!important;outline-offset:3px!important}
@media(max-width:700px) {.block-container{padding:1rem}.citypulse-hero{padding:22px}.citypulse-hero h1{font-size:2.4rem}[data-testid="stTabs"] [role="tablist"]{gap:.85rem}}
@media(prefers-reduced-motion:reduce) {.stApp *, .stApp *::before,.stApp *::after {scroll-behavior:auto!important;animation:none!important;transition:none!important}}
</style>'''
HERO='''<section class="citypulse-hero" aria-label="CityPulse research explorer">
<div class="eyebrow">URBAN EXPERIENCE ATLAS · MULTIMODAL RESEARCH</div>
<h1>CityPulse</h1><p>Read the city through its places, reviews and connections.<br>One study population. Five complementary perspectives.</p></section>'''

def wrap_label(value: object,width: int=28) -> str:
    return '<br>'.join(html.escape(line) for line in textwrap.wrap(str(value),width=width,break_long_words=True))

def style_figure(fig: go.Figure,height: int | None=None) -> go.Figure:
    """Honest axes, readable labels and a consistent light canvas."""
    types={t.type for t in fig.data}
    is_matrix=bool(types & {'heatmap','image'})
    is_map=bool(types & {'scattermap','choropleth'})
    horizontal=any(t.type=='bar' and t.orientation=='h' for t in fig.data)
    if height is None:height=max(430,min(1000,160+30*max((len(t.y) for t in fig.data if t.type=='bar' and t.orientation=='h'),default=0))) if horizontal else (620 if is_matrix else 450)
    fig.update_layout(template='plotly_white',height=height,paper_bgcolor='#FFFFFF',plot_bgcolor='#FFFFFF',
        font=dict(family='Arial, sans-serif',size=13,color=INK),
        title=dict(x=.035,xanchor='left',y=.96,font=dict(size=17,color=INK)),
        margin=dict(l=35,r=35,t=85,b=75),
        legend=dict(title_text='',orientation='h',y=-.2,x=0,font=dict(size=12)),
        hoverlabel=dict(bgcolor=INK,font=dict(color='#FFFFFF',size=13)),
        colorway=COLORS,modebar=dict(bgcolor='#FFFFFF',color=MUTED,activecolor=TEAL))
    if not is_map:
        fig.update_xaxes(showline=False,zeroline=False,gridcolor='#E7EDF2',automargin=True,title_font=dict(size=13),tickfont=dict(size=12))
        fig.update_yaxes(showline=False,zeroline=False,gridcolor='#E7EDF2',automargin=True,title_font=dict(size=13),tickfont=dict(size=12))
    for trace in fig.data:
        if trace.type=='bar':
            trace.update(marker_line_width=0)
            if trace.orientation=='h':fig.update_xaxes(rangemode='tozero',tickformat=',d');fig.update_yaxes(showgrid=False)
            else:fig.update_yaxes(rangemode='tozero',tickformat=',d');fig.update_xaxes(showgrid=False)
    return fig

def overview_figure(agg: pd.DataFrame,mean: float | None,focus: str='') -> go.Figure:
    colors=[AMBER if bid==focus else TEAL for bid in agg.business_id]
    fig=go.Figure(go.Scatter(x=agg['Selected reviews'],y=agg['Mean selected rating'],mode='markers',
        customdata=agg[['business_id','name']],marker=dict(color=colors,size=11,line=dict(color='#FFFFFF',width=1.4),opacity=.85),
        hovertemplate='%{customdata[1]}<br>%{x:,} selected reviews<br>Mean selected rating %{y:.2f}<extra></extra>'))
    if focus in set(agg.business_id):
        focused=agg[agg.business_id==focus]
        fig.add_trace(go.Scatter(x=focused['Selected reviews'],y=focused['Mean selected rating'],customdata=focused[['business_id','name']],mode='markers',marker=dict(color=AMBER,size=16,symbol='diamond',line=dict(color='#FFFFFF',width=1.5)),name='Focused restaurant',hovertemplate='%{customdata[1]}<br>%{x:,} selected reviews<br>Mean %{y:.2f}<extra>Focused restaurant</extra>'))
    fig.data[0].showlegend=False
    fig.update_layout(showlegend=bool(focus),title='Restaurant review comparison',xaxis_title='Selected reviews per restaurant',yaxis_title='Mean selected review rating')
    fig.update_yaxes(range=[.8,5.2],tickvals=[1,2,3,4,5]);fig.update_xaxes(rangemode='tozero',tickformat=',d')
    if mean is not None and np.isfinite(mean):fig.add_hline(y=mean,line_dash='dot',line_color=MUTED,annotation_text=f'Selected review mean · {mean:.2f}',annotation_position='top left',annotation_font_color=MUTED)
    return fig

def monthly_figure(counts: pd.DataFrame,rating: bool=False) -> go.Figure:
    x=pd.to_datetime(counts.Month)
    if rating:
        fig=go.Figure(go.Scatter(x=x,y=counts['Mean rating'],mode='lines+markers',connectgaps=False,line=dict(color=TEAL,width=2.5),marker=dict(size=5),customdata=counts[['Rated reviews']],hovertemplate='%{x|%b %Y}<br>Mean %{y:.2f}<br>%{customdata[0]:,} rated reviews<extra></extra>'))
        fig.update_yaxes(range=[1,5],tickvals=[1,2,3,4,5],title='Mean selected review rating')
        fig.update_layout(title='Mean reported rating')
    else:
        peak=int(counts.Reviews.to_numpy().argmax())
        colors=[AMBER if i==peak else TEAL for i in range(len(counts))]
        fig=go.Figure(go.Bar(x=x,y=counts.Reviews,marker_color=colors,hovertemplate='%{x|%b %Y}<br>%{y:,} posted reviews<extra></extra>'))
        fig.update_yaxes(title='Posted reviews',rangemode='tozero')
        fig.update_layout(title='Monthly posted reviews',bargap=.2)
    ticks=np.unique(np.linspace(0,len(x)-1,min(8,len(x))).astype(int))
    fig.update_xaxes(title=None,tickmode='array',tickvals=x.iloc[ticks],ticktext=[v.strftime('%b<br>%Y') for v in x.iloc[ticks]])
    return fig

def ranked_figure(frame: pd.DataFrame,label: str,value: str,title: str,id_column: str) -> go.Figure:
    ordered=frame.sort_values([value,label],ascending=[True,False]).copy()
    fig=go.Figure(go.Bar(x=ordered[value],y=ordered[label].astype(str),orientation='h',customdata=ordered[[id_column]],marker_color=TEAL,
        text=ordered[value],texttemplate='%{text:,}',textposition='outside',cliponaxis=False,
        hovertemplate='%{y}<br>%{x:,}<extra></extra>'))
    fig.update_layout(title=title,xaxis_title=('Count' if value=='Value' else value),yaxis_title=None)
    fig.update_yaxes(tickmode='array',tickvals=ordered[label].astype(str),ticktext=[wrap_label(v) for v in ordered[label]])
    fig.update_xaxes(range=[0,max(1,float(ordered[value].max())*1.18)] if len(ordered) else [0,1])
    return fig

def adjacency_figure(matrix: np.ndarray,ids: list[str],lookup: dict) -> go.Figure:
    # Stable short IDs retain readability; original restaurant names appear on hover/table.
    labels=[f'R{i+1:02}' for i in range(len(ids))]
    custom=np.empty((len(ids),len(ids),2),dtype=object)
    for i,a in enumerate(ids):
        for j,b in enumerate(ids):custom[i,j]=[lookup[a],lookup[b]]
    fig=go.Figure(go.Heatmap(z=matrix,x=labels,y=labels,zmin=0,colorscale=SEQUENTIAL,customdata=custom,
        colorbar=dict(title=dict(text='Shared<br>reviewers'),thickness=14),
        hovertemplate='%{customdata[0]}<br>%{customdata[1]}<br>%{z:,} shared reviewers<extra></extra>'))
    fig.update_layout(title='Shared-reviewer connection matrix',xaxis_title='Restaurant key (see table)',yaxis_title='Restaurant key (see table)')
    fig.update_yaxes(autorange='reversed',scaleanchor='x',scaleratio=1)
    return fig

def timeline_html(counts: pd.DataFrame,settings=None) -> str:
    """Temporal frames use shared timing. Shared iframe adapter supplies all controls."""
    if counts.empty:return ''
    from src.motion import MotionSettings
    settings=settings or MotionSettings()
    frame_cap=max(1,min(32,settings.payload()['duration']//16))
    indexes=np.unique(np.linspace(0,len(counts)-1,min(frame_cap,len(counts))).astype(int))
    x=counts.Month.tolist();values=counts.Reviews.tolist()
    fig=go.Figure(go.Bar(x=x,y=values,marker_color=TEAL))
    fig.frames=[go.Frame(name=str(i),data=[go.Bar(x=x,y=[v if j<=i else None for j,v in enumerate(values)],marker_color=TEAL)]) for i in indexes]
    fig.update_layout(title='Temporal reveal · posted reviews',yaxis=dict(range=[0,max(1,max(values)*1.15)],title='Posted reviews'),xaxis=dict(title='Review posting month',nticks=8))
    style_figure(fig,440)
    snippet=fig.to_html(full_html=False,include_plotlyjs=True,auto_play=False,div_id='citypulse-timeline',config={'displaylogo':False,'responsive':True})
    # No independent autoplay loop: one shared controller coordinates this view.
    return snippet+'<script>window.citypulseFinalCounts='+json.dumps(values)+';window.citypulseFrameNames='+json.dumps([f.name for f in fig.frames])+';</script>'
