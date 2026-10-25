#!/usr/bin/env python3
"""Offline fixed topic preparation; never trains on an interactive selection."""
import argparse,sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import pandas as pd
from src.data import load_snapshot
from src.analysis import fit_topics,review_examples
from src.pipeline import checksum

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--snapshot',type=Path,required=True);p.add_argument('--method',choices=['nmf','bertopic'],default='nmf');p.add_argument('--max-documents',type=int,default=5000)
 a=p.parse_args()
 if a.max_documents<10:p.error('Need at least 10 documents')
 for name in ['topics.csv','topic_labels.csv','document_map.csv','topic_manifest.json','TOPIC_REVIEW_PRIVATE.csv']:
  if (a.snapshot/name).exists():p.error('Topic artifacts already exist; use a copied snapshot for a new model version')
 _,r,_,audit=load_snapshot(str(a.snapshot));embeddings=None
 if a.method=='nmf':assign,labels=fit_topics(r,max_documents=a.max_documents)
 else:
  from sentence_transformers import SentenceTransformer
  from bertopic import BERTopic
  from umap import UMAP
  docs=r[r.text.fillna('').str.split().str.len()>=10].sort_values('review_id')
  if len(docs)>a.max_documents:docs=docs.sample(a.max_documents,random_state=42).sort_values('review_id')
  if len(docs)<20:p.error('Insufficient text for BERTopic pilot')
  encoder=SentenceTransformer('all-MiniLM-L6-v2');embeddings=encoder.encode(docs.text.tolist(),show_progress_bar=True)
  reducer=UMAP(n_neighbors=min(15,len(docs)-1),n_components=5,min_dist=0,metric='cosine',random_state=42)
  model=BERTopic(embedding_model=encoder,umap_model=reducer,calculate_probabilities=False)
  topics,_=model.fit_transform(docs.text.tolist(),embeddings)
  import numpy as np
  norms=embeddings/np.maximum(np.linalg.norm(embeddings,axis=1,keepdims=True),1e-12)
  topic_ids=sorted(set(topics));centroids=np.array([norms[np.array(topics)==i].mean(axis=0) for i in topic_ids]);centroids/=np.maximum(np.linalg.norm(centroids,axis=1,keepdims=True),1e-12)
  similarities=norms@centroids.T;own=np.array([topic_ids.index(i) for i in topics]);score=similarities[np.arange(len(topics)),own]
  other=similarities.copy();other[np.arange(len(topics)),own]=-1
  margin=score-other.max(axis=1) if len(topic_ids)>1 else np.full(len(topics),np.nan)
  assign=pd.DataFrame({'review_id':docs.review_id.values,'topic':topics,'representative_score':score,'boundary_margin':margin})
  labels=pd.DataFrame([{'topic':i,'Label':('Outlier / unassigned' if i==-1 else ' / '.join(t for t,_ in model.get_topic(i)[:4]))} for i in sorted(set(topics))])
  xy=UMAP(n_neighbors=min(15,len(docs)-1),n_components=2,metric='cosine',random_state=42).fit_transform(embeddings)
  pd.DataFrame({'review_id':docs.review_id.values,'topic':topics,'x':xy[:,0],'y':xy[:,1]}).to_csv(a.snapshot/'document_map.csv',index=False)
 if assign.empty:p.error('Insufficient documents or vocabulary; no topics written')
 assign.to_csv(a.snapshot/'topics.csv',index=False);labels.to_csv(a.snapshot/'topic_labels.csv',index=False)
 review=review_examples(assign,r)
 review.to_csv(a.snapshot/'TOPIC_REVIEW_PRIVATE.csv',index=False)
 (a.snapshot/'topic_manifest.json').write_text(json.dumps({'schema_version':2,'artifacts':{n:checksum(a.snapshot/n) for n in ['topics.csv','topic_labels.csv','document_map.csv'] if (a.snapshot/n).exists()},'review_sampling':'Up to 3 representative, 3 remaining low-margin boundary, 3 seeded random per topic; no duplicates; sparse topics have fewer roles. Scores are not calibrated probabilities.','method':a.method,'seed':42,'document_cap':a.max_documents,'assigned':len(assign),'parent_snapshot_sha256':audit['snapshot_sha256'],'semantic_validation':'PENDING','note':'Review sheet contains licensed text; do not publish without permission.'},indent=2))
 print('Wrote fixed topics. Interpretation review remains pending.')
if __name__=='__main__':main()
