"""CityPulse: a real-data, coordinated multimodal research explorer."""
from __future__ import annotations
import html,json,os,hashlib
from pathlib import Path
import numpy as np
import pandas as pd
import networkx as nx
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
from src.motion import MotionSettings,MODES,SPEEDS,child_motion_html
from src.motion_ui import render_motion
from src.visuals import CSS,HERO,COLORS,SEQUENTIAL,style_figure,overview_figure,monthly_figure,ranked_figure,adjacency_figure,timeline_html
from src.data import load_snapshot,validate_snapshot,load_topics,resolve_photo,IntegrityError
from src.clustering_ui import render_clustering_lab
from src.stories import trend_story,review_story,term_by_restaurant
from src.story_ui import render_story
from src.visual_intelligence import temporal_story_frames,theme_landscape,review_rating_mix
from src.guided_motion import render_player,topic_bubbles,synchronized_trends
from src.analysis import select_reviews,monthly_reviews,term_table,restaurant_graph,graph_details,shared_reviewers,spatial_clusters,image_histogram

ROOT=Path(__file__).resolve().parent
st.set_page_config(page_title='CityPulse · Urban Experience Atlas',page_icon='◉',layout='wide')
st.markdown(CSS,unsafe_allow_html=True)
px.defaults.template='plotly_dark'
px.defaults.color_discrete_sequence=COLORS

@st.cache_data(show_spinner=False)
def cached_load(path: str,stamp: tuple):return load_snapshot(path)
@st.cache_data(show_spinner=False)
def graph_cache(rows: pd.DataFrame,minimum: int,maximum: int):return restaurant_graph(rows,minimum,maximum)

DEFAULTS={'categories':[],'use_dates':False,'term':'','focus':'','topic_filter':[],'network_focus':'','pair':''}
def reset():
    for key,value in DEFAULTS.items():st.session_state[key]=value.copy() if isinstance(value,list) else value
    st.session_state.pop('dates',None)
    st.session_state['chart_epoch']=st.session_state.get('chart_epoch',0)+1

def persist_focus(widget,state):
    st.session_state[state]=st.session_state[widget]

def transfer_focus():
    st.session_state.network_focus=st.session_state.focus
    st.session_state.pair=''
    st.session_state.view='Networks'

def chart(fig,table,key,select=None):
    style_figure(fig)
    figure_revision=hashlib.sha256(fig.to_json().encode()).hexdigest()[:16]
    fig.update_layout(meta={'citypulse_motion':key,'citypulse_revision':figure_revision})
    config={'displaylogo':False,'responsive':True,'scrollZoom':False,'toImageButtonOptions':{'format':'svg','filename':'citypulse_'+key,'scale':1}}
    if select:
        def event():
            points=st.session_state.get(key,{}).get('selection',{}).get('points',[])
            if points:select(points)
        st.plotly_chart(fig,width='stretch',key=key,on_select=event,selection_mode=('points','box','lasso'),config=config,theme=None)
    else:st.plotly_chart(fig,width='stretch',key=key,config=config,theme=None)
    if select:st.caption('Explore: select a mark to update evidence focus or filters. The sidebar provides a keyboard alternative.')
    with st.expander('Accessible data · '+key.split('_')[0]):
        st.dataframe(table,hide_index=True,width='stretch')
        st.download_button('Download this chart’s data',table.to_csv(index=False),'citypulse_'+key+'.csv','text/csv',key='data_'+key)

def export(r,label='Download selected review metadata',key='metadata'):
    fields=['review_id','business_id','date','stars']
    st.download_button(label,r[fields].sort_values('review_id').to_csv(index=False),key+'.csv','text/csv',key=key)

st.markdown(HERO,unsafe_allow_html=True)
snapshot=os.environ.get('CITYPULSE_DATA_DIR',str(ROOT/'data/processed'))
preview_mode=False
if not (Path(snapshot)/'audit.json').exists() and not os.environ.get('CITYPULSE_DATA_DIR') and os.environ.get('CITYPULSE_DISABLE_DEMO')!='1':
    from src.demo_preview import ensure_preview
    try:
        preview_path,preview_photos=ensure_preview(ROOT)
        snapshot=str(preview_path)
        os.environ['CITYPULSE_ASSET_ROOT']=str(preview_photos)
        preview_mode=True
    except (OSError,ValueError) as exc:
        st.error(f'Could not prepare the synthetic design preview: {exc}')
if preview_mode:
    st.markdown('<div style="background:#25271f;border:1px solid #8a7841;border-left:4px solid #e8b85e;border-radius:10px;padding:13px 18px;color:#f1dcaa;margin:10px 0 18px"><strong>DEMO DATA · Design Preview</strong> — Restaurants, reviews, coordinates and illustrations are synthetic. Explore the interactions, but do not report these values as Yelp research findings.</div>',unsafe_allow_html=True)
