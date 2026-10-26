"""Autoplay guided stories for selected data; never estimates missing business outcomes."""
from __future__ import annotations
import html
import json
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

DARK='#191F27'; TEAL='#5CD8C0'; AMBER='#F2B777'; PURPLE='#9B8CEF'

def player_html(fig:go.Figure, *, delay:int=820, autoplay:bool=True, loop:bool=False)->str:
    """Embed one independently controllable Plotly scene. No continuous rerun timers."""
    figure=pio.to_html(fig,full_html=False,include_plotlyjs=True,auto_play=False,config={'displaylogo':False,'responsive':True})
    frames=[f.name for f in fig.frames]
    if not frames:return figure
    names=json.dumps(frames)
    return f"""<html><head><style>body{{margin:0;background:{DARK};color:#EAF2F4;font:14px system-ui}}
.controls{{display:flex;gap:8px;flex-wrap:wrap;padding:8px 10px;align-items:center}}button{{background:#253440;border:1px solid #48606b;color:#eefaff;border-radius:8px;padding:9px 14px;cursor:pointer}}button:focus-visible{{outline:2px solid {TEAL}}}
progress{{width:160px;accent-color:{TEAL}}}small{{color:#aebfc9}}</style></head><body>{figure}<div class="controls">
<button id="play">▶ Play</button><button id="pause">Ⅱ Pause</button><button id="again">↺ Replay</button><button id="final">Show final state</button><progress id="progress" value="0" max="{max(len(frames)-1,1)}"></progress><small id="status" aria-live="polite">Ready</small></div>
<script>(function(){{const gd=document.querySelector('.plotly-graph-div');const names={names};let at=0,timer=null;const delay={int(delay)},loop={str(loop).lower()};let repeat=null;const bar=document.querySelector('#progress'),status=document.querySelector('#status');
function stop(){{if(timer!==null)clearTimeout(timer);if(repeat!==null)clearTimeout(repeat);timer=null;repeat=null;}}function show(i){{at=i;Plotly.animate(gd,[names[i]],{{mode:'immediate',frame:{{duration:0,redraw:true}},transition:{{duration:0}}}});bar.value=i;status.textContent='Step '+(i+1)+' of '+names.length;}}
function play(){{stop();function tick(){{if(at>=names.length-1){{timer=null;if(loop)repeat=setTimeout(()=>{{show(0);play();}},2600);return;}}show(at+1);timer=setTimeout(tick,delay);}}timer=setTimeout(tick,delay);}}
document.querySelector('#play').onclick=play;document.querySelector('#pause').onclick=stop;document.querySelector('#again').onclick=()=>{{stop();show(0);play();}};document.querySelector('#final').onclick=()=>{{stop();show(names.length-1);}};
const reduce=window.matchMedia&&window.matchMedia('(prefers-reduced-motion: reduce)').matches;window.addEventListener('pagehide',stop);setTimeout(()=>{{show(reduce||!{str(autoplay).lower()}?names.length-1:0);if(!reduce&&{str(autoplay).lower()})play();}},180);
}})();</script></body></html>"""

def render_player(fig,*,key:str,height:int=540,delay:int=820,autoplay:bool=True,loop:bool=False):
    if not fig.frames:return
    import streamlit.components.v1 as components
    components.html(player_html(fig,delay=delay,autoplay=autoplay,loop=loop),height=height,scrolling=False)

