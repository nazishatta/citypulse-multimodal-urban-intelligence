"""True live PyVis reviewer-audience network for the Clustering Lab."""
from __future__ import annotations
import html
import json
import math
import networkx as nx
import streamlit.components.v1 as components
from pyvis.network import Network


def render_live_audience(graph, memberships, lookup, *, colors, freeze=False, height=550):
    """Draw the measured graph with physics; no artificial links or groups."""
    net=Network(height=f'{height}px',width='100%',bgcolor='#18212B',font_color='#F4F7F9',cdn_resources='in_line')
    nodes=sorted(graph.nodes(),key=str)
    coordinates=nx.spring_layout(graph,weight='weight',seed=42) if nodes else {}
    for node in nodes:
        community=int(memberships.get(node,0))
        net.add_node(str(node),label='',title=html.escape(str(lookup.get(node,node)))+f' · community {community} · {graph.degree(node)} links',
                     color=colors[community%len(colors)],size=11+3*math.sqrt(graph.degree(node)),
                     x=float(coordinates[node][0]*400),y=float(coordinates[node][1]*400))
    for a,b,data in graph.edges(data=True):
        weight=float(data.get('weight',1))
        net.add_edge(str(a),str(b),title=f'{weight:g} shared reviewers',width=min(4,0.6+math.sqrt(weight)),color='rgba(165,183,200,0.24)')
    net.set_options(json.dumps({'physics':{'enabled':not freeze,'solver':'forceAtlas2Based',
                                   'stabilization':{'enabled':False},'minVelocity':.01,
                                   'forceAtlas2Based':{'gravitationalConstant':-115,'centralGravity':.002,
                                                       'springLength':160,'springConstant':.025,'damping':.75}},
                                'interaction':{'hover':True,'dragNodes':True,'navigationButtons':True},
                                'nodes':{'font':{'color':'#EFF6F8'}},'edges':{'smooth':False}}))
    page=net.generate_html()
    # Continuous subtle movement, suspended while dragging, on Freeze, reduced motion or hidden tab.
    motion='true' if not freeze else 'false'
    script='''<script>
(function(){
const allowed = MOTION_ALLOWED && !window.matchMedia('(prefers-reduced-motion: reduce)').matches;
if (!allowed || typeof network === 'undefined' || typeof nodes === 'undefined') return;
let dragged=false, tick=0;
network.on('dragStart',()=>{dragged=true;});
network.on('dragEnd',()=>{dragged=false;});
setInterval(()=>{
  if(dragged || document.hidden) return;
  const ids=nodes.getIds(); if(!ids.length) return;
  const id=ids[tick++ % ids.length];
  const positions=network.getPositions([id]); const p=positions[id];
  if(!p)return;
  network.moveNode(id,p.x+Math.sin(tick*1.3)*0.8,p.y+Math.cos(tick*1.7)*0.8);
  network.startSimulation();
},1700);
})();
</script>'''.replace('MOTION_ALLOWED',motion)
    page=page.replace('</body>',script+'</body>')
    components.html(page,height=height+10,scrolling=False)