with st.sidebar:
    st.header('Your study population')
    st.caption('Define the population, then focus a restaurant to follow its evidence across views.')
    st.selectbox('Motion mode',MODES,key='motion_mode',help='System reduced motion always takes priority. Reduce motion uses only a short fade; Off shows final states immediately.')
    st.select_slider('Motion speed',options=list(SPEEDS),value='Standard',key='motion_speed')
motion=MotionSettings(st.session_state.motion_mode,st.session_state.motion_speed)
if not (Path(snapshot)/'audit.json').exists():
    st.info('No prepared Yelp snapshot is installed. No demonstration data is presented as real Yelp evidence.')
    st.code('python scripts/prepare_data.py --data-dir /path/to/yelp --city Philadelphia --state PA --photo-json /path/to/photos.json --photos-dir /path/to/photos --out data/processed\npython -m streamlit run app.py')
    st.markdown('Read **START_HERE.md** for acquisition, audit, photo rights, and preparation steps. The supplied bundle contains code and synthetic test fixtures, not licensed Yelp datasets.')
    st.stop()
try:
    p=Path(snapshot);validated=validate_snapshot(snapshot)  # Always validate before any cached read.
    b,r,photos,audit=cached_load(snapshot,(validated['snapshot_sha256'],(p/'audit.json').stat().st_mtime_ns,(p/'citypulse.sqlite').stat().st_mtime_ns))
    assignments,labels,document_points,topic_manifest=load_topics(snapshot,set(r.review_id),audit['snapshot_sha256'])
except (OSError,ValueError,KeyError) as exc:st.error(f'Snapshot cannot be loaded: {exc}');st.stop()
if audit['scope']['mode']!='FULL_SCAN':st.warning('FIRST-N EXPLORATORY SCAN: biased prefix, unsuitable for population claims or final feasibility approval.')
st.caption(f"{audit['scope']['city']}, {audit['scope']['state']} · Snapshot {audit['snapshot_sha256'][:12]} · {audit['created_at'][:10]}")
for key,value in DEFAULTS.items():
    if key not in st.session_state:st.session_state[key]=value.copy() if isinstance(value,list) else value
categories=sorted({c.strip() for value in b.categories for c in value.split(',') if c.strip()!='Restaurants'})
dates=pd.to_datetime(r.date,errors='coerce').dropna()
with st.sidebar:
    st.multiselect('Business categories · OR within selection',categories,key='categories')
    st.checkbox('Restrict review dates',key='use_dates')
    if st.session_state.use_dates and len(dates):
        st.date_input('Review posting period',(dates.min().date(),dates.max().date()),min_value=dates.min().date(),max_value=dates.max().date(),key='dates')
    st.text_input('Exact review term or bigram',key='term',help='English stop words excluded; matches the term chart tokenizer.')
    st.button('Reset all filters and focus',on_click=reset,width='stretch')
    st.caption('Categories use OR. Different filters use AND. Restaurant focus reveals evidence without changing the review population.')
period=st.session_state.get('dates',()) if st.session_state.use_dates else ()
if st.session_state.use_dates and len(period)!=2:st.info('Choose the start and end date.');st.stop()
bsel,rsel=select_reviews(r,b,st.session_state.categories,str(period[0]) if period else None,str(period[1]) if period else None,st.session_state.term,st.session_state.use_dates)
# Precomputed topic IDs remain fixed across selections.
if assignments is not None:
    names=dict(zip(labels.topic,labels.Label))
    with st.sidebar:st.multiselect('Fixed topic · OR within selection',sorted(names),format_func=lambda i:names[i],key='topic_filter')
    if st.session_state.topic_filter:rsel=rsel[rsel.review_id.isin(assignments.loc[assignments.topic.isin(st.session_state.topic_filter),'review_id'])]
else:assignments=None;labels=None
ids=sorted(rsel.business_id.unique());evidence_b=bsel[bsel.business_id.isin(ids)].copy()
focus_choices=['']+ids
if st.session_state.focus not in focus_choices:st.session_state.focus=''
lookup=b.set_index('business_id').name.to_dict()
with st.sidebar:st.selectbox('Focus a restaurant',focus_choices,format_func=lambda v:lookup.get(v,'All restaurants / no focus'),key='focus')
focus=st.session_state.focus
focused=rsel[rsel.business_id==focus] if focus else rsel
c=st.columns(4)
for col,title,value in zip(c,['Review population','Restaurants','Mapped restaurants','Prepared photo records'],[len(rsel),len(evidence_b),int(evidence_b.latitude.notna().sum()),int(photos.business_id.isin(ids).sum())]):col.metric(title,f'{value:,}',help={'Review population':'Reviews matching the active corpus filters.','Restaurants':'Restaurants with at least one selected review.','Mapped restaurants':'Restaurants with selected reviews and usable coordinates.','Prepared photo records':'Prepared metadata rows; image availability is checked when displayed.'}[title])
st.caption('Photo KPI counts prepared records. Current asset availability is verified when photographs are opened.')
st.caption(f'Category cohort: {len(bsel):,} businesses · selected reviews: {len(rsel):,} · missing dates within selection: {rsel.date.isna().sum():,} · focus evidence: {len(focused):,} reviews. Photo and graph eligibility differ and are stated in their views.')
if focus:
    st.info('Evidence focus: '+lookup[focus]+' · Global charts keep the selected population. Focus-specific evidence is explicitly labeled.')
    st.button('Explore focused restaurant in network',on_click=transfer_focus)
