"""Eighth CityPulse tab: teach and explore three non-interchangeable structures."""
from __future__ import annotations
import networkx as nx
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from src.clustering_lab import geographic_summary,shared_audience_summary,text_group_summary
from src.stories import cluster_story
from src.story_ui import render_story
from src.visual_intelligence import cluster_profile
from src.guided_motion import cluster_entrance,render_player
from src.visuals import COLORS,ranked_figure


def render_clustering_lab(evidence_b,rsel,assignments,labels,lookup,chart,preview_mode):
    st.caption('07 / CLUSTERING LAB · THREE DIFFERENT STRUCTURES')
    st.subheader('What does it mean for restaurants or reviews to form a group?')
    st.write('Explore **nearby places**, **overlapping reviewer audiences**, and **similar review themes**. These are three different analytical concepts—not three answers to the same clustering problem.')
    if preview_mode:
        st.info('DEMONSTRATION DATA: these clustering results use fictional restaurants and generated reviews. They are not Yelp findings.')
    method=st.radio('Choose a grouping question', ['Geographic · nearby places','Network · shared audiences','Text · review themes'],horizontal=True,key='cluster_method')
    if method.startswith('Geographic'):
        st.markdown('#### Where are restaurants geographically concentrated?')
        c1,c2=st.columns(2)
        with c1: radius=st.slider('Neighborhood radius (meters)',100,3000,650,50,key='cluster_radius')
        with c2: min_n=st.slider('Minimum restaurants per spatial group',2,8,3,key='cluster_min')
        grouped,counts=geographic_summary(evidence_b,radius,min_n)
        if grouped.empty:
            st.info('No selected restaurants have coordinates. Broaden the selected population.')
            return
        n_clusters=int((counts['Spatial cluster']!=-1).sum()); n_noise=int((grouped['Spatial cluster']==-1).sum())
        a,b,c=st.columns(3)
        a.metric('Spatial groups',n_clusters);b.metric('Unassigned places',n_noise);c.metric('Mapped restaurants',len(grouped))
        grouped=grouped.assign(Group=grouped['Spatial cluster'].map(lambda n:'Unassigned (−1)' if n==-1 else f'Spatial group {n+1}'))
        # Always use a stable, explicit discrete color mapping for group identities.
        names=sorted(grouped.Group.unique()); palette={v:COLORS[i%len(COLORS)] for i,v in enumerate(names)}
        palette['Unassigned (−1)']='#7D8997'
        # Cluster intelligence first: avoid a duplicate of the animated geographic plot below.
        st.markdown('**Cluster comparison · how large is each restaurant group?**')
        comparison=counts.assign(Group=counts['Spatial cluster'].map(lambda n:'Unassigned (−1)' if n==-1 else f'Spatial group {n+1}'))
        comparison=comparison.sort_values(['Restaurants','Group'],ascending=[False,True])
        bar=px.bar(comparison,x='Restaurants',y='Group',orientation='h',color='Group',
                   color_discrete_map=palette,text='Restaurants',height=300,
                   title='Measured group sizes · selected restaurants')
        bar.update_layout(showlegend=False,yaxis={'categoryorder':'total ascending'},
                          paper_bgcolor='#191F27',plot_bgcolor='#191F27',
                          font={'color':'#EDF5F8'},
                          hoverlabel={'bgcolor':'#111A23','font':{'color':'#FFFFFF'}})
        chart(bar,comparison[['Group','Restaurants']],'cluster_size_comparison_v52')
        chosen=st.selectbox('Explore a detected spatial group',
             [v for v in comparison.Group if not v.startswith('Unassigned')],
             index=0,key='cluster_inspect_v52') if n_clusters else None
        if chosen:
            members=grouped[grouped.Group==chosen]
            st.markdown(f'**{chosen}: {len(members)} restaurants**')
            st.caption('These restaurants are geographically close under the chosen DBSCAN settings; the cluster does not establish economic demand or reviewer similarity.')
            fields=[x for x in ['name','business_id','stars','review_count'] if x in members.columns]
            st.dataframe(members[fields].rename(columns={'name':'Restaurant','stars':'Snapshot stars','review_count':'Yelp snapshot review count'}),
                         hide_index=True,use_container_width=True)
        st.caption('The animated scene below uses the same measured DBSCAN assignments. It is the ONLY coordinate scatterplot in this view.')
        st.markdown('**Story mode · how spatial groups are assigned**')
        st.caption('Coordinates stay fixed while the actual DBSCAN group labels are revealed. The final gray points are unassigned (noise).')
        render_player(cluster_entrance(grouped),key='cluster_reveal',height=535,delay={'Quick':1400,'Standard':2350,'Gentle':3400}[st.session_state.get('motion_speed','Standard')],loop=True)
        if n_clusters:
            st.markdown('**Group profiles · actual selected restaurants**')
            profile=grouped[grouped['Spatial cluster']!=-1].groupby('Group',as_index=False).agg(Restaurants=('business_id','nunique'),Example=('name','first'))
            st.dataframe(profile,hide_index=True,use_container_width=True)
            richer=cluster_profile(grouped)
            st.markdown('**What distinguishes these groups? · measured profiles**')
            st.dataframe(richer,hide_index=True,use_container_width=True)
            st.caption('Ratings in this profile are the dataset’s business snapshot ratings, not means of the currently selected reviews. Compare these separately.')
        st.markdown('**Business interpretation · geographic groupings**')
        st.write('**What this shows:** Actual restaurants grouped by geographic proximity at the selected radius. The chart compares group sizes; the animated plot reveals membership.')
        st.write('**Why it matters:** A company can examine concentrations of competing or complementary restaurants and understand how sensitive those concentrations are to the radius setting.')
        st.write('**Next action:** Select the largest and smallest groups, compare their categories and review activity, then validate any expansion hypothesis with footfall, rents and demand data. Proximity alone does not establish an underserved market.')
        render_story(cluster_story(counts,n_noise,radius,min_n),'Spatial groups')
        st.info(f'**What this shows:** DBSCAN identified **{n_clusters} spatial groups** using a {radius:,} m radius and at least {min_n} businesses per group. **{n_noise}** mapped places are unassigned (label −1). Nearby locations do not imply similar ratings or shared audiences.')
    elif method.startswith('Network'):
        st.markdown('#### Which restaurants share observed reviewers?')
        c1,c2=st.columns(2)
        with c1: threshold=st.slider('Minimum shared reviewers per connection',1,8,2,key='cluster_shared')
        with c2: cap=st.slider('Maximum restaurants shown',20,150,60,10,key='cluster_cap')
        g,ranking,provenance=shared_audience_summary(rsel,threshold,50)
        if not g.number_of_edges():
            st.info('No qualifying reviewer-overlap connections. Lower the threshold or widen the filters. No edges are fabricated.')
            return
        a,b,c=st.columns(3)
        a.metric('Network communities',provenance['communities']);b.metric('Shared-reviewer links',g.number_of_edges());c.metric('Connected restaurants',sum(d>0 for _,d in g.degree()))
        rank=ranking.sort_values(['Shared-reviewer strength','business_id'],ascending=[False,True])
        members=rank.business_id.head(cap).tolist(); view=g.subgraph(members)
        pos=nx.spring_layout(view,seed=42,weight='weight')
        xs=[];ys=[]
        for u,v in view.edges():xs.extend([pos[u][0],pos[v][0],None]);ys.extend([pos[u][1],pos[v][1],None])
        fig=go.Figure(go.Scatter(x=xs,y=ys,mode='lines',line=dict(color='rgba(175,192,209,.22)',width=1),hoverinfo='skip',showlegend=False))
        groups=rank.set_index('business_id').Community.to_dict()
        fig.add_trace(go.Scatter(x=[pos[i][0] for i in members],y=[pos[i][1] for i in members],mode='markers',
                  marker=dict(size=[10+2*float(g.degree(i))**0.5 for i in members],color=[COLORS[int(groups[i])%len(COLORS)] for i in members],line=dict(width=1,color='#DAE4EB')),
                  customdata=[[i,int(groups[i]),int(g.degree(i))] for i in members],text=[lookup.get(i,i) for i in members],
                  hovertemplate='%{text}<br>Community %{customdata[1]}<br>Connections %{customdata[2]}<extra></extra>',showlegend=False))
        fig.update_layout(title='Reviewer-overlap graph · algorithmic communities',height=540,xaxis_visible=False,yaxis_visible=False)
        fig.update_yaxes(scaleanchor='x')
        chart(fig,rank.assign(Restaurant=rank.business_id.map(lookup)),'cluster_network')
        st.markdown('**Business interpretation · overlapping audiences**')
        st.write('**What this shows:** Observed reviewer-overlap communities; stronger edges represent more distinct overlapping review accounts.')
        st.write('**Why it matters:** This can suggest which businesses deserve competitive or customer-audience comparison, but it cannot establish that reviewers visited both businesses or that they are substitutable.')
        st.write('**Next action:** Inspect the strongest pairs and compare their review themes and published categories before drawing any commercial conclusion.')
        st.info(f'**What this shows:** {provenance["communities"]} algorithmic communities from {g.number_of_edges()} observed links (at least {threshold} distinct shared reviewers per edge). The figure shows {len(members)} of {len(g)} graph nodes. Connections are **not** friendship or restaurant partnerships; layout distance is not geographic distance.')
    else:
        st.markdown('#### Which review themes appear together in the selected population?')
        groups,eligible=text_group_summary(rsel,assignments,labels)
        if groups.empty:
            st.info('No verified topic artifacts for this snapshot. Run the offline NMF topic builder first. We will not invent text clusters.')
            return
        st.metric('Topic-assigned selected reviews',eligible)
        groups=groups.assign(Topic=groups.topic.map(lambda v:f'T{v+1}' if v>=0 else 'Unassigned'))
        fig=ranked_figure(groups,'Topic','Reviews','Dominant NMF topic assignments','topic')
        chart(fig,groups[['Topic','Label','Reviews']],'cluster_text')
        st.dataframe(groups[['Topic','Label','Reviews']],hide_index=True,width='stretch')
        st.markdown('**Business interpretation · customer language**')
        st.write('**What this shows:** Review groups assigned to dominant learned topics. Topic names are tentative and should be checked against representative review excerpts.')
        st.write('**Why it matters:** Managers can investigate repeated discussion themes across the review population rather than relying on average ratings alone.')
        st.write('**Next action:** Compare topic frequencies across restaurants and read evidence before prioritizing service or menu improvements.')
        st.info('**What this shows:** Reviews grouped by their dominant fixed NMF topic. These are **model-derived theme assignments**, not verified sentiment, not geographic clusters, and not an independent hard-clustering algorithm. Read representative reviews before trusting a topic label.')
    st.caption('Motion uses the shared CityPulse controller; auto-start and visible playback depend on the browser renderer. Exact results remain available in the data tables.')
