"""Fail-closed snapshot/topic validation and portable image resolution."""
from pathlib import Path
import json,re,sqlite3
import numpy as np
import pandas as pd
from src.pipeline import checksum

class IntegrityError(ValueError):
    """Prepared evidence does not match its declared lineage or schema."""

def validate_snapshot(directory: str) -> dict:
    root=Path(directory).resolve()
    if (root/'PREPARATION_FAILED.txt').exists():raise IntegrityError('Incomplete snapshot; prepare a new one')
    report=json.loads((root/'audit.json').read_text())
    expected=report.get('snapshot_sha256','')
    if not isinstance(expected,str) or not re.fullmatch(r'[a-f0-9]{64}',expected):raise IntegrityError('Invalid or missing database checksum')
    if checksum(root/'citypulse.sqlite')!=expected:raise IntegrityError('Database checksum mismatch; restore or prepare a new snapshot')
    return report

def load_snapshot(directory: str):
    root=Path(directory).resolve();report=validate_snapshot(directory)
    with sqlite3.connect((root/'citypulse.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        frames=[pd.read_sql_query('SELECT * FROM '+t,db) for t in ('businesses','reviews','photos')]
    if checksum(root/'citypulse.sqlite')!=report['snapshot_sha256']:raise IntegrityError('Database changed during loading')
    b,r,photos=frames
    for frame,key in [(b,'business_id'),(r,'review_id'),(photos,'photo_id')]:
        if frame[key].isna().any() or frame[key].duplicated().any() or frame[key].eq('').any():raise IntegrityError('Invalid unique IDs: '+key)
    if not r.business_id.isin(b.business_id).all() or not photos.business_id.isin(b.business_id).all():raise IntegrityError('Broken business foreign key')
    return (*frames,report)

def load_topics(directory: str,review_ids: set[str],snapshot_hash: str):
    root=Path(directory);names=['topics.csv','topic_labels.csv','document_map.csv','topic_manifest.json']
    if not any((root/n).exists() for n in names):return None,None,None,None
    if not all((root/n).is_file() for n in ['topics.csv','topic_labels.csv','topic_manifest.json']):raise IntegrityError('Incomplete topic artifacts')
    manifest=json.loads((root/'topic_manifest.json').read_text())
    if manifest.get('parent_snapshot_sha256')!=snapshot_hash:raise IntegrityError('Topic parent snapshot mismatch')
    artifacts=manifest.get('artifacts')
    if not isinstance(artifacts,dict):raise IntegrityError('Topic file checksums missing; rebuild artifacts with current script')
    required={'topics.csv','topic_labels.csv'}
    if (root/'document_map.csv').exists():required.add('document_map.csv')
    if not required.issubset(artifacts) or not set(artifacts).issubset(set(names)-{'topic_manifest.json'}):raise IntegrityError('Unexpected or missing topic artifact declaration')
    for name,expected in artifacts.items():
        if not (root/name).is_file() or checksum(root/name)!=expected:raise IntegrityError('Topic checksum mismatch: '+name)
    a=pd.read_csv(root/'topics.csv',dtype={'review_id':str});labels=pd.read_csv(root/'topic_labels.csv')
    if not {'review_id','topic'}.issubset(a) or not {'topic','Label'}.issubset(labels):raise IntegrityError('Invalid topic table columns')
    if a.review_id.isna().any() or a.review_id.eq('').any() or a.review_id.duplicated().any():raise IntegrityError('Topic review IDs must be nonempty and unique')
    if not set(a.review_id).issubset(review_ids):raise IntegrityError('Topic review IDs not in parent snapshot')
    for series in [a.topic,labels.topic]:
        values=pd.to_numeric(series,errors='coerce')
        if values.isna().any() or not np.isfinite(values).all() or (values%1!=0).any():raise IntegrityError('Topic IDs must be finite integers')
    a.topic=a.topic.astype(int);labels.topic=labels.topic.astype(int)
    if labels.topic.duplicated().any() or labels.Label.isna().any() or labels.Label.astype(str).str.strip().eq('').any():raise IntegrityError('Topic labels must be unique by ID and nonempty')
    if not set(a.topic).issubset(set(labels.topic)):raise IntegrityError('Topic assignment has no label')
    if manifest.get('assigned')!=len(a):raise IntegrityError('Topic assigned count mismatch')
    points=None
    if 'document_map.csv' in artifacts:
        points=pd.read_csv(root/'document_map.csv',dtype={'review_id':str})
        if not {'review_id','topic','x','y'}.issubset(points):raise IntegrityError('Invalid document map columns')
        if points.review_id.isna().any() or points.review_id.duplicated().any() or set(points.review_id)!=set(a.review_id):raise IntegrityError('Document map IDs do not match assignments')
        if not np.isfinite(points[['x','y']].apply(pd.to_numeric,errors='coerce').to_numpy()).all():raise IntegrityError('Document map coordinates must be finite')
        matched=points.merge(a[['review_id','topic']],on='review_id',suffixes=('_map','_assigned'))
        if not matched.topic_map.eq(matched.topic_assigned).all():raise IntegrityError('Document map topics disagree')
    return a,labels,points,manifest

def resolve_photo(relative: str,asset_root: str,expected_sha256: str | None=None) -> Path:
    root=Path(asset_root).resolve();ref=Path(relative)
    if ref.is_absolute():raise IntegrityError('Legacy absolute photo path; prepare a new portable snapshot')
    candidate=(root/ref).resolve()
    if not candidate.is_relative_to(root):raise IntegrityError('Photo path escapes asset root')
    if not candidate.is_file():raise FileNotFoundError('Photo unavailable under configured asset root: '+relative)
    if expected_sha256 and checksum(candidate)!=expected_sha256:raise IntegrityError('Photo checksum mismatch: '+relative)
    return candidate