with st.expander('Selection details and export'):
    st.write('Active categories: '+(', '.join(st.session_state.categories) or 'All'))
    st.write('Exact term: '+(st.session_state.term or 'None'))
    st.write('Review dates: '+(' to '.join(map(str,period)) if period else 'All available dates'))
    st.write('Fixed topics: '+(', '.join(map(str,st.session_state.topic_filter)) or 'All / no topic filter'))
    export(rsel)
tabs=st.tabs(['Overview','Trends','Map','Reviews & Topics','Photos','Networks','Clustering Lab','Methods'],key='view',on_change='rerun')

if tabs[0].open:
 with tabs[0]:
    st.caption('01 / STUDY OVERVIEW')
    st.subheader('A city, viewed through connected evidence')
    st.write('Compare review volume with reported experience, then follow a restaurant through its location, language, photographs and connections.')
    if not len(rsel):st.info('No review evidence matches. Clear a term, widen dates, or reset filters.')
    agg=rsel.groupby('business_id').agg(**{'Selected reviews':('review_id','size'),'Mean selected rating':('stars','mean')}).reset_index().merge(evidence_b[['business_id','name','stars']],on='business_id')
    st.caption('Mean selected review rating and the snapshot business star rating are different populations. Neither is an objective measure of quality.')
    if len(agg):
        fig=overview_figure(agg,rsel.stars.mean(),focus)
        def focus_event(points):st.session_state.focus=points[0]['customdata'][0]
        chart(fig,agg,'businesses_'+str(st.session_state.get('chart_epoch',0)),focus_event)
    if len(agg):
        valid=rsel.stars.notna().sum()
        st.markdown(f'<div class="citypulse-note">{int(agg["Mean selected rating"].notna().sum()):,}/{len(agg):,} restaurants have a mean rating to plot; {valid:,} selected reviews have valid ratings. Each point represents one restaurant. The dotted line is the mean across selected rated reviews.</div>',unsafe_allow_html=True)
    st.markdown('**Suggested investigation:** choose a category and period, compare the map and review terms, focus one restaurant, inspect its photographs, then examine shared-reviewer connections.')

if tabs[1].open:
 with tabs[1]:
    st.caption('02 / TEMPORAL PATTERNS')
    st.write('**Business question:** Are reviews appearing more frequently, and does the reported experience change at the same time?')
    st.subheader('When does recorded review activity change?')
    st.write('Monthly activity and rating context share the same selected review population. Amber marks the first observed maximum; it is not a significance claim.')
    counts=monthly_reviews(rsel)
    if counts.empty:st.info('No dated reviews in the selected population.')
    else:
        st.markdown('#### Guided exploration · review activity through time')
        st.caption('The first chart reveals observed months in sequence, on a fixed vertical scale. Use Play / Pause / Final to control the story. Motion Off uses an exact static Plotly chart below.')
        if motion.mode != 'Off' and motion.mode != 'Reduce motion':
            import streamlit.components.v1 as st_components
            motion_fig=temporal_story_frames(counts)
            st_components.html(motion_fig.to_html(full_html=False,include_plotlyjs=True,auto_play=True,animation_opts={'frame':{'duration':420,'redraw':True},'transition':{'duration':150}}),height=510,scrolling=False)
        else:
            chart(monthly_figure(counts),counts,'guided_activity_static')
        activity_col,rating_col=st.columns([1.25,1],gap='large')
        with activity_col:chart(monthly_figure(counts),counts,'monthly_reviews')
        with rating_col:chart(monthly_figure(counts,rating=True),counts,'monthly_rating')
        st.markdown('#### Coordinated story · volume and mean rating')
        st.caption('Both measurements progress through the same calendar months. The axes remain fixed. No inference about actual visits or causes is made.')
        if motion.mode not in ('Off','Reduce motion'):
            render_player(synchronized_trends(counts),key='synced_trends',height=555,delay=850)
        peak=counts.loc[counts.Reviews.idxmax()]
        render_story(trend_story(counts),'Review activity')
        st.markdown('#### Alternative view · month-by-year activity heatmap')
        grid=counts.copy()
        grid['Year']=grid.Month.astype(str).str[:4]
        grid['Calendar month']=pd.to_datetime(grid.Month.astype(str)).dt.strftime('%b')
        order=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
        heat=grid.pivot_table(index='Year',columns='Calendar month',values='Reviews',aggfunc='sum').reindex(columns=order)
        fig_heat=px.imshow(heat,labels={'x':'Month','y':'Year','color':'Posted reviews'},color_continuous_scale=[[0,'#1b2833'],[.5,'#37998f'],[1,'#5bd7bf']],aspect='auto',title='Review activity by calendar month and year')
        chart(fig_heat,grid[['Month','Reviews']],'calendar_heatmap')
        st.markdown(f'<div class="citypulse-note">Observed coverage: {len(counts):,} calendar months · Peak posted-review month: {html.escape(str(peak.Month))} ({int(peak.Reviews):,} reviews). Missing months are filled with zero counts; the rating line keeps gaps.</div>',unsafe_allow_html=True)
        with st.expander('Optional temporal replay'):
            st.caption('Guided playback uses the same monthly counts and fixed scales. Pause, Replay and Show final state are available. Reduced-motion settings stop automatic playback.')
            if st.checkbox('Enable temporal replay',key='timeline_replay'):
                st.iframe(child_motion_html(timeline_html(counts,motion),motion,'timeline'),height=550,alt='Monthly review timeline with shared playback controls')
        st.caption('Review posting date is not visit date. Edge months may be partial; dataset coverage and review selection can affect trends. No uncertainty interval is implied by the line.')

