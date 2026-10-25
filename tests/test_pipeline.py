from pathlib import Path
import json,sqlite3
import pytest
from src.pipeline import prepare,coordinates,date_value,checksum
from tests.fixtures import make_inputs,write_json

@pytest.fixture
def raw(tmp_path):
 p=tmp_path/'raw';make_inputs(p);return p

def test_baseline_exact_counts_and_decoded_images(raw,tmp_path):
 report=prepare(raw,tmp_path/'out','fixture city','TS',raw/'photos.json',raw/'photos')
 assert report['metrics']['businesses']==12
 assert report['metrics']['reviews']==360
 assert report['metrics']['decoded_images']==12
 assert report['metrics']['observed_months']==36
 assert report['metrics']['repeat_reviewers']==20
 assert report['permissions']=='NOT_VERIFIED'
 assert report['status']=='REVISE_SCOPE_OR_DATA'
 assert checksum(tmp_path/'out/citypulse.sqlite')==report['snapshot_sha256']

def test_duplicate_business_and_review_ids_do_not_inflate_counts(raw,tmp_path):
 for name in ['business','review']:
  p=raw/f'yelp_academic_dataset_{name}.json'
  p.write_text(p.read_text()+p.read_text().splitlines()[0]+'\n')
 report=prepare(raw,tmp_path/'out','Fixture City','TS')
 assert report['metrics']['businesses']==12
 assert report['metrics']['reviews']==360
 assert report['parsing']['review']['duplicate_id_skipped']==1
 assert report['parsing']['business']['duplicate_id_skipped']==1

def test_bad_image_bytes_not_counted_as_image(raw,tmp_path):
 (raw/'photos/p0.jpg').write_bytes(b'not an image')
 report=prepare(raw,tmp_path/'out','Fixture City','TS',raw/'photos.json',raw/'photos')
 assert report['metrics']['decoded_images']==11
 assert report['parsing']['photo']['undecodable_asset']==1

def test_bad_coordinates_are_excluded_from_mapping_not_corpus(raw,tmp_path):
 p=raw/'yelp_academic_dataset_business.json';rows=[json.loads(s) for s in p.read_text().splitlines()]
 rows[0]['latitude']=float('nan');rows[1]['latitude']=True;rows[2]['longitude']=300
 write_json(p,rows)
 report=prepare(raw,tmp_path/'out','Fixture City','TS')
 assert report['metrics']['mapped_businesses']==9
 assert report['metrics']['businesses']==12

def test_bad_dates_text_and_missing_ids(raw,tmp_path):
 p=raw/'yelp_academic_dataset_review.json';rows=[json.loads(s) for s in p.read_text().splitlines()]
 rows[0]['date']='2099-01-01';rows[1]['date']='bad';rows[2]['text']=' ';rows[3]['review_id']=None
 write_json(p,rows)
 report=prepare(raw,tmp_path/'out','Fixture City','TS')
 assert report['metrics']['reviews']==359
 assert report['metrics']['text_reviews']==358
 assert report['metrics']['dated_nonempty_reviews']==356
 assert report['parsing']['review']['missing_id']==1

def test_first_n_never_passes_full_audit(raw,tmp_path):
 report=prepare(raw,tmp_path/'out','Fixture City','TS',limit=3)
 assert report['status']=='INCOMPLETE_SCAN'

def test_existing_snapshot_never_overwritten(raw,tmp_path):
 out=tmp_path/'out';prepare(raw,out,'Fixture City','TS')
 with pytest.raises(FileExistsError):prepare(raw,out,'Fixture City','TS')

def test_missing_inputs_fail_before_snapshot_creation(tmp_path):
 with pytest.raises(FileNotFoundError):prepare(tmp_path,tmp_path/'out','City','TS')
 assert not (tmp_path/'out').exists()

def test_nonobject_json_and_malformed_lines_are_reported(raw,tmp_path):
 p=raw/'yelp_academic_dataset_review.json';p.write_text(p.read_text()+'[]\n{bad\n')
 report=prepare(raw,tmp_path/'out','Fixture City','TS')
 assert report['parsing']['review']['invalid_json']==2
 assert report['metrics']['reviews']==360

def test_photo_path_traversal_rejected(raw,tmp_path):
 write_json(raw/'photos.json',[dict(photo_id='../secret',business_id='b0')])
 report=prepare(raw,tmp_path/'out','Fixture City','TS',raw/'photos.json',raw/'photos')
 assert report['metrics']['decoded_images']==0
 assert report['parsing']['photo']['unsafe_photo_id']==1
