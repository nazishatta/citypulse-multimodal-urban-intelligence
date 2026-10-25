#!/usr/bin/env python3
"""Run locally against authorized real data; output is not a browser benchmark."""
import argparse,json,platform,sys,time,tracemalloc
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import plotly.express as px
from src.data import load_snapshot,load_topics
from src.analysis import restaurant_graph,graph_details

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--snapshot',required=True);p.add_argument('--out',type=Path,required=True);p.add_argument('--provenance',choices=['real','synthetic'],required=True);a=p.parse_args()
 tracemalloc.start();results={}
 def timed(name,fn):
  t=time.perf_counter();value=fn();results[name+'_seconds']=time.perf_counter()-t;return value
 b,r,photos,audit=timed('verified_load',lambda:load_snapshot(a.snapshot))
 g,info=timed('graph_build',lambda:restaurant_graph(r[['user_id','business_id']],2,50))
 timed('graph_metrics',lambda:graph_details(g))
 topics,labels,points,manifest=timed('verified_topics',lambda:load_topics(a.snapshot,set(r.review_id),audit['snapshot_sha256']))
 if topics is not None:
  dist=topics.groupby('topic').size().rename('Reviews').reset_index()
  timed('topic_figure_json',lambda:px.bar(dist,x='topic',y='Reviews').to_json())
 current,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
 results.update(provenance=a.provenance,python=platform.python_version(),platform=platform.platform(),snapshot_sha256=audit['snapshot_sha256'],businesses=len(b),reviews=len(r),photos=len(photos),nodes=len(g),edges=g.number_of_edges(),projection=info,python_traced_peak_bytes=peak,limitations='Single cold-process observation; traced Python allocations exclude some native allocations. Browser paint, interactions, deployment and full-process RSS not measured.')
 a.out.write_text(json.dumps(results,indent=2));print(a.out)
if __name__=='__main__':main()