if tabs[2].open:
 with tabs[2]:
    st.caption('03 / GEOGRAPHIC CONTEXT')
    st.subheader('Where are the restaurants in this selection?')
    mapped=evidence_b.dropna(subset=['latitude','longitude'])
    st.caption(f'{len(mapped):,}/{len(evidence_b):,} restaurants with selected reviews have usable coordinates. These are Yelp sample records, not a census.')
    if len(mapped):
        mapped=mapped.merge(rsel.groupby('business_id').size().rename('Selected reviews'),on='business_id')
        map_context=st.selectbox('Map background',['Context basemap · online','Coordinate canvas · offline'],index=1 if os.environ.get('CITYPULSE_MAP_BACKGROUND')=='offline' else 0,help='Online tiles require network access. Use the coordinate canvas when tiles are unavailable.')
        map_style='carto-positron' if map_context.startswith('Context') else 'white-bg'
        center={'lat':float(mapped.latitude.median()),'lon':float(mapped.longitude.median())}
        fig=px.scatter_map(mapped,lat='latitude',lon='longitude',hover_name='name',zoom=10,center=center,map_style=map_style,custom_data=['business_id'],hover_data=['Selected reviews'],color_discrete_sequence=COLORS,title='Restaurant locations · one point per restaurant')
        fig.update_traces(marker=dict(size=11,opacity=.85))
        if focus:
            focused_map=mapped[mapped.business_id==focus]
            if len(focused_map):fig.add_trace(go.Scattermap(lat=focused_map.latitude,lon=focused_map.longitude,mode='markers',marker=dict(size=18,color='#A65F10'),customdata=focused_map[['business_id']],text=focused_map.name,hovertemplate='%{text}<extra>Focused restaurant</extra>',name='Focused restaurant'))
        chart(fig,mapped[['business_id','name','latitude','longitude']],'restaurant_map',lambda points:st.session_state.update(focus=points[0]['customdata'][0]))
        st.caption('The basemap provides context; point positions encode business coordinates. Amber identifies the current restaurant focus. Use the sidebar restaurant selector as a keyboard alternative. Switch to the offline canvas if tiles do not load.')
        radius=st.slider('Spatial clustering radius (meters)',100,2000,500,100)
        clustered=spatial_clusters(mapped,radius,3)
        fig=px.scatter_map(clustered,lat='latitude',lon='longitude',color=clustered['Spatial cluster'].astype(str),hover_name='name',map_style=map_style,center=center,zoom=10,color_discrete_map={'-1':'#7B8794'},title='Geographic proximity groups · DBSCAN; noise = −1')
        chart(fig,clustered[['name','Spatial cluster']],'spatial_clusters')
        st.caption('DBSCAN uses haversine distances, radius in meters and minimum three businesses. Geographic groups are separate from review topics and network communities.')
        if st.checkbox('Open Folium street map'):
            import folium
            from streamlit_folium import st_folium
            m=folium.Map(location=[mapped.latitude.mean(),mapped.longitude.mean()],zoom_start=11)
            for row in mapped.itertuples():folium.CircleMarker([row.latitude,row.longitude],radius=5,tooltip=html.escape(row.name)).add_to(m)
            st_folium(m,width=1000,height=500,returned_objects=[])
    regions=ROOT/'data/regions.geojson'
    if regions.exists() and len(mapped):
        import geopandas as gpd
        polys=gpd.read_file(regions)
        if polys.crs is None or 'region_id' not in polys:st.warning('Polygon file needs declared CRS and unique region_id.')
        elif polys.region_id.duplicated().any():st.warning('Duplicate region IDs. Resolve them before spatial aggregation.')
        else:
            points=gpd.GeoDataFrame(mapped,geometry=gpd.points_from_xy(mapped.longitude,mapped.latitude),crs='EPSG:4326')
            joined=gpd.sjoin(points,polys[['region_id','geometry']].to_crs(4326),how='left',predicate='within')
            if joined.business_id.duplicated().any():st.warning('Overlapping polygons produce multiple joins; choropleth withheld.')
            else:
                n=joined.groupby('region_id').size().rename('Businesses')
                q=rsel.groupby('business_id').size().rename('Reviews')
                joined=joined.merge(q,on='business_id',how='left')
                review_counts=joined.groupby('region_id').Reviews.sum()
                spatial=polys.merge(n,on='region_id',how='left');spatial['Businesses']=spatial.Businesses.fillna(0)
                spatial['Reviews per business']=spatial.region_id.map(review_counts)/spatial.Businesses.replace(0,np.nan)
                st.caption(f'{joined.region_id.isna().sum()} points fall outside polygons or on boundaries. Counts use only matched selected businesses; no population-rate claim.')
                metric=st.selectbox('Area metric',['Businesses','Reviews per business'])
                geo=spatial.to_crs(4326).set_index('region_id')
                fig=px.choropleth(geo,geojson=json.loads(geo.to_json()),locations=geo.index,color=metric,color_continuous_scale=SEQUENTIAL,title=metric+' · selected Yelp records')
                fig.update_geos(fitbounds='locations',visible=False)
                chart(fig,spatial.drop(columns='geometry'),'area_summary')
    else:st.info('Polygon choropleth/spatial join activates when you supply data/regions.geojson with region_id and a declared CRS. No boundaries are fabricated.')

