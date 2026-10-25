#!/usr/bin/env python3
"""Streaming structural feasibility audit of local Yelp Open Dataset JSONL files.

No downloads, network access, or third-party imports. A first-N limit is biased.
"""
import argparse
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import json
from pathlib import Path
import re

FILES = {'business':'yelp_academic_dataset_business.json','review':'yelp_academic_dataset_review.json','user':'yelp_academic_dataset_user.json','tip':'yelp_academic_dataset_tip.json','checkin':'yelp_academic_dataset_checkin.json'}

def json_lines(path, cap, counters):
    with path.open(encoding='utf-8-sig') as f:
        for lineno, line in enumerate(f,1):
            if cap is not None and lineno > cap: break
            counters['lines'] += 1
            try:
                obj=json.loads(line)
                if not isinstance(obj,dict): raise ValueError('record is not object')
                counters['valid_json'] += 1
                yield obj
            except (ValueError, json.JSONDecodeError):
                counters['invalid_json'] += 1

def within(thing, city, state):
    return (not city or str(thing.get('city','')).casefold().strip()==city.casefold().strip()) and (not state or str(thing.get('state','')).casefold().strip()==state.casefold().strip())

def restaurant(b):
    c=b.get('categories') or ''
    if isinstance(c,list): c=', '.join(map(str,c))
    return bool(re.search(r'\brestaurants?\b',str(c),re.I))

def audit(data_dir, city='', state='', cap=None, photo_json=None, photos_dir=None):
    data_dir=Path(data_dir)
    counts={}
    existing={k: str(data_dir/v) for k,v in FILES.items() if (data_dir/v).is_file()}
    out={'scope':{'city':city or 'ALL','state':state or 'ALL','mode':'FIRST_N (nonrandom; biased)' if cap else 'FULL_SCAN','max_records_per_file':cap},'files':{},'metrics':{},'flags':[],'warnings':[]}
    if 'business' not in existing or 'review' not in existing:
        out['flags'].append('BLOCKED: business and review JSONL both required')
    selected=set(); all_bids=set(); coords_ok=0; coords_missing=0; coord_invalid=0; selected_city_state=Counter(); businesses_dupe=0
    if 'business' in existing:
        d=Counter()
        for x in json_lines(Path(existing['business']),cap,d):
            bid=x.get('business_id')
            if bid:
                if bid in all_bids: businesses_dupe+=1
                all_bids.add(bid)
            if not within(x,city,state) or not restaurant(x): continue
            if not bid: continue
            selected.add(bid);selected_city_state[(str(x.get('city','')),str(x.get('state','')))]+=1
            lat,lon=x.get('latitude'),x.get('longitude')
            if lat is None or lon is None:coords_missing+=1
            else:
                try:
                    if -90<=float(lat)<=90 and -180<=float(lon)<=180:coords_ok+=1
                    else:coord_invalid+=1
                except (TypeError,ValueError):coord_invalid+=1
        out['files']['business']=dict(d);out['metrics'].update(selected_restaurant_businesses=len(selected),valid_coordinates=coords_ok,missing_coordinates=coords_missing,invalid_coordinates=coord_invalid,duplicate_business_ids=businesses_dupe,selected_city_state_counts={f'{c}, {s}':n for (c,s),n in selected_city_state.items()})
    reviewer_to_biz=defaultdict(set); review_ids=set(); dup_reviews=0; n_in_scope=0; nonempty=0; dated=0; parse_errors=0; year_counts=Counter(); stars=Counter(); missing_bid=0; review_linked=0
    if 'review' in existing:
        d=Counter()
        for x in json_lines(Path(existing['review']),cap,d):
            rid=x.get('review_id')
            if rid:
                if rid in review_ids:dup_reviews+=1
                review_ids.add(rid)
            bid=x.get('business_id')
            if not bid:missing_bid+=1
            if bid not in selected: continue
            n_in_scope+=1;review_linked+=1
            t=x.get('text')
            if isinstance(t,str) and t.strip():nonempty+=1
            date=x.get('date')
            if date:
                try:
                    yr=datetime.fromisoformat(str(date).replace('Z','+00:00')).year
                    dated+=1;year_counts[str(yr)]+=1
                except ValueError:parse_errors+=1
            if x.get('stars') is not None:stars[str(x.get('stars'))]+=1
            uid=x.get('user_id')
            if uid:reviewer_to_biz[str(uid)].add(str(bid))
        out['files']['review']=dict(d)
        multi=sum(len(v)>1 for v in reviewer_to_biz.values())
        edges=sum(len(v) for v in reviewer_to_biz.values())
        out['metrics'].update(in_scope_reviews=n_in_scope,nonempty_review_texts=nonempty,parseable_review_dates=dated,invalid_review_dates=parse_errors,review_year_counts=dict(sorted(year_counts.items())),review_star_counts=dict(stars),duplicate_review_ids=dup_reviews,missing_review_business_id=missing_bid,distinct_in_scope_reviewers=len(reviewer_to_biz),repeat_reviewers_2plus_businesses=multi,unique_reviewer_business_edges=edges)
        if cap:out['warnings'].append('First-N scanning review JSONL is not a representative sample and underestimates joins, network and time support.')
    for typ in ['user','tip','checkin']:
        if typ in existing:
            d=Counter()
            for obj in json_lines(Path(existing[typ]),cap,d):
                if typ in ('tip','checkin') and obj.get('business_id') in selected:d['in_scope_records']+=1
            out['files'][typ]=dict(d)
        else:out['warnings'].append(f'{typ} data file not supplied (optional for basic reviewer-business graph).')
    if photo_json:
        photo_json=Path(photo_json)
        if not photo_json.is_file():out['flags'].append(f'Photo metadata path missing: {photo_json}')
        else:
            d=Counter(); matched=0; actual=0; perbiz=set(); labels=Counter(); inspected=0
            for obj in json_lines(photo_json,cap,d):
                if obj.get('business_id') not in selected:continue
                matched+=1;perbiz.add(obj.get('business_id'));labels[str(obj.get('label') or 'unlabeled')]+=1
                photo_id=obj.get('photo_id')
                if photos_dir and photo_id:
                    candidate=Path(photos_dir)/(str(photo_id)+'.jpg')
                    if candidate.is_file() and candidate.stat().st_size>0:actual+=1
                inspected+=1
            out['files']['photo']=dict(d)
            out['metrics'].update(in_scope_photo_metadata=matched,in_scope_photo_businesses=len(perbiz),photo_labels=dict(labels),photo_image_files_present=actual)
            if not photos_dir:out['flags'].append('Photo metadata present; actual image directory NOT supplied or verified.')
            elif actual == 0:out['flags'].append('No actual matching nonempty .jpg image files found for in-scope photo metadata.')
            else:out['warnings'].append('Photo check confirms nonempty JPG files only; image decoding and display rights still require review.')
    else:out['flags'].append('Photo modality NOT VERIFIED: separate metadata and actual image files not supplied.')
    if not selected:out['flags'].append('No matching restaurant businesses. Verify city/state spelling, categories, or file completeness.')
    if n_in_scope<3000:out['warnings'].append('Below suggested 3,000 in-scope reviews; text/time support may be sparse.')
    if len(selected)<200:out['warnings'].append('Below suggested 200 in-scope restaurants.')
    if sum(len(v)>1 for v in reviewer_to_biz.values())<100:out['warnings'].append('Below suggested 100 reviewers spanning multiple restaurants; projected network may be weak.')
    if cap:out['warnings'].append('Use uncapped full scan before GO/NO-GO; each file is individually truncated from its start.')
    out['flags'].append('License/terms and real image decodability require manual review; automated scan cannot approve public redistribution.')
    return out

