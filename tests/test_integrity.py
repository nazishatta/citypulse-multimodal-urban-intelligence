"""Negative evidence-integrity tests; every input is synthetic."""
import json,shutil,sqlite3,subprocess,sys
from pathlib import Path
import pandas as pd
import pytest
from src.pipeline import prepare,checksum
from src.data import load_snapshot,load_topics,resolve_photo,IntegrityError
from src.analysis import review_examples
from tests.fixtures import make_inputs

@pytest.fixture
def prepared(tmp_path):
 raw=tmp_path/'raw';make_inputs(raw);out=tmp_path/'snapshot'
 prepare(raw,out,'Fixture City','TS',raw/'photos.json',raw/'photos')
 return raw,out

def test_modified_database_rejected(prepared):
 _,out=prepared
 with sqlite3.connect(out/'citypulse.sqlite') as db:db.execute('UPDATE reviews SET stars=5')
 with pytest.raises(IntegrityError,match='checksum'):load_snapshot(str(out))

def test_missing_checksum_rejected(prepared):
 _,out=prepared;p=out/'audit.json';a=json.loads(p.read_text());a.pop('snapshot_sha256');p.write_text(json.dumps(a))
 with pytest.raises(IntegrityError,match='checksum'):load_snapshot(str(out))

def test_photo_relocation_and_tampering(prepared,tmp_path):
 raw,out=prepared;_,r,p,a=load_snapshot(str(out));row=p.iloc[0]
 assert not Path(row.path).is_absolute()
 moved=tmp_path/'moved';shutil.move(raw/'photos',moved)
 assert resolve_photo(row.path,str(moved),row.sha256).is_file()
 (moved/row.path).write_bytes(b'corrupt')
 with pytest.raises(IntegrityError,match='checksum'):resolve_photo(row.path,str(moved),row.sha256)

@pytest.mark.parametrize('reference',['../outside.jpg','/tmp/absolute.jpg'])
def test_unsafe_photo_reference_rejected(tmp_path,reference):
 with pytest.raises(IntegrityError):resolve_photo(reference,str(tmp_path))

def topic_files(out,mutation=None):
 b,r,p,a=load_snapshot(str(out));df=pd.DataFrame({'review_id':r.review_id.head(3),'topic':[0,0,0]})
 if mutation:df=mutation(df)
 df.to_csv(out/'topics.csv',index=False);pd.DataFrame({'topic':[0],'Label':['Provisional']}).to_csv(out/'topic_labels.csv',index=False)
 manifest={'parent_snapshot_sha256':a['snapshot_sha256'],'assigned':len(df),'artifacts':{n:checksum(out/n) for n in ['topics.csv','topic_labels.csv']}}
 (out/'topic_manifest.json').write_text(json.dumps(manifest));return r,a

@pytest.mark.parametrize('case',['duplicate','unknown','fractional','unlabeled','stale','tampered','partial','count'])
def test_bad_topic_artifacts_rejected(prepared,case):
 _,out=prepared
 def mutate(df):
  if case=='duplicate':df.loc[1,'review_id']=df.loc[0,'review_id']
  if case=='unknown':df.loc[0,'review_id']='missing'
  if case=='fractional':df['topic']=.5
  if case=='unlabeled':df['topic']=42
  return df
 r,a=topic_files(out,mutate)
 p=out/'topic_manifest.json';m=json.loads(p.read_text())
 if case=='stale':m['parent_snapshot_sha256']='0'*64
 if case=='count':m['assigned']=999
 p.write_text(json.dumps(m))
 if case=='tampered':(out/'topics.csv').write_text('changed')
 if case=='partial':(out/'topic_labels.csv').unlink()
 with pytest.raises(IntegrityError):load_topics(str(out),set(r.review_id),a['snapshot_sha256'])

def test_valid_and_absent_topics(prepared):
 _,out=prepared;_,r,_,a=load_snapshot(str(out))
 assert load_topics(str(out),set(r.review_id),a['snapshot_sha256'])==(None,None,None,None)
 r,a=topic_files(out);assert len(load_topics(str(out),set(r.review_id),a['snapshot_sha256'])[0])==3

def test_examples_disjoint_diverse_reproducible():
 a=pd.DataFrame({'review_id':[str(i) for i in range(20)],'topic':[0]*20,'representative_score':list(range(20)),'boundary_margin':list(range(20))})
 r=pd.DataFrame({'review_id':a.review_id,'text':['synthetic']*20})
 x=review_examples(a,r);pd.testing.assert_frame_equal(x,review_examples(a,r))
 assert not x.review_id.duplicated().any()
 assert x.groupby('sample_role').size().to_dict()=={'boundary':3,'random':3,'representative':3}
 assert set(x[x.sample_role=='representative'].review_id)=={'17','18','19'}
 assert set(x[x.sample_role=='boundary'].review_id)=={'0','1','2'}