if tabs[3].open:
 with tabs[3]:
    st.caption('04 / LANGUAGE & TOPICS')
    st.write('**Business question:** What keeps appearing in customer feedback, and which original reviews support those patterns?')
    st.subheader('What language shapes the selected reviews?')
    metric=st.radio('Term measure',['documents','occurrences'],horizontal=True)
    term_limit=st.select_slider('Terms shown',options=[10,15,25],value=15)
    frequency=term_table(rsel.text.fillna('').tolist(),limit=term_limit,measure=metric)
    if len(frequency):
        fig=ranked_figure(frequency,'Term','Value','Most frequent terms · '+metric,'Term')
        fig.update_xaxes(title='Reviews containing term' if metric=='documents' else 'Total term occurrences')
        chart(fig,frequency,'review_terms_'+str(st.session_state.get('chart_epoch',0)),lambda pts:st.session_state.update(term=pts[0]['customdata'][0]))
    else:st.info('No usable text vocabulary in this selection.')
    if len(frequency):
        st.markdown('#### Guided reveal · which terms dominate?')
        st.caption('Bubbles encode observed term frequency, NOT sentiment, service quality, or distinct machine-learned topics.')
        if motion.mode not in ('Off','Reduce motion'):
            render_player(topic_bubbles(frequency),key='topic_bubbles',height=550,delay=850)
    render_story(review_story(frequency,len(rsel),metric),'Review language')
    if len(frequency):
        st.markdown('#### Alternative visual · review-language landscape')
        st.caption('Treemap area encodes how often each displayed expression appears under the selected metric. It does not represent positive or negative sentiment.')
        chart(theme_landscape(frequency),frequency,'language_landscape')
    if len(frequency) and len(rsel):
        st.markdown('#### Alternative view · which restaurants receive which expressions?')
        st.caption('Cells show the percentage of eligible selected reviews mentioning each displayed expression, not sentiment scores. Restaurants may have very different review counts.')
        term_subset=frequency.sort_values('Value',ascending=False).Term.head(6).tolist()
        term_compare=term_by_restaurant(rsel,evidence_b,term_subset)
        if len(term_compare):
            matrix=term_compare.pivot(index='Restaurant',columns='Term',values='Percent')
            hm=px.imshow(matrix,aspect='auto',color_continuous_scale=[[0,'#17242f'],[.5,'#247e82'],[1,'#5bd8c0']],zmin=0,zmax=100,labels={'color':'Reviews mentioning term (%)'},title='Term presence across selected restaurants')
            hm.update_traces(hovertemplate='%{y}<br>%{x}: %{z:.1f}%<extra></extra>')
            chart(hm,term_compare,'terms_by_restaurant')
    st.markdown('#### Another perspective · rating distributions')
    st.caption('A 100%-stacked chart shows the observed mix of 1–5 star reviews for selected restaurants. Unlike text frequencies, these are actual reported ratings—not machine-inferred sentiment.')
    mix_fig,mix_table=review_rating_mix(rsel,evidence_b)
    if len(mix_table):
        chart(mix_fig,mix_table,'review_rating_mix')
        st.caption('Compare distributions and inspect their denominators in the accessible table. Ratings represent selected posted reviews, not all customers or current business quality.')
    st.caption('Documents counts at most once per review; occurrences counts repeats. Review terms use the same unigram/bigram tokenizer as the global exact-term filter. Select a bar or use the sidebar.')
    if assignments is not None:
        topic_reviews=rsel.merge(assignments,on='review_id',how='inner')
        st.caption(f'Topic-assigned evidence: {len(topic_reviews)}/{len(rsel)} selected reviews; a deterministic model subset may exclude other records.')
        dist=topic_reviews.groupby('topic').size().rename('Reviews').reset_index().merge(labels,on='topic',how='left')
        if len(dist):
            fig=ranked_figure(dist,'Label','Reviews','Exploratory topic distribution','topic')
            chart(fig,dist,'topic_distribution_'+str(st.session_state.get('chart_epoch',0)),lambda pts:st.session_state.update(topic_filter=[pts[0]['customdata'][0]]))
        st.caption('Fit once, then filter. Topic labels require review; unsupervised topics do not establish ground-truth sentiment.')
        if document_points is not None:
            points=document_points[document_points.review_id.isin(rsel.review_id)]
            chart(px.scatter(points,x='x',y='y',color=points.topic.astype(str),color_discrete_map={str(t):COLORS[i%len(COLORS)] for i,t in enumerate(sorted(assignments.topic.unique()))},hover_data=['review_id'],title='Review embedding map · UMAP distances are exploratory'),points,'embedding_map')
    else:st.info('Run scripts/build_topics.py to create fixed topic assignments. NMF works locally; BERTopic/UMAP is an optional offline extension.')
    evidence=focused[focused.text.fillna('').str.len()>0].sort_values('review_id')
    st.divider()
    st.markdown('**Read the supporting evidence**')
    st.caption('Restaurant focus affects this evidence panel only. Review text explains the chart in the author’s original words.')
    if len(evidence):
        rid=st.selectbox('Read original review',evidence.review_id,format_func=lambda v:v)
        row=evidence[evidence.review_id==rid].iloc[0]
        st.write(lookup[row.business_id]);st.caption(f'{row.date or "Undated"} · {row.stars} stars · original review text')
        st.write(row.text)
    st.caption('Do not publish review text unless the applicable terms permit the intended display. Export defaults omit reviewer IDs and original text.')

