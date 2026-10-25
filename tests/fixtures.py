"""SYNTHETIC test data. Not Yelp observations, not empirical project findings."""
import json
from pathlib import Path
from PIL import Image

def write_json(path,rows):path.write_text('\n'.join(json.dumps(x) for x in rows)+'\n')
def make_inputs(root: Path):
 root.mkdir(parents=True,exist_ok=True);photos=root/'photos';photos.mkdir(exist_ok=True)
 businesses=[dict(business_id=f'b{i}',name=f'SYNTHETIC Restaurant {i}',city='Fixture City',state='TS',categories='Restaurants, Pizza' if i%2==0 else 'Restaurants, Cafe',latitude=39+i*.001,longitude=-75-i*.001,stars=4,review_count=20) for i in range(12)]
 texts=['friendly service delicious pizza tomato cheese dining experience excellent staff family dinner restaurant','coffee breakfast pastries warm bakery morning sandwiches espresso cafe pleasant local dining','outdoor patio parking quiet table atmosphere seating restaurant dinner reservation comfortable location','slow service cold meal waiting staff order incorrect disappointing restaurant refund experience']
 reviews=[dict(review_id=f'r{i:04}',business_id=f'b{i%12}',user_id=f'u{i%20}',date=f'{2022+i//120}-{1+(i//10)%12:02}-15 12:00:00',stars=1+i%5,text=texts[i%4]+' '+str(i)) for i in range(360)]
 images=[dict(photo_id=f'p{i}',business_id=f'b{i}',label='food' if i%2==0 else 'inside',caption='SYNTHETIC colored fixture') for i in range(12)]
 for i in range(12):Image.new('RGB',(64,48),(i*20,40,150)).save(photos/f'p{i}.jpg')
 write_json(root/'yelp_academic_dataset_business.json',businesses);write_json(root/'yelp_academic_dataset_review.json',reviews);write_json(root/'photos.json',images)
 return businesses,reviews,images
