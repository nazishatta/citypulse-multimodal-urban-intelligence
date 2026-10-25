from pathlib import Path
import json,subprocess,sys
import pytest
from streamlit.testing.v1 import AppTest
from src.pipeline import prepare
from tests.fixtures import make_inputs

@pytest.fixture
def snapshot(tmp_path,monkeypatch):
 raw=tmp_path/'raw';make_inputs(raw);out=tmp_path/'snapshot';prepare(raw,out,'Fixture City','TS',raw/'photos.json',raw/'photos')
 monkeypatch.setenv('CITYPULSE_DATA_DIR',str(out));monkeypatch.setenv('CITYPULSE_ASSET_ROOT',str(raw/'photos'));return out

def test_offline_nmf_artifacts_render_and_filter(snapshot):
 project=Path(__file__).parents[1]
 subprocess.run([sys.executable,str(project/'scripts/build_topics.py'),'--snapshot',str(snapshot)],check=True,capture_output=True)
 assert (snapshot/'topics.csv').exists()
 at=AppTest.from_file(str(project/'app.py'),default_timeout=45).run()
 at.session_state['view']='Reviews & Topics';at.run();assert not at.exception
 at.multiselect(key='topic_filter').set_value([0]).run();assert not at.exception
 assert int(at.metric[0].value.replace(',',''))<360

def test_network_modes_and_neighborhood(snapshot):
 at=AppTest.from_file(str(Path(__file__).parents[1]/'app.py'),default_timeout=45).run()
 at.session_state['view']='Networks';at.run();assert not at.exception
 renderer=next(x for x in at.radio if x.label=='Network renderer')
 renderer.set_value('PyVis · drag nodes').run();assert not at.exception
 layout=next(x for x in at.radio if x.label=='Network layout')
 layout.set_value('Circular').run();assert not at.exception
 at.selectbox(key='_network_focus_widget').set_value('b0').run();assert not at.exception
 pair=at.selectbox(key='_pair_widget');pair.set_value(pair.options[1] if False else 'b4').run();assert not at.exception


def test_geojson_join_and_choropleth(snapshot):
 # Temporary supplementary polygons; not distributed as city boundaries.
 project=Path(__file__).parents[1];folder=project/'data';folder.mkdir(exist_ok=True)
 path=folder/'regions.geojson'
 assert not path.exists()
 feature={'type':'FeatureCollection','features':[{'type':'Feature','properties':{'region_id':'synthetic_area'},'geometry':{'type':'Polygon','coordinates':[[[-76,38],[-74,38],[-74,40],[-76,40],[-76,38]]]}}]}
 path.write_text(json.dumps(feature))
 try:
  at=AppTest.from_file(str(project/'app.py'),default_timeout=45).run();at.session_state['view']='Map';at.run();assert not at.exception
  assert any(x.label=='Area metric' for x in at.selectbox)
 finally:path.unlink()