if tabs[4].open:
 with tabs[4]:
    st.caption('05 / IMAGE COLLECTION')
    st.subheader('Inspect the visual record')
    asset_root=os.environ.get('CITYPULSE_ASSET_ROOT',str(Path(snapshot)/'assets/photos'))
    st.caption('Photographs provide business-level context. Files are checked before display; unavailable or modified images are withheld.')
    pics=photos[photos.business_id.isin([focus] if focus else ids)]
    labels=sorted(pics.label.unique())
    label=st.selectbox('Photo category',['All']+labels)
    if label!='All':pics=pics[pics.label==label]
    st.caption(f'{len(pics)} prepared photo records in this evidence population. Only the displayed images are checked for current availability. Photos link to businesses, not specific reviews or dates.')
    if pics.empty:st.info('No decoded photos available. Supply separate authorized photo metadata and actual image files during preparation.')
    else:
        st.caption('Montage: first nine photo IDs in stable order; this is a navigation sample, not a representative visual summary.')
        for chunk in range(0,min(9,len(pics)),3):
            cols=st.columns(3)
            for col,photo in zip(cols,pics.sort_values('photo_id').iloc[chunk:chunk+3].itertuples()):
                try:
                    image_path=resolve_photo(photo.path,asset_root,photo.sha256)
                    with Image.open(image_path) as source:
                        from PIL import ImageOps
                        thumb=ImageOps.fit(source.convert('RGB'),(480,320))
                    col.image(thumb,caption=f'{lookup[photo.business_id]} · {photo.label} · cropped thumbnail',width='stretch')
                except (OSError,IntegrityError) as exc:col.warning(str(exc))
        pid=st.selectbox('Inspect photo',pics.photo_id)
        p=pics[pics.photo_id==pid].iloc[0]
        try:image_path=resolve_photo(p.path,asset_root,p.sha256)
        except (OSError,IntegrityError) as exc:st.warning(str(exc));image_path=None
        if image_path is not None:
            with Image.open(image_path) as source:img=source.convert('RGB');img.thumbnail((1024,1024));arr=np.asarray(img)
            original_col,distribution_col=st.columns([1,1.25],gap='large')
            with original_col:
                st.image(img,caption=f'Photo {pid} · {lookup[p.business_id]} · {p.label}',width='stretch')
                st.caption(f'Original {p.width}×{p.height}; analysis preview {img.width}×{img.height}. RGB converted; histogram normalized per channel.')
                with st.expander('Inspect an individual color channel'):
                    channel=st.radio('Inspect channel',['Red','Green','Blue'],horizontal=True)
                    st.image(arr[:,: ,['Red','Green','Blue'].index(channel)],caption=channel+' intensity',clamp=True,width='stretch')
            with distribution_col:
                hist=image_histogram(arr)
                fig=px.line(hist,x='Intensity',y='Pixel share',color='Channel',line_dash='Channel',color_discrete_map={'Red':'#B02A37','Green':'#267B3C','Blue':'#245CB5'},title='Normalized RGB intensity distributions')
                fig.update_xaxes(range=[0,255],tickvals=[0,64,128,192,255])
                fig.update_yaxes(tickformat='.0%',rangemode='tozero')
                chart(fig,hist,'rgb_intensity')
        st.caption('Montage thumbnails are cropped for alignment; the inspector retains the full image aspect ratio.')
        st.info('No trained image classifier is bundled. Saliency/occlusion remains a final-project extension, not a fabricated explanation.')

