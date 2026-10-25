"""Stream licensed Yelp files into an isolated, auditable SQLite snapshot."""
from __future__ import annotations
import hashlib
import json
import math
import re
import sqlite3
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterator
from PIL import Image, UnidentifiedImageError

BUSINESS = 'yelp_academic_dataset_business.json'
REVIEWS = 'yelp_academic_dataset_review.json'

def checksum(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024*1024), b''): h.update(block)
    return h.hexdigest()

def records(path: Path, stats: Counter, limit: int | None = None) -> Iterator[dict[str, Any]]:
    with path.open(encoding='utf-8-sig') as f:
        for line_no, line in enumerate(f, 1):
            if limit is not None and line_no > limit: break
            stats['lines'] += 1
            try:
                obj = json.loads(line)
                if not isinstance(obj, dict): raise ValueError('object required')
            except (ValueError, TypeError):
                stats['invalid_json'] += 1
                continue
            stats['valid_objects'] += 1
            yield obj

def identifier(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None

def coordinates(lat: Any, lon: Any) -> tuple[float | None, float | None]:
    if isinstance(lat, bool) or isinstance(lon, bool): return None, None
    try:
        a, b = float(lat), float(lon)
        if math.isfinite(a) and math.isfinite(b) and -90 <= a <= 90 and -180 <= b <= 180: return a, b
    except (TypeError, ValueError): pass
    return None, None

def date_value(value: Any) -> str | None:
    if not isinstance(value, str): return None
    try:
        d = datetime.fromisoformat(value.replace('Z', '+00:00'))
        if d.year < 2004 or d.date() > datetime.now(timezone.utc).date(): return None
        return d.date().isoformat()
    except ValueError: return None

def prepare(data_dir: Path, output: Path, city: str, state: str,
            photo_json: Path | None = None, photos_dir: Path | None = None,
            limit: int | None = None) -> dict[str, Any]:
    if limit is not None and limit < 1: raise ValueError('limit must be positive')
    if not city.strip() or not state.strip(): raise ValueError('Explicit city and state are required')
    if not all((data_dir/n).is_file() for n in (BUSINESS, REVIEWS)): raise FileNotFoundError('Business and review JSONL files are required')
    if photo_json is not None and not photo_json.is_file(): raise FileNotFoundError(photo_json)
    if output.exists(): raise FileExistsError('Choose a NEW output directory; existing snapshots are preserved')
    output.mkdir(parents=True)
    db = sqlite3.connect(output/'citypulse.sqlite')
    db.executescript('''
    CREATE TABLE businesses (business_id TEXT PRIMARY KEY,name TEXT,city TEXT,state TEXT,categories TEXT,latitude REAL,longitude REAL,stars REAL,source_review_count INTEGER);
    CREATE TABLE reviews (review_id TEXT PRIMARY KEY,business_id TEXT,user_id TEXT,date TEXT,stars REAL,text TEXT);
    CREATE TABLE photos (photo_id TEXT PRIMARY KEY,business_id TEXT,label TEXT,caption TEXT,path TEXT,width INTEGER,height INTEGER,sha256 TEXT);
    CREATE TABLE seen_business (id TEXT PRIMARY KEY);
    CREATE TABLE seen_review (id TEXT PRIMARY KEY);
    CREATE TABLE seen_photo (id TEXT PRIMARY KEY);
    ''')
    counters: dict[str, Counter] = {}
    sources = {}
    def source(name: str, path: Path):
        sources[name] = {'name':path.name,'bytes':path.stat().st_size,'sha256':checksum(path)}
    def unique(table: str, value: str) -> bool:
        return db.execute(f'INSERT OR IGNORE INTO {table} VALUES (?)',(value,)).rowcount == 1
    def rating(value: Any) -> float | None:
        if isinstance(value, bool): return None
        try:
            x=float(value)
            return x if math.isfinite(x) and 1 <= x <= 5 else None
        except (ValueError,TypeError): return None
    try:
        source('business',data_dir/BUSINESS); stats=counters['business']=Counter()
        for b in records(data_dir/BUSINESS,stats,limit):
            bid=identifier(b.get('business_id'))
            if not bid: stats['missing_id']+=1; continue
            if not unique('seen_business',bid): stats['duplicate_id_skipped']+=1; continue
            if str(b.get('city','')).strip().casefold()!=city.strip().casefold() or str(b.get('state','')).strip().casefold()!=state.strip().casefold(): continue
            cats=b.get('categories') or ''
            if isinstance(cats,list): cats=', '.join(map(str,cats))
            if not re.search(r'\bRestaurants\b',str(cats),re.I): continue
            lat,lon=coordinates(b.get('latitude'),b.get('longitude'))
            if lat is None: stats['selected_invalid_or_missing_coordinates']+=1
            else: stats['selected_valid_coordinates']+=1
            db.execute('INSERT INTO businesses VALUES (?,?,?,?,?,?,?,?,?)',(bid,str(b.get('name') or 'Unnamed'),city.strip(),state.strip(),str(cats),lat,lon,rating(b.get('stars')),b.get('review_count') if isinstance(b.get('review_count'),int) else None))
        db.commit()
        selected={r[0] for r in db.execute('SELECT business_id FROM businesses')}
        source('review',data_dir/REVIEWS); stats=counters['review']=Counter()
        for r in records(data_dir/REVIEWS,stats,limit):
            rid=identifier(r.get('review_id'))
            if not rid: stats['missing_id']+=1; continue
            if not unique('seen_review',rid): stats['duplicate_id_skipped']+=1; continue
            bid=identifier(r.get('business_id'))
            if bid is None: stats['missing_business_id']+=1
            elif not db.execute('SELECT 1 FROM seen_business WHERE id=?',(bid,)).fetchone(): stats['unmatched_business_id_in_scanned_file']+=1
            if bid not in selected: continue
            uid=identifier(r.get('user_id')); date=date_value(r.get('date')); stars=rating(r.get('stars'))
            text=r.get('text') if isinstance(r.get('text'),str) else ''
            if date is None: stats['selected_invalid_or_missing_date']+=1
            if not text.strip(): stats['selected_empty_text']+=1
            if uid is None: stats['selected_missing_user']+=1
            if stars is None: stats['selected_invalid_or_missing_rating']+=1
            db.execute('INSERT INTO reviews VALUES (?,?,?,?,?,?)',(rid,bid,uid,date,stars,text.strip()))
            if stats['lines']%10000==0: db.commit()
        db.commit()
        if photo_json:
            source('photos',photo_json);stats=counters['photo']=Counter()
            for p in records(photo_json,stats,limit):
                pid=identifier(p.get('photo_id'))
                if not pid: stats['missing_id']+=1;continue
                if not unique('seen_photo',pid):stats['duplicate_id_skipped']+=1;continue
                if p.get('business_id') not in selected:continue
                stats['selected_metadata']+=1
                # IDs are file stems only. Reject traversal and separator characters.
                if not re.fullmatch(r'[A-Za-z0-9_-]+',pid):stats['unsafe_photo_id']+=1;continue
                candidates=[photos_dir/(pid+ext) for ext in ('.jpg','.jpeg','.png','.webp')] if photos_dir else []
                path=next((f for f in candidates if f.is_file()),None)
                if path is None:stats['missing_asset']+=1;continue
                try:
                    with Image.open(path) as img:img.verify()
                    with Image.open(path) as img:img.load();width,height=img.size
                except (OSError,ValueError,UnidentifiedImageError,Image.DecompressionBombError):stats['undecodable_asset']+=1;continue
                db.execute('INSERT INTO photos VALUES (?,?,?,?,?,?,?,?)',(pid,p['business_id'],str(p.get('label') or 'unlabeled'),str(p.get('caption') or ''),path.name,width,height,checksum(path)))
        db.executescript('''CREATE INDEX review_business ON reviews(business_id);CREATE INDEX review_date ON reviews(date);CREATE INDEX review_user ON reviews(user_id);CREATE INDEX photo_business ON photos(business_id);''')
        def number(query: str) -> int:return db.execute(query).fetchone()[0]
        months=dict(db.execute("SELECT substr(date,1,7),count(*) FROM reviews WHERE date IS NOT NULL GROUP BY 1 ORDER BY 1"))
        metrics={
            'businesses':number('SELECT count(*) FROM businesses'),
            'mapped_businesses':number('SELECT count(*) FROM businesses WHERE latitude IS NOT NULL'),
            'reviews':number('SELECT count(*) FROM reviews'),
            'text_reviews':number("SELECT count(*) FROM reviews WHERE length(trim(text))>0"),
            'dated_nonempty_reviews':number("SELECT count(*) FROM reviews WHERE date IS NOT NULL AND length(trim(text))>0"),
            'observed_months':len(months), 'reviews_by_month':months,
            'repeat_reviewers':number('SELECT count(*) FROM (SELECT user_id FROM reviews WHERE user_id IS NOT NULL GROUP BY user_id HAVING count(DISTINCT business_id)>=2)'),
            'reviewer_business_edges':number('SELECT count(*) FROM (SELECT DISTINCT user_id,business_id FROM reviews WHERE user_id IS NOT NULL)'),
            'decoded_images':number('SELECT count(*) FROM photos'),
            'businesses_with_images':number('SELECT count(DISTINCT business_id) FROM photos')}
        gates={'mapped_businesses':metrics['mapped_businesses']>=200,'dated_nonempty_reviews':metrics['dated_nonempty_reviews']>=3000,'repeat_reviewers':metrics['repeat_reviewers']>=100,'decoded_images':metrics['decoded_images']>=100 and metrics['businesses_with_images']>=20,'observed_months':metrics['observed_months']>=24}
        report={'schema_version':3,'created_at':datetime.now(timezone.utc).isoformat(),'scope':{'city':city,'state':state,'mode':'FULL_SCAN' if limit is None else 'FIRST_N_BIASED','limit_per_file':limit},'source_files':sources,'parsing':{k:dict(v) for k,v in counters.items()},'metrics':metrics,'engineering_targets':gates,'status':'INCOMPLETE_SCAN' if limit else ('STRUCTURAL_TARGETS_MET_REVIEW_PENDING' if all(gates.values()) else 'REVISE_SCOPE_OR_DATA'),'permissions':'NOT_VERIFIED','deduplication':'First valid object per ID wins globally; later duplicate IDs skipped; missing IDs excluded.','warnings':['Targets are proposed engineering thresholds, not professor requirements.','Review dates are posting dates, not visits.','Images link to businesses, not individual reviews.','Identity, licenses, semantic relevance and spatial validity require review.','Invalid dates remain in corpus but are excluded from temporal selections.']}
        db.executescript('DROP TABLE seen_business;DROP TABLE seen_review;DROP TABLE seen_photo;');db.commit()
        report['snapshot_sha256']=checksum(output/'citypulse.sqlite')
        (output/'audit.json').write_text(json.dumps(report,indent=2),encoding='utf8')
        (output/'AUDIT_REPORT.md').write_text('# CityPulse data audit\n\nStatus: '+report['status']+'\n\n```json\n'+json.dumps(report,indent=2)+'\n```\n',encoding='utf8')
        return report
    except Exception:
        db.rollback()
        (output/'PREPARATION_FAILED.txt').write_text('Preparation failed. Do not use this incomplete snapshot. Choose a new output path for retry.')
        raise
    finally:db.close()
