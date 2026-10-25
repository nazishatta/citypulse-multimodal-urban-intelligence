import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_yelp import audit

class AuditTest(unittest.TestCase):
    def test_synthetic_join_and_repeated_reviewer(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp)
            def write(name,records):
                (root/name).write_text('\n'.join(json.dumps(x) for x in records)+'\n',encoding='utf8')
            write('yelp_academic_dataset_business.json',[
                {'business_id':'1','categories':'Restaurants, Pizza','city':'Testville','state':'TX','latitude':30,'longitude':-97},
                {'business_id':'2','categories':'Restaurants, Cafe','city':'Testville','state':'TX','latitude':31,'longitude':-97},
                {'business_id':'3','categories':'Automotive','city':'Testville','state':'TX','latitude':30,'longitude':-97}])
            write('yelp_academic_dataset_review.json',[
                {'review_id':'r1','business_id':'1','user_id':'a','date':'2024-01-01','text':'Great pizza','stars':5},
                {'review_id':'r2','business_id':'2','user_id':'a','date':'2024-01-02','text':'Nice cafe','stars':4},
                {'review_id':'r3','business_id':'1','user_id':'b','date':'2024-02-01','text':'Good','stars':4},
                {'review_id':'r4','business_id':'3','user_id':'a','date':'2024-02-01','text':'car','stars':1}])
            result=audit(root,'Testville','TX')
            m=result['metrics']
            self.assertEqual(m['selected_restaurant_businesses'],2)
            self.assertEqual(m['in_scope_reviews'],3)
            self.assertEqual(m['repeat_reviewers_2plus_businesses'],1)
            self.assertEqual(m['unique_reviewer_business_edges'],3)
            self.assertEqual(m['valid_coordinates'],2)
            self.assertTrue(any('Photo modality NOT VERIFIED' in z for z in result['flags']))
if __name__=='__main__':unittest.main()