def report_text(d):
    m=d['metrics'];s=['# CityPulse — Actual-data feasibility audit','',f"**Mode:** {d['scope']['mode']} | **City:** {d['scope']['city']} | **State:** {d['scope']['state']}",'', '## Observed metrics','']
    for k,v in m.items():s.append(f'- **{k}:** `{json.dumps(v,ensure_ascii=False)}`')
    s += ['','## File parsing','']
    for k,v in d['files'].items():s.append(f'- **{k}:** `{json.dumps(v)}`')
    s += ['','## Blocks / unknowns','']+[f'- {x}' for x in d['flags']]
    s += ['','## Cautions','']+[f'- {x}' for x in d['warnings']]
    s += ['','## Decision','', '**NOT YET VERIFIED.** The numerical scans cannot establish photo permissions, visual design correctness, topic quality, GIS CRS correctness, or deployment. Complete the human scorecard before GO.','']
    return '\n'.join(s)

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data-dir',required=True,type=Path);p.add_argument('--city',default='');p.add_argument('--state',default='');p.add_argument('--max-records',type=int);p.add_argument('--photo-json',type=Path);p.add_argument('--photos-dir',type=Path);p.add_argument('--out',type=Path,default=Path('audit_results'))
    a=p.parse_args()
    if a.max_records is not None and a.max_records<1:p.error('--max-records must be positive')
    result=audit(a.data_dir,a.city,a.state,a.max_records,a.photo_json,a.photos_dir)
    a.out.mkdir(parents=True,exist_ok=True)
    (a.out/'summary.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
    (a.out/'AUDIT_REPORT.md').write_text(report_text(result),encoding='utf8')
    print('Wrote',a.out/'summary.json','and',a.out/'AUDIT_REPORT.md')
    print('Restaurant businesses:',result['metrics'].get('selected_restaurant_businesses','unknown'))
    print('In-scope reviews:',result['metrics'].get('in_scope_reviews','unknown'))
    print('Repeat reviewers:',result['metrics'].get('repeat_reviewers_2plus_businesses','unknown'))
    print('Photo status:','SEE FLAGS (not approved)')
if __name__=='__main__':main()