def topic_bubbles(terms:pd.DataFrame,max_terms:int=12)->go.Figure:
    """Stages progressively reveal term bubbles; frequency means appearances, not positive sentiment."""
    if terms.empty:return go.Figure()
    d=terms.nlargest(max_terms,'Value').reset_index(drop=True)
    vals=d['Value'].astype(float).clip(lower=0); top=max(vals.max(),1)
    xs=[];ys=[];sizes=[];labels=[]
    # Fixed non-overlapping grid for readable, comparable bubble size rather than fake physics.
    for i,row in d.iterrows():
        xs.append((i%4)*3+1.3);ys.append(6-(i//4)*2.1);sizes.append(24+48*np.sqrt(float(row['Value'])/top));labels.append(str(row['Term']))
    def trace(k):
        colors=[TEAL if i<k else '#44515e' for i in range(len(d))]
        opacity=[.92 if i<k else .12 for i in range(len(d))]
        return go.Scatter(x=xs,y=ys,mode='markers+text',text=labels,textposition='bottom center',
            textfont=dict(size=12,color='#ebf4f4'),marker=dict(size=sizes,color=colors,opacity=opacity,line=dict(color='#c2f8ed',width=1)),
            customdata=list(zip([int(v) for v in vals],labels)),hovertemplate='%{customdata[1]}: %{customdata[0]} appearances<extra></extra>',showlegend=False)
    frames=[go.Frame(name=str(i),data=[trace(i)]) for i in range(1,len(d)+1)]
    fig=go.Figure(data=[trace(1)],frames=frames)
    fig.update_layout(title='Language patterns emerge · selected review terms',height=445,margin=dict(t=65,l=15,r=15,b=20),paper_bgcolor=DARK,plot_bgcolor=DARK,font=dict(color='white'),xaxis=dict(visible=False,range=[0,11]),yaxis=dict(visible=False,range=[-1,7]),showlegend=False)
    return fig

def synchronized_trends(months:pd.DataFrame,max_frames:int=18)->go.Figure:
    """Volume and rating reveal on the same calendar frames; fixed y-scales."""
    if months.empty:return go.Figure()
    d=months.reset_index(drop=True).copy();n=len(d);x=d.Month.astype(str).tolist();y=pd.to_numeric(d.Reviews,errors='coerce').fillna(0).tolist()
    rating_col=next((c for c in ['Mean rating','Mean Rating','Rating','rating','Mean selected rating'] if c in d.columns),None)
    rating=pd.to_numeric(d[rating_col],errors='coerce').tolist() if rating_col else [float('nan')]*n
    indices=sorted(set([0,*[round(i*(n-1)/max(max_frames-1,1)) for i in range(max_frames)],n-1]))
    def state(k):
        return [go.Bar(x=x[:k+1],y=y[:k+1],marker_color=TEAL,name='Review volume',xaxis='x',yaxis='y'),
                go.Scatter(x=x[:k+1],y=rating[:k+1],mode='lines+markers',line=dict(color=AMBER,width=3),name='Mean rating',xaxis='x2',yaxis='y2')]
    fig=go.Figure(data=state(0),frames=[go.Frame(name=str(k),data=state(k)) for k in indices])
    fig.update_layout(title='One timeline · reviews posted and mean reported rating',height=455,paper_bgcolor=DARK,plot_bgcolor=DARK,font=dict(color='white'),margin=dict(t=72,b=55,l=48,r=20),barmode='group',
        xaxis=dict(domain=[0,.48],categoryorder='array',categoryarray=x,nticks=6,tickangle=-30,title='Posting month'),
        xaxis2=dict(domain=[.56,1],categoryorder='array',categoryarray=x,nticks=6,tickangle=-30,title='Posting month'),
        yaxis=dict(range=[0,max(1,max(y))*1.2],title='Posted reviews',gridcolor='#33414d'),
        yaxis2=dict(range=[1,5],title='Mean reported rating',gridcolor='#33414d',anchor='x2'),legend=dict(orientation='h',y=1.07))
    return fig

def cluster_entrance(grouped:pd.DataFrame)->go.Figure:
    """Staged cluster coloring; geographic positions stay fixed, no invented clustering."""
    d=grouped.dropna(subset=['latitude','longitude']).reset_index(drop=True)
    if d.empty:return go.Figure()
    group=d['Spatial cluster'].astype(int).tolist();ids=sorted(set(g for g in group if g>=0));palette=[TEAL,AMBER,PURPLE,'#76B9F1','#FF8CAB'];
    phases=['All mapped restaurants']+[f'Group {g+1}' for g in ids]+['Unassigned locations']
    def trace(stage):
        if stage==0:colors=['#8194A2']*len(d)
        else:
            revealed=set(ids[:min(stage,len(ids))]); colors=[palette[g%len(palette)] if g in revealed else ('#75818e' if stage==len(phases)-1 and g==-1 else '#344652') for g in group]
        return go.Scatter(x=d.longitude,y=d.latitude,mode='markers',text=d.name,marker=dict(size=13,color=colors,line=dict(color='#e3eff3',width=.7)),hovertemplate='%{text}<extra></extra>',showlegend=False)
    fig=go.Figure(data=[trace(0)],frames=[go.Frame(name=str(i),data=[trace(i)],layout=go.Layout(title=f'Spatial groups · {name}')) for i,name in enumerate(phases)])
    fig.update_layout(title='Spatial groups · all mapped restaurants',height=430,margin=dict(t=60,l=45,r=20,b=45),paper_bgcolor=DARK,plot_bgcolor=DARK,font=dict(color='white'),xaxis=dict(title='Longitude',range=[d.longitude.min()-.015,d.longitude.max()+.015],gridcolor='#33414d'),yaxis=dict(title='Latitude',range=[d.latitude.min()-.015,d.latitude.max()+.015],gridcolor='#33414d'))
    return fig
