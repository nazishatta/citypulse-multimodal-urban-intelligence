#!/usr/bin/env python3
"""Prepare an actual licensed city snapshot. Never downloads or fabricates data."""
import argparse,json,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from src.pipeline import prepare

def main():
 p=argparse.ArgumentParser(description=__doc__)
 p.add_argument('--data-dir',required=True,type=Path);p.add_argument('--out',required=True,type=Path)
 p.add_argument('--city',required=True);p.add_argument('--state',required=True)
 p.add_argument('--photo-json',type=Path);p.add_argument('--photos-dir',type=Path);p.add_argument('--max-records',type=int)
 a=p.parse_args()
 try:r=prepare(a.data_dir,a.out,a.city,a.state,a.photo_json,a.photos_dir,a.max_records)
 except (ValueError,OSError) as e:p.exit(2,str(e)+'\n')
 print(json.dumps({'status':r['status'],'metrics':r['metrics']},indent=2))
if __name__=='__main__':main()