if tabs[5].open:
 with tabs[5]:
    st.caption('06 / SHARED-REVIEWER NETWORK')
    st.subheader('Which places share observed reviewers?')
    minimum=st.slider('Minimum distinct shared reviewers',1,10,2)
    activity=st.slider('Maximum businesses per reviewer used in projection',5,100,50,5)
    with st.spinner('Building the selected reviewer projection…'):
        g,info=graph_cache(rsel[['user_id','business_id']],minimum,activity)
    st.caption(f'{len(g)} restaurant nodes · {g.number_of_edges()} edges · {nx.number_connected_components(g) if len(g) else 0} components. Excluded {info["excluded_high_activity_reviewers"]} high-activity reviewers above {activity} businesses; exclusions affect projection weights only.')
    if not g.number_of_edges():st.info('No shared-reviewer edges survive. Lower the threshold or widen filters. No network connections are invented.')
    else:
        cap=st.slider('Display cap · metrics computed on selected graph',20,200,80,20)
        ranking,details=graph_details(g)
        ranking=ranking.sort_values(['Shared-reviewer strength','business_id'],ascending=[False,True])
        st.caption('Betweenness: '+details['betweenness']+'. Edge distance = 1/shared-reviewer count; connections are not geographic distances or friendships.')
        net_options=['']+ranking.business_id.tolist()
        if st.session_state.network_focus not in net_options:st.session_state.network_focus=''
        st.session_state['_network_focus_widget']=st.session_state.network_focus
        st.selectbox('Inspect restaurant neighborhood',net_options,format_func=lambda i:lookup.get(i,'Ranked display'),key='_network_focus_widget',on_change=persist_focus,args=('_network_focus_widget','network_focus'))
        nf=st.session_state.network_focus
        nodes=([nf]+sorted(g.neighbors(nf),key=lambda n:(-g[nf][n]['weight'],n)))[:cap] if nf else ranking.business_id.head(cap).tolist()
        view=g.subgraph(nodes).copy()
        st.caption(f'Displaying {len(view)}/{len(g)} restaurants and {view.number_of_edges()}/{g.number_of_edges()} edges. Community assignments use the selected graph, not the display cap.')
        layout=st.radio('Network layout',['Force-directed','Circular'],horizontal=True)
        mode=st.radio('Network renderer',['Plotly · select nodes','PyVis · drag nodes'],horizontal=True)
        pos=nx.spring_layout(view,seed=42,weight='weight') if layout=='Force-directed' else nx.circular_layout(view)
        membership=details['membership']
        if mode.startswith('Plotly'):
            ex=[];ey=[]
            for a,z in view.edges:ex.extend([pos[a][0],pos[z][0],None]);ey.extend([pos[a][1],pos[z][1],None])
            fig=go.Figure(go.Scatter(x=ex,y=ey,mode='lines',line=dict(width=.7,color='#AAB4BC'),hoverinfo='skip',showlegend=False))
            fig.add_trace(go.Scatter(x=[pos[n][0] for n in nodes],y=[pos[n][1] for n in nodes],mode='markers',customdata=[[n,g.degree(n),g.degree(n,weight='weight'),membership[n]] for n in nodes],text=[lookup[n] for n in nodes],hovertemplate='%{text}<br>%{customdata[1]} connections<br>Strength %{customdata[2]}<br>Community %{customdata[3]}<extra></extra>',marker=dict(size=[12+2*np.sqrt(g.degree(n)) for n in nodes],color=[COLORS[membership[n]%len(COLORS)] for n in nodes],line=dict(color=['#A65F10' if n==nf else '#FFFFFF' for n in nodes],width=[3 if n==nf else 1 for n in nodes])),showlegend=False))
            fig.update_layout(title='Shared-reviewer network · displayed subgraph',xaxis_visible=False,yaxis_visible=False)
            fig.update_yaxes(scaleanchor='x',scaleratio=1)
            for cid in sorted({membership[n] for n in nodes})[:8]:
                fig.add_trace(go.Scatter(x=[None],y=[None],mode='markers',marker=dict(size=9,color=COLORS[cid%len(COLORS)]),name=f'Community {cid}',showlegend=True,hoverinfo='skip'))
            def node_event(pts):
                valid=[p for p in pts if p.get('customdata')]
                if valid:st.session_state.network_focus=valid[0]['customdata'][0]
            node_data=ranking[ranking.business_id.isin(nodes)].assign(Restaurant=lambda f:f.business_id.map(lookup))
            chart(fig,node_data,'network_nodes_'+str(st.session_state.get('chart_epoch',0)),node_event)
        else:
            from pyvis.network import Network
            reduced=st.checkbox('Freeze physics / reduced motion',value=True)
            net=Network(height='560px',width='100%',cdn_resources='in_line',bgcolor='#F5F8FA')
            for n in nodes:net.add_node(n,label='',title=html.escape(lookup[n])+f' · {g.degree(n)} connections',size=float(10+2*np.sqrt(g.degree(n))),color=COLORS[membership[n]%len(COLORS)],x=float(pos[n][0]*450),y=float(pos[n][1]*450),physics=not reduced and layout=='Force-directed')
            for a,z,d in view.edges(data=True):net.add_edge(a,z,title=str(d['weight'])+' shared reviewers',width=1,color='#B8C1CA')
            net.toggle_physics(not reduced and layout=='Force-directed')
            st.iframe(child_motion_html(net.generate_html(notebook=False),motion,'pyvis',allow_physics=not reduced and layout=='Force-directed'),height=650,alt='Shared-reviewer network with draggable nodes and motion controls')
            st.caption('Shared Play/Pause/Show final state controls also govern physics. Continuous physics requires unfreezing it here; system reduced motion and Motion off always stop it. Hover names, drag nodes. PyVis clicks do not update Streamlit; use the synchronized restaurant selector for evidence. Physics is opt-in; circular layout remains fixed.')
        order=nodes[:40]
        matrix=nx.to_numpy_array(view,nodelist=order,weight='weight')
        st.markdown('**Compare exact connection strengths**')
        chart(adjacency_figure(matrix,order,lookup),pd.DataFrame(matrix,index=order,columns=order).rename_axis('business_id').reset_index(),'adjacency')
        st.caption('Matrix keys follow the displayed ordering; the table connects each key to its original restaurant name.')
        st.dataframe(pd.DataFrame({'Matrix key':[f'R{i+1:02}' for i in range(len(order))],'business_id':order,'Restaurant':[lookup[n] for n in order]}),hide_index=True,width='stretch')
        st.caption('Node size = degree; color = community. Layout spacing does not measure similarity. Palette colors may repeat when communities exceed eight; use the ranking table for exact IDs.')
        st.dataframe(ranking.assign(Restaurant=ranking.business_id.map(lookup)),hide_index=True,width='stretch')
        if nf:
            others=['']+sorted(g.neighbors(nf))
            if st.session_state.pair not in others:st.session_state.pair=''
            st.session_state['_pair_widget']=st.session_state.pair
            st.selectbox('Inspect shared-reviewer evidence with',others,format_func=lambda i:lookup.get(i,'Choose another restaurant'),key='_pair_widget',on_change=persist_focus,args=('_pair_widget','pair'))
            if st.session_state.pair:
                pair=shared_reviewers(rsel,nf,st.session_state.pair)
                st.caption(f'{pair.user_id.nunique()} shared reviewers in all selected reviews. Projected edge may be smaller after the high-activity exclusion.')
                st.dataframe(pair[['review_id','business_id','date','stars']],hide_index=True)
                export(pair,'Download shared-reviewer evidence metadata','pair_evidence')

