#!/usr/bin/env python3
"""Build a self-contained visual review using explicitly synthetic fixtures only."""
import argparse,html,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import networkx as nx
from src.motion import MotionSettings
from plotly.offline import get_plotlyjs
from src.pipeline import prepare
from src.data import load_snapshot
from src.analysis import monthly_reviews,term_table,fit_topics,restaurant_graph
from src.visuals import CSS,HERO,style_figure,overview_figure,monthly_figure,ranked_figure,adjacency_figure
from tests.fixtures import make_inputs,write_json
import numpy as np

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--out',type=Path,default=Path('VISUAL_PREVIEW.html'));args=p.parse_args()
 with tempfile.TemporaryDirectory() as temp:
  root=Path(temp);raw=root/'raw';businesses,original,_=make_inputs(raw)
  rng=np.random.default_rng(42);months=np.arange(36);prob=(1+months/18)*(1+.35*np.sin(months*np.pi/6));prob=prob/prob.sum();weights=np.array([2,3,8,4,5,9,2,6,3,7,4,10]);weights=weights/weights.sum()
  reviews=[]
  for i in range(1500):
   m=int(rng.choice(months,p=prob));bid=int(rng.choice(12,p=weights));rating=int(np.clip(np.rint(2+(bid%5)*.6+rng.normal(0,.9)),1,5))
   reviews.append(dict(review_id=f'preview{i:05}',business_id=f'b{bid}',user_id=f'u{int(rng.integers(0,120))}',date=f'{2022+m//12}-{m%12+1:02}-{int(rng.integers(1,28)):02} 12:00:00',stars=rating,text=original[(bid+i%3)%4]['text']))
  write_json(raw/'yelp_academic_dataset_review.json',reviews)
  out=root/'snapshot';prepare(raw,out,'Fixture City','TS',raw/'photos.json',raw/'photos')
  b,r,photos,_=load_snapshot(str(out))
 agg=r.groupby('business_id').agg(**{'Selected reviews':('review_id','size'),'Mean selected rating':('stars','mean')}).reset_index().merge(b[['business_id','name']],on='business_id')
 counts=monthly_reviews(r);assign,labels=fit_topics(r)
 dist=assign.groupby('topic').size().rename('Reviews').reset_index().merge(labels,on='topic')
 g,_=restaurant_graph(r,2,50);ids=sorted(g);lookup=b.set_index('business_id').name.to_dict()
 terms=term_table(r.text.tolist(),limit=15);matrix=nx.to_numpy_array(g,nodelist=ids)
 figures=[('Study overview',overview_figure(agg,r.stars.mean(),'b0'),agg),('Review activity',monthly_figure(counts),counts),('Rating context',monthly_figure(counts,True),counts),('Review language',ranked_figure(terms,'Term','Value','Most frequent terms · documents','Term'),terms),('Topic comparison',ranked_figure(dist,'Label','Reviews','Exploratory topics · provisional labels','topic'),dist),('Shared-reviewer matrix',adjacency_figure(matrix,ids,lookup),__import__('pandas').DataFrame(matrix,index=[f'R{i+1:02} · {lookup[n]}' for i,n in enumerate(ids)],columns=[f'R{i+1:02}' for i in range(len(ids))]))]
 sections=[]
 for i,(title,fig,table) in enumerate(figures):
  style_figure(fig)
  fig.update_layout(meta={'citypulse_motion':f'preview-{i}'})
  plot=fig.to_html(full_html=False,include_plotlyjs=False,div_id=f'preview-{i}',config={'displaylogo':False,'responsive':True})
  sections.append(f'<section class="preview-panel" id="panel-{i}" aria-labelledby="heading-{i}"><h2 id="heading-{i}">{html.escape(title)}</h2><p>Generated test records only. Hover, zoom and inspect the data table. Selection in this preview does not change the Streamlit application.</p>'+plot+'<details><summary>Accessible chart data</summary>'+table.to_html(index=True,escape=True,border=0)+'</details></section>')
 metrics=''.join(f'<div data-testid="stMetric"><div data-testid="stMetricLabel">{label}</div><div class="metric-value">{value}</div></div>' for label,value in [('Synthetic reviews',len(r)),('Synthetic restaurants',len(b)),('Synthetic months',len(counts)),('Prepared synthetic photo records',len(photos))])
 nav=''.join(f'<a href="#panel-{i}">{html.escape(title)}</a>' for i,(title,_,_) in enumerate(figures))
 document='<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CityPulse · Synthetic Visual Preview</title>'+CSS+'''<style>
body{margin:0;font-family:Arial,sans-serif;line-height:1.5}.block-container{margin:auto;padding:28px}.preview-notice{background:#FFF1D6;border:1px solid #AD6A10;padding:14px;border-radius:8px;margin-bottom:20px;font-weight:600}.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:16px}.metric-value{font-size:2rem;color:#172B40;font-weight:700}.preview-panel{background:white;padding:24px;margin:22px 0;border:1px solid #DCE3EA;border-radius:10px;scroll-margin-top:20px}.preview-panel p{color:#536579;font-size:.9rem}nav{display:flex;gap:16px;flex-wrap:wrap;margin:24px 0}a{color:#006A71}details{overflow:auto}summary{cursor:pointer;color:#006A71}table{border-collapse:collapse;width:100%;font-size:.85rem}th,td{border-bottom:1px solid #DCE3EA;padding:8px;text-align:left}@media(max-width:700px){.metrics{grid-template-columns:repeat(2,1fr)}.preview-panel{padding:12px}.block-container{padding:12px}}
</style><script>'''+get_plotlyjs()+'''</script></head><body class="stApp"><main class="block-container"><div class="preview-notice">SYNTHETIC DESIGN PREVIEW · No real Yelp records or research findings. This file previews chart styling; the full seven-tab explorer runs in Streamlit.</div>'''+HERO+'<div class="metrics">'+metrics+'</div><nav aria-label="Preview sections">'+nav+'</nav>'+''.join(sections)+'<footer>CityPulse visual revision · Synthetic values are for design review only. No dataset suitability, browser accessibility or submission-readiness claim.</footer></main></body></html>'
 assets=Path(__file__).resolve().parents[1]/'src/frontend'
 motion_css='<style>'+ (assets/'motion.css').read_text()+'</style>'
 motion_root='<section aria-label="Shared motion settings"><label for="preview-mode">Motion mode </label><select id="preview-mode"><option>Follow system</option><option>Reduce motion</option><option>Off</option></select> <label for="preview-speed">Speed </label><select id="preview-speed"><option>Quick</option><option selected>Standard</option><option>Gentle</option></select><div id="preview-motion-root"></div></section>'
 bootstrap='''<script>'''+(assets/'motion.js').read_text()+'''
let cleanupMotion;
function setMotion(){
 if(cleanupMotion)cleanupMotion();
 const speed=document.getElementById('preview-speed').value;
 const settings={mode:document.getElementById('preview-mode').value,speed,duration:{Quick:400,Standard:650,Gentle:1000}[speed],updateDuration:160,reducedDuration:120,easing:'cubic-bezier(0.22, 1, 0.36, 1)'};
 cleanupMotion=mountCityPulseMotion(document.getElementById('preview-motion-root'),{settings,tab:'Preview',revision:'synthetic-v4'});
}
window.addEventListener('load',setMotion);
document.getElementById('preview-mode').addEventListener('change',setMotion);
document.getElementById('preview-speed').addEventListener('change',setMotion);
</script>'''
 document=document.replace('</head>',motion_css+'</head>').replace('<nav aria-label="Preview sections">',motion_root+'<nav aria-label="Preview sections">').replace('</body>',bootstrap+'</body>')
 args.out.write_text(document);print(args.out)
if __name__=='__main__':main()
