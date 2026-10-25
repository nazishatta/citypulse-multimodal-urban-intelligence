"""Deterministic SYNTHETIC interface demonstration; never empirical Yelp evidence."""
from __future__ import annotations
import json
from pathlib import Path
from PIL import Image, ImageDraw
import random, math
from src.pipeline import prepare

def ensure_preview(root: Path) -> tuple[Path,Path]:
    raw=root/'data'/'synthetic_preview_inputs'
    snap=root/'data'/'synthetic_preview_snapshot'
    if (snap/'audit.json').exists() and (raw/'PREVIEW_VERSION').exists() and (raw/'PREVIEW_VERSION').read_text()=='v43':
        return snap,raw/'photos'
    if snap.exists():
        import shutil
        shutil.rmtree(snap)
    raw.mkdir(parents=True,exist_ok=True)
    photos=raw/'photos';photos.mkdir(exist_ok=True)
    categories=['Pizza','Cafe','Burgers','Indian','Japanese','Bakery','Mexican','Mediterranean']
    rng=random.Random(4307)
    # Three demonstrable geographic neighborhoods, plus sparse outliers.
    centers=[(39.952,-75.164),(39.963,-75.195),(39.938,-75.148)]
    businesses=[]
    for i in range(24):
        kind=categories[i%len(categories)]
        lat,lon=centers[i//8]
        businesses.append(dict(business_id=f'demo-b{i:02}',name=f'DEMO {kind} Studio {i+1}',city='Preview City',state='TS',categories=f'Restaurants, {kind}',latitude=lat+rng.uniform(-.0022,.0022),longitude=lon+rng.uniform(-.0024,.0024),stars=round(2.5+(i%7)*.34,2),review_count=250))
    themes=[
      'Friendly staff and quick service made the visit easy',
      'Long waiting time and slow checkout caused frustration',
      'Fresh delicious food and a well balanced menu impressed us',
      'High prices and small portions did not feel like good value',
      'Cozy atmosphere with comfortable seating and warm lighting',
      'Online ordering was convenient but delivery was delayed',
      'Clean interior and helpful team made the experience pleasant',
      'Cold food and rushed service were disappointing',
      'Excellent coffee and desserts make breakfast enjoyable',
      'Noisy dining room and crowded tables made conversation difficult',
    ]
    reviews=[]
    for month_index in range(48):
        year=2022+month_index//12; month=month_index%12+1
        seasonal=4 if month in (5,6,7,8) else (-2 if month in (1,2) else 0)
        trend=month_index//15
        n=max(3,9+seasonal+trend+rng.randint(-3,5))
        for k in range(n):
            i=len(reviews)
            bid=(month_index*5+k*7+rng.randint(0,23))%24
            review=rng.choice(themes[:3] if bid<8 else themes[2:7] if bid<16 else themes[5:])
            rating=max(1,min(5,round((3.6 if bid<8 else 3.0 if bid<16 else 2.5)+rng.gauss(0,1))))
            reviews.append(dict(review_id=f'demo-r{i:05}',business_id=f'demo-b{bid:02}',user_id=f'demo-u{rng.randrange(115):03}',date=f'{year}-{month:02}-{rng.randrange(1,29):02} 12:00:00',stars=rating,text=review))
    photo_rows=[]
    for i in range(24):
        pid=f'demo-p{i:03}';category=['food','drink','inside','outside'][i%4]
        photo_rows.append(dict(photo_id=pid,business_id=f'demo-b{i:02}',label=category,caption=f'Synthetic vector illustration of {category}; not a Yelp photograph'))
        img=Image.new('RGB',(360,240),(25+(i%3)*10,45+(i%4)*9,65+(i%5)*9))
        d=ImageDraw.Draw(img)
        if category=='food':
            d.ellipse((68,48,291,211),fill='#e3c7a2',outline='#95d8c6',width=8)
            for j in range(9):
                x=rng.randrange(100,260);y=rng.randrange(83,176)
                d.ellipse((x,y,x+15,y+15),fill=['#d46c43','#559a60','#f5c967'][j%3])
        elif category=='drink':
            d.rounded_rectangle((130,48,245,206),radius=18,fill='#a45f3c',outline='#a9e7de',width=8)
            d.arc((205,91,276,164),-90,90,fill='#e8c0a0',width=10)
            d.line((168,52,186,16),fill='#eeeeee',width=5)
        elif category=='inside':
            d.rectangle((48,34,306,188),fill='#263c52',outline='#a4dad4',width=5)
            d.rectangle((68,54,138,120),fill='#f0bc74')
            d.rectangle((195,54,284,120),fill='#a9cdd4')
            d.line((65,187,291,187),fill='#d9a46e',width=12)
            for x in (100,225):d.rectangle((x,144,x+50,160),fill='#c88766')
        else:
            d.polygon([(55,115),(175,30),(305,115)],fill='#b67c6d',outline='#c5ecdd')
            d.rectangle((75,112,286,211),fill='#a0bcca',outline='#d6eee7',width=5)
            d.rectangle((165,143,204,211),fill='#31465e')
            d.rectangle((93,140,133,174),fill='#f2d199')
        d.text((12,9),'SYNTHETIC / NOT YELP',fill='#fff3d9')
        img.save(photos/f'{pid}.jpg')
    for name,rows in [('yelp_academic_dataset_business.json',businesses),('yelp_academic_dataset_review.json',reviews),('photos.json',photo_rows)]:
        (raw/name).write_text(''.join(json.dumps(item)+'\n' for item in rows))
    (raw/'PREVIEW_VERSION').write_text('v43')
    prepare(raw,snap,'Preview City','TS',raw/'photos.json',photos)
    return snap,photos