if tabs[6].open:
 with tabs[6]:
    render_clustering_lab(evidence_b,rsel,assignments,labels,lookup,chart,preview_mode)

if tabs[7].open:
 with tabs[7]:
    st.caption('08 / METHODS & INTERPRETATION')
    st.subheader('Understand what the evidence can support')
    st.markdown('### From source evidence to an operational question')
    st.markdown('**1. Select a city or restaurant → 2. Inspect posted-review trends → 3. Compare review language → 4. Inspect permitted photographs → 5. Explore shared reviewer groups → 6. Read the original evidence.**')
    st.markdown('**How a business could use this:** Investigate recurring feedback, prioritize service questions, compare observed neighborhoods, and form testable expansion hypotheses. The application cannot independently estimate demand, revenue, footfall, or causality.')
    st.write('Yelp records are a selected platform snapshot, not a population census. Ratings are reported experiences, not verified business quality. Reviews are not visits; photos are business-linked, not review-linked. Reviewer overlap does not establish social ties.')
    st.write('One immutable snapshot supports all modalities. Category filters use OR; review date, exact term and topic filters use AND. Focus is separate from corpus filtering. Invalid dates are excluded only when applying date filters.')
    st.warning('Rights review and real-data feasibility are not certified by code. Retain the applicable agreement and attribution. Do not commit raw reviews, identity records, image files or generated extracts to public GitHub without checking permissions.')
    with st.expander('Snapshot audit and computational details'):st.json(audit)
    st.download_button('Download computational audit',json.dumps(audit,indent=2),'audit.json','application/json')
    st.markdown('**Final extension:** evaluated review-rating or photo-category model behind FastAPI/Flask, consumed by this Streamlit client. No model performance or saliency claim is made here.')
    st.caption('Document AI assistance and make your own analytical decisions in accordance with the course policy.')

# Mount after all native charts have been described; component enhances their DOM without replacing events.
revision=json.dumps({'categories':st.session_state.categories,'period':list(map(str,period)),'term':st.session_state.term,'topic':st.session_state.topic_filter,'focus':focus,'network_focus':st.session_state.network_focus,'pair':st.session_state.pair,'epoch':st.session_state.get('chart_epoch',0)},sort_keys=True)
with st.sidebar:render_motion(motion,st.session_state.get('view','Overview'),revision)
