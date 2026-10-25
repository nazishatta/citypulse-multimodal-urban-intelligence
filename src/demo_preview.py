"""Deterministic SYNTHETIC interface demonstration; never empirical Yelp evidence."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageDraw
from src.pipeline import prepare

def ensure_preview(root: Path) -> tuple[Path,Path]:
    raw=root/'data'/'synthetic_preview_inputs'
    snap=root/'data'/'synthetic_preview_snapshot'
    if (snap/'audit.json').exists():
        return snap,raw/'photos'
    raw.mkdir(parents=True,exist_ok=True)
    photos=raw/'photos';photos.mkdir(exist_ok=True)
    categories=['Pizza','Cafe','Burgers','Indian','Japanese','Bakery','Mexican','Mediterranean']
    businesses=[]
    for i in range(24):
        kind=categories[i%len(categories)]
        businesses.append(dict(business_id=f'demo-b{i:02}',name=f'DEMO {kind} Studio {i+1}',city='Preview City',state='TS',categories=f'Restaurants, {kind}',latitude=39.93+(i//6)*.018+(i%3)*.003,longitude=-75.19+(i%6)*.02,stars=round(2.8+(i%9)*.22,2),review_count=200))
    words=[
      'The service was quick and friendly with a pleasant welcome and helpful team',
      'The menu had delicious food and excellent flavors although the waiting time varied',
      'The atmosphere felt comfortable and the lighting and seating suited our group',
      'The value and price seemed fair and the portion sizes were satisfying',
      'The takeaway ordering process was simple but delivery took longer than expected',
      'The coffee and dessert were fresh and the morning visit was relaxing',
    ]
    reviews=[]
    for i in range(720):
        month=1+(i//15)%12
        year=2022+(i//180)
        reviews.append(dict(review_id=f'demo-r{i:05}',business_id=f'demo-b{(i*7+i//11)%24:02}',user_id=f'demo-u{i%93:03}',date=f'{year}-{month:02}-15 12:00:00',stars=1+(i*3+i//13)%5,text=words[i%len(words)]+' '+words[(i//7)%len(words)]))
    photo_rows=[]
    for i in range(24):
        pid=f'demo-p{i:03}'
        photo_rows.append(dict(photo_id=pid,business_id=f'demo-b{i:02}',label=['food','drink','inside','outside'][i%4],caption='Generated abstract demonstration illustration — NOT a Yelp photograph'))
        img=Image.new('RGB',(360,240),(22+i*4,40+(i*7)%75,58+(i*11)%96))
        d=ImageDraw.Draw(img)
        d.rounded_rectangle((50,45,310,194),radius=35,outline=(136,215,196),width=7)
        d.ellipse((110+(i%5)*7,74,250,180),outline=(231,170,109),width=8)
        d.text((22,15),'SYNTHETIC PREVIEW',fill=(245,245,245))
        img.save(photos/f'{pid}.jpg')
    for name,rows in [('yelp_academic_dataset_business.json',businesses),('yelp_academic_dataset_review.json',reviews),('photos.json',photo_rows)]:
        (raw/name).write_text(''.join(json.dumps(item)+'\n' for item in rows))
    prepare(raw,snap,'Preview City','TS',raw/'photos.json',photos)
    return snap,photos
